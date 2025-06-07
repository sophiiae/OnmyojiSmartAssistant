import copy
from functools import cached_property
from datetime import datetime, timedelta
import operator
from threading import Lock
import time
import inflection

from module.base.logger import logger
from module.base.exception import RequestHumanTakeover, ScriptError
from module.control.config.config_model import ConfigModel
from module.control.config.config_state import ConfigState

from module.control.config.function import Function

from module.control.config.scheduler import TaskScheduler
from module.control.config.utils import dict_to_kv, nearest_future

class Config(ConfigState):
    """
    Configuration management class that handles task scheduling and configuration updates.

    This class extends ConfigState and provides methods for:
    - Task scheduling and execution
    - Configuration file management
    - Thread-safe configuration updates
    """

    def __init__(self, config_name: str, task=None) -> None:
        """
        Initialize the configuration.

        Args:
            config_name (str): Name of the configuration file
            task: Optional task parameter for initialization
        """
        super().__init__(config_name)  # Initialize ConfigState parent class
        self.model = ConfigModel(config_name=config_name)

    @cached_property
    def lock_config(self) -> Lock:
        """
        Thread-safe lock for configuration operations.

        Returns:
            Lock: Threading lock for configuration synchronization
        """
        return Lock()

    def reload(self):
        """
        Reload configuration from file.

        This method recreates the configuration model from the stored file,
        effectively discarding any unsaved changes.
        """
        try:
            self.model = ConfigModel(config_name=self.config_name)
            logger.info(
                f"Configuration {self.config_name} reloaded successfully")
        except Exception as e:
            logger.error(
                f"Failed to reload configuration {self.config_name}: {e}")
            raise

    def save(self):
        """
        Save current configuration to file.

        This method persists the current configuration state to the JSON file.
        """
        try:
            self.model.write_json(self.config_name)
            logger.info(f"Configuration {self.config_name} saved successfully")
        except Exception as e:
            logger.error(
                f"Failed to save configuration {self.config_name}: {e}")
            raise

    def update_scheduler(self) -> None:
        """
        Update the task scheduler by categorizing tasks into pending, waiting, and error lists.

        This method:
        1. Iterates through all configured tasks
        2. Categorizes them based on their schedule status
        3. Applies scheduling rules to pending tasks
        4. Sorts waiting tasks by execution time
        """
        pending_task = []
        waiting_task = []
        error = []
        now = datetime.now()

        try:
            for key, value in self.model.model_dump().items():
                func = Function(key, value)

                if not func.enable:
                    continue

                if not isinstance(func.next_run, datetime):
                    logger.warning(
                        f"Task {func.name} has invalid next_run time: {func.next_run}")
                    error.append(func)
                elif func.next_run < now:
                    pending_task.append(func)
                else:
                    waiting_task.append(func)

            # Apply scheduling rules to pending tasks
            if pending_task:
                pending_task = TaskScheduler.schedule(
                    rule=self.model.script.optimization.schedule_rule,
                    pending=pending_task
                )

            # Sort waiting tasks by execution time
            if waiting_task:
                waiting_task = sorted(
                    waiting_task, key=operator.attrgetter("next_run"))

            # Add error tasks to the beginning of pending tasks for immediate attention
            if error:
                pending_task = error + pending_task

            self.pending_task = pending_task
            self.waiting_task = waiting_task

            logger.info(f"Scheduler updated - Pending: {len(pending_task)}, "
                        f"Waiting: {len(waiting_task)}, Errors: {len(error)}")

        except Exception as e:
            logger.error(f"Failed to update scheduler: {e}")
            raise

    def get_next(self) -> Function:
        """
        Get the next task to execute.

        Returns:
            Function: The next task to be executed

        Raises:
            RequestHumanTakeover: When no tasks are available for execution
        """
        self.update_scheduler()

        # Return the first pending task if available
        if self.pending_task:
            logger.info(
                f"Pending tasks: {[f.name for f in self.pending_task]}")
            task = self.pending_task[0]
            self.task = task
            return task

        # If no pending tasks, return the next waiting task
        if self.waiting_task:
            logger.info("No task pending, returning next waiting task")
            task = copy.deepcopy(self.waiting_task[0])
            logger.info(f"Next waiting task: {task.name} at {task.next_run}")
            return task
        else:
            logger.critical("No task waiting or pending")
            logger.critical("Please enable at least one task")
            raise RequestHumanTakeover()

    def get_schedule_data(self) -> dict[str, dict]:
        """
        Get current scheduler status data.

        Note: You must call update_scheduler() before this method to get current information.

        Returns:
            dict: Dictionary containing running, pending, and waiting task information
        """
        running = {}
        if self.task is not None and self.task.next_run < datetime.now():
            running = {
                "name": self.task.name,
                "next_run": str(self.task.next_run)
            }

        # Get pending tasks (excluding the currently running one)
        pending = []
        for p in self.pending_task[1:]:
            item = {"name": p.name, "next_run": str(p.next_run)}
            pending.append(item)

        # Get waiting tasks
        waiting = []
        for w in self.waiting_task:
            item = {"name": w.name, "next_run": str(w.next_run)}
            waiting.append(item)

        data = {"running": running, "pending": pending, "waiting": waiting}
        return data

    def task_call(self, task: str | None = None, force_call: bool = True) -> bool:
        """
        Schedule a task for immediate execution.

        Args:
            task (str): Task name in camelCase format
            force_call (bool): Execute even if task is disabled

        Returns:
            bool: True if task was scheduled, False if skipped

        Raises:
            ScriptError: If the specified task doesn't exist
        """
        if not task:
            logger.warning("No task specified for task_call")
            return False

        task = inflection.underscore(task)

        # Validate task exists
        if self.model.deep_get(self.model, keys=f'{task}.scheduler.next_run') is None:
            raise ScriptError()

        task_enable = self.model.deep_get(
            self.model, keys=f'{task}.scheduler.enable')

        if force_call or task_enable:
            logger.info(f"Task call: {task}")
            next_run = datetime.now().replace(microsecond=0)

            success = self.model.deep_set(
                self.model,
                keys=f'{task}.scheduler.next_run',
                value=next_run
            )

            if success:
                self.save()
                return True
            else:
                logger.error(f"Failed to set next_run for task: {task}")
                return False
        else:
            logger.info(
                f"Task call: {task} (skipped because disabled by user)")
            return False

    def task_delay(self, task: str, start_time: datetime | None = None,
                   success: bool | None = None, server: bool = True, target_time: datetime | None = None) -> None:
        """
        Set the next execution time for a task.

        Args:
            task (str): Task name in camelCase format
            start_time (datetime, optional): Base time for interval calculation. Defaults to now.
            success (bool, optional): Whether to use success or failure interval
            server (bool): Legacy parameter, kept for compatibility
            target_time (datetime, optional): Specific target time to set
        """
        try:
            # Reload configuration to ensure we have the latest state
            self.reload()

            # Task preprocessing
            if not task:
                if self.task is None:
                    logger.warning("No task specified and no current task")
                    return
                task = self.task.name

            task = inflection.underscore(task)

            # Validate task exists
            task_object = getattr(self.model, task, None)
            if not task_object:
                logger.warning(f'No task named {task}')
                return

            scheduler = getattr(task_object, 'scheduler', None)
            if not scheduler:
                logger.warning(f'No scheduler in {task}')
                return

            # Set base time for calculations
            if not start_time:
                start_time = datetime.now().replace(microsecond=0)

            # Calculate next run time based on provided parameters
            run_times = []

            # Add interval-based time if success parameter is provided
            if success is not None:
                interval = (
                    scheduler.success_interval
                    if success
                    else scheduler.failure_interval
                )

                # Parse interval string format "DD HH:MM:SS"
                if isinstance(interval, str):
                    try:
                        parts = interval.split(":")
                        if len(parts) == 3:
                            # Format: "DD HH:MM:SS"
                            d, h, m, s = interval.split(":")
                            interval = timedelta(
                                days=int(d),
                                hours=int(h),
                                minutes=int(m),
                                seconds=int(s)
                            )
                        elif len(parts) == 4:
                            # Alternative format: "D:H:M:S"
                            d, h, m, s = parts
                            interval = timedelta(
                                days=int(d),
                                hours=int(h),
                                minutes=int(m),
                                seconds=int(s)
                            )
                        else:
                            logger.error(
                                f"Invalid interval format: {interval}")
                            return
                    except (ValueError, AttributeError) as e:
                        logger.error(
                            f"Failed to parse interval {interval}: {e}")
                        return

                run_times.append(start_time + interval)

            # Add target time if provided
            if target_time is not None:
                target_list = [target_time] if not isinstance(
                    target_time, list) else target_time
                calculated_target = nearest_future(target_list)
                run_times.append(calculated_target)

            # Use the earliest calculated time, or default to start_time
            if run_times:
                next_run = min(run_times).replace(microsecond=0)
            else:
                logger.warning(
                    f"No valid run time calculated for task {task}, using current time")
                next_run = start_time

            # Log the delay operation
            kv = dict_to_kv(
                {
                    "success": success,
                    "target": target_time,
                    "start_time": start_time,
                },
                allow_none=False,
            )
            logger.info(f"Delay task [{task}] to {next_run} ({kv})")

            # Thread-safe configuration update
            with self.lock_config:
                try:
                    # Set the next run time
                    success_set = self.model.deep_set(
                        self.model,
                        keys=f'{task}.scheduler.next_run',
                        value=next_run
                    )

                    if success_set:
                        self.save()
                        logger.info(
                            f"Successfully set {task}.scheduler.next_run: {next_run}")
                    else:
                        logger.error(
                            f"Failed to set next_run for task: {task}")

                except Exception as e:
                    logger.error(
                        f"Error setting next_run for task {task}: {e}")
                    raise

        except Exception as e:
            logger.error(f"Failed to delay task {task}: {e}")
            raise


if __name__ == '__main__':
    # Test configuration
    config = Config(config_name='osa')
    config.update_scheduler()
    print(f"Waiting tasks: {[task.name for task in config.waiting_task]}")
    print(f"Pending tasks: {[task.name for task in config.pending_task]}")
