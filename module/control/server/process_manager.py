import time
from datetime import datetime
from typing import List, Optional, Dict, Any
from threading import Thread, Event, Lock
from queue import Queue, Empty
from enum import Enum
from module.control.config.config_model import ConfigModel
from module.base.logger import logger

class ProcessState(Enum):
    """Process manager states."""
    STOPPED = "stopped"
    STARTING = "starting"
    RUNNING = "running"
    STOPPING = "stopping"
    ERROR = "error"


class TaskInfo:
    """Information about a scheduled task."""

    def __init__(self, name: str, task_object: Any, next_run: datetime):
        """
        Initialize task information.

        Args:
            name (str): Task name
            task_object: Task configuration object
            next_run (datetime): Next scheduled execution time
        """
        self.name = name
        self.task_object = task_object
        self.next_run = next_run
        self.last_run: Optional[datetime] = None
        self.run_count = 0
        self.error_count = 0

    def __repr__(self) -> str:
        return f"TaskInfo(name={self.name}, next_run={self.next_run})"


class ProcessManager:
    """
    Process manager for handling task scheduling and execution.

    This class provides:
    - Task queue management
    - Process lifecycle control
    - Thread-safe operations
    - Error handling and logging
    """

    def __init__(self, config: ConfigModel) -> None:
        """
        Initialize the process manager.

        Args:
            config (ConfigModel): Configuration model containing task definitions
        """
        self.config: ConfigModel = config
        self.state: ProcessState = ProcessState.STOPPED

        # Task management
        self.task_queue: Queue[TaskInfo] = Queue()
        self.active_tasks: Dict[str, TaskInfo] = {}

        # Threading
        self.worker_thread: Optional[Thread] = None
        self.stop_event: Event = Event()
        self.state_lock: Lock = Lock()

        # Statistics
        self.total_tasks_processed = 0
        self.start_time: Optional[datetime] = None

        logger.info("ProcessManager initialized")

    def get_state(self) -> ProcessState:
        """
        Get current process manager state.

        Returns:
            ProcessState: Current state
        """
        with self.state_lock:
            return self.state

    def _set_state(self, new_state: ProcessState) -> None:
        """
        Set process manager state (thread-safe).

        Args:
            new_state (ProcessState): New state to set
        """
        with self.state_lock:
            old_state = self.state
            self.state = new_state
            logger.info(
                f"State changed: {old_state.value} -> {new_state.value}")

    def start_processing(self) -> bool:
        """
        Start the process manager and begin task processing.

        Returns:
            bool: True if started successfully, False otherwise
        """
        try:
            if self.get_state() != ProcessState.STOPPED:
                logger.warning(
                    f"Cannot start - current state: {self.get_state().value}")
                return False

            self._set_state(ProcessState.STARTING)

            # Load tasks from configuration
            self._load_tasks()

            # Start worker thread
            self.stop_event.clear()
            self.worker_thread = Thread(target=self._worker_loop, daemon=True)
            self.worker_thread.start()

            self.start_time = datetime.now()
            self._set_state(ProcessState.RUNNING)

            logger.info("ProcessManager started successfully")
            return True

        except Exception as e:
            logger.error(f"Failed to start ProcessManager: {e}")
            self._set_state(ProcessState.ERROR)
            return False

    def stop_processing(self) -> bool:
        """
        Stop the process manager and clean up resources.

        Returns:
            bool: True if stopped successfully, False otherwise
        """
        try:
            current_state = self.get_state()
            if current_state in [ProcessState.STOPPED, ProcessState.STOPPING]:
                logger.info(
                    f"Already stopped or stopping - state: {current_state.value}")
                return True

            self._set_state(ProcessState.STOPPING)

            # Signal worker thread to stop
            self.stop_event.set()

            # Wait for worker thread to finish
            if self.worker_thread and self.worker_thread.is_alive():
                self.worker_thread.join(timeout=10.0)
                if self.worker_thread.is_alive():
                    logger.warning("Worker thread did not stop within timeout")
                    return False

            # Clear task queue
            self._clear_task_queue()

            self._set_state(ProcessState.STOPPED)

            uptime = datetime.now() - self.start_time if self.start_time else None
            logger.info(
                f"ProcessManager stopped. Uptime: {uptime}, Tasks processed: {self.total_tasks_processed}")

            return True

        except Exception as e:
            logger.error(f"Error stopping ProcessManager: {e}")
            self._set_state(ProcessState.ERROR)
            return False

    def _load_tasks(self) -> None:
        """
        Load enabled tasks from configuration into the task queue.
        """
        try:
            self.active_tasks.clear()

            # Get configuration data
            model_data = self.config.model_dump()
            loaded_count = 0

            for key, value in model_data.items():
                # Skip non-task configuration items
                if key == "script" or isinstance(value, str):
                    continue

                try:
                    # Get task object from configuration
                    task_object = getattr(self.config, key, None)
                    if not task_object:
                        continue

                    # Check if task has scheduler
                    scheduler = getattr(task_object, "scheduler", None)
                    if not scheduler:
                        logger.debug(f"Task {key} has no scheduler, skipping")
                        continue

                    # Check if task is enabled
                    is_enabled = getattr(scheduler, "enable", False)
                    if not is_enabled:
                        logger.debug(f"Task {key} is disabled, skipping")
                        continue

                    # Get next run time
                    next_run_str = getattr(scheduler, "next_run", None)
                    if not next_run_str:
                        logger.warning(
                            f"Task {key} has no next_run time, skipping")
                        continue

                    # Parse next run time
                    if isinstance(next_run_str, str):
                        try:
                            next_run = datetime.strptime(
                                next_run_str, "%Y-%m-%d %H:%M:%S")
                        except ValueError as e:
                            logger.error(
                                f"Invalid next_run format for task {key}: {next_run_str} - {e}")
                            continue
                    elif isinstance(next_run_str, datetime):
                        next_run = next_run_str
                    else:
                        logger.error(
                            f"Invalid next_run type for task {key}: {type(next_run_str)}")
                        continue

                    # Create task info and add to active tasks
                    task_info = TaskInfo(key, task_object, next_run)
                    self.active_tasks[key] = task_info
                    loaded_count += 1

                    logger.debug(f"Loaded task: {task_info}")

                except Exception as e:
                    logger.error(f"Error loading task {key}: {e}")
                    continue

            logger.info(f"Loaded {loaded_count} enabled tasks")

        except Exception as e:
            logger.error(f"Failed to load tasks: {e}")
            raise

    def _worker_loop(self) -> None:
        """
        Main worker loop for processing tasks.
        """
        logger.info("Worker thread started")

        try:
            while not self.stop_event.is_set():
                try:
                    # Check for tasks that are ready to run
                    ready_tasks = self._get_ready_tasks()

                    if ready_tasks:
                        for task_info in ready_tasks:
                            if self.stop_event.is_set():
                                break
                            self._process_task(task_info)

                    # Sleep briefly to avoid busy waiting
                    time.sleep(1.0)

                except Exception as e:
                    logger.error(f"Error in worker loop: {e}")
                    time.sleep(5.0)  # Wait before retrying

        except Exception as e:
            logger.error(f"Fatal error in worker loop: {e}")
            self._set_state(ProcessState.ERROR)
        finally:
            logger.info("Worker thread stopping")

    def _get_ready_tasks(self) -> List[TaskInfo]:
        """
        Get tasks that are ready to be executed.

        Returns:
            List[TaskInfo]: List of tasks ready for execution
        """
        ready_tasks = []
        current_time = datetime.now()

        for task_info in self.active_tasks.values():
            if task_info.next_run <= current_time:
                ready_tasks.append(task_info)

        # Sort by next_run time (earliest first)
        ready_tasks.sort(key=lambda t: t.next_run)

        return ready_tasks

    def _process_task(self, task_info: TaskInfo) -> None:
        """
        Process a single task.

        Args:
            task_info (TaskInfo): Task to process
        """
        try:
            logger.info(f"Processing task: {task_info.name}")

            # Update task statistics
            task_info.last_run = datetime.now()
            task_info.run_count += 1
            self.total_tasks_processed += 1

            # Here you would integrate with your actual task execution logic
            # For now, this is a placeholder that simulates task execution
            self._execute_task(task_info)

            # Update next run time (this should be handled by your task execution logic)
            # For now, we'll remove the task from active tasks
            if task_info.name in self.active_tasks:
                del self.active_tasks[task_info.name]

            logger.info(f"Task {task_info.name} completed successfully")

        except Exception as e:
            logger.error(f"Error processing task {task_info.name}: {e}")
            task_info.error_count += 1

    def _execute_task(self, task_info: TaskInfo) -> None:
        """
        Execute the actual task logic.

        This is a placeholder method that should be replaced with
        actual task execution logic.

        Args:
            task_info (TaskInfo): Task to execute
        """
        # Placeholder implementation
        logger.info(f"Executing task: {task_info.name}")
        time.sleep(0.1)  # Simulate work
        logger.info(f"Task {task_info.name} execution completed")

    def _clear_task_queue(self) -> None:
        """Clear all tasks from the queue."""
        try:
            while not self.task_queue.empty():
                try:
                    self.task_queue.get_nowait()
                except Empty:
                    break

            self.active_tasks.clear()
            logger.debug("Task queue cleared")

        except Exception as e:
            logger.error(f"Error clearing task queue: {e}")

    def get_status(self) -> Dict[str, Any]:
        """
        Get current status information.

        Returns:
            Dict[str, Any]: Status information
        """
        uptime = None
        if self.start_time:
            uptime = str(datetime.now() - self.start_time)

        return {
            "state": self.get_state().value,
            "uptime": uptime,
            "total_tasks_processed": self.total_tasks_processed,
            "active_tasks_count": len(self.active_tasks),
            "active_tasks": [
                {
                    "name": task.name,
                    "next_run": str(task.next_run),
                    "last_run": str(task.last_run) if task.last_run else None,
                    "run_count": task.run_count,
                    "error_count": task.error_count
                }
                for task in self.active_tasks.values()
            ]
        }

    def reload_tasks(self) -> bool:
        """
        Reload tasks from configuration.

        Returns:
            bool: True if reload was successful, False otherwise
        """
        try:
            if self.get_state() != ProcessState.RUNNING:
                logger.warning(
                    "Cannot reload tasks - process manager not running")
                return False

            logger.info("Reloading tasks from configuration")
            self._load_tasks()
            logger.info("Tasks reloaded successfully")
            return True

        except Exception as e:
            logger.error(f"Failed to reload tasks: {e}")
            return False

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - ensure cleanup."""
        if self.get_state() != ProcessState.STOPPED:
            self.stop_processing()


# Example usage
if __name__ == "__main__":
    import sys
    from pathlib import Path
    sys.path.append(str(Path(__file__).parent.parent.parent))
    from module.control.config.config_model import ConfigModel

    try:
        # Create a test configuration
        config = ConfigModel("osa")

        # Use context manager for proper cleanup
        with ProcessManager(config) as pm:
            logger.background(f"Starting process manager...")
            if pm.start_processing():
                logger.background("Process manager started successfully")

                # Let it run for a short time
                time.sleep(5)

                status = pm.get_status()
                logger.background(f"Status: {status}")

            else:
                logger.error("Failed to start process manager")

    except KeyboardInterrupt:
        logger.error("\nShutdown requested...")
    except Exception as e:
        logger.error(f"Error: {e}")
