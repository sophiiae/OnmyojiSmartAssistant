from collections import deque
from typing import Optional
from module.base.exception import GameNotRunningError, GameStuckError, GameTooManyClickError
from module.base.logger import logger
from module.base.timer import Timer
from module.control.config.config import Config
from module.control.server.connection import Connection
import time


class Device:
    """
    Device management class for handling Android device interactions.

    This class provides:
    - Screenshot capture functionality
    - Touch input simulation (click/swipe)
    - Application lifecycle management
    - Stuck detection and prevention
    - Click tracking and validation
    """

    # Maximum number of clicks for a single button before triggering error
    MAX_SINGLE_BUTTON_CLICKS = 12
    # Maximum number of clicks for two buttons alternating before triggering error
    MAX_DUAL_BUTTON_CLICKS = 6
    # Maximum number of recent clicks to track
    CLICK_RECORD_SIZE = 15
    # Default stuck detection timeout (seconds)
    STUCK_TIMEOUT = 60
    # Extended stuck detection timeout for special states (seconds)
    STUCK_TIMEOUT_LONG = 300

    def __init__(self, config: Config):
        """
        Initialize the device with configuration.

        Args:
            config (Config): Configuration object containing device settings
        """
        self.device = None
        self.cnn: Optional[Connection] = None
        self.config: Config = config
        self.image = None

        # Detection and click tracking
        self.detect_record: set[str] = set()
        self.click_record: deque[str] = deque(maxlen=self.CLICK_RECORD_SIZE)

        # Timers for stuck detection
        self.stuck_timer = Timer(
            self.STUCK_TIMEOUT, retry_max=self.STUCK_TIMEOUT).start()
        self.stuck_timer_long = Timer(
            self.STUCK_TIMEOUT_LONG, retry_max=self.STUCK_TIMEOUT_LONG).start()

        # States that are allowed to wait longer before being considered stuck
        self.stuck_long_wait_list = ['BATTLE_STATUS_S', 'PAUSE', 'LOGIN_CHECK']

        # Initialize connection and device
        try:
            self.cnn = Connection(config)
            self.device = self.cnn.device if self.cnn else None
            logger.info(
                f"Device initialized successfully for config: {config.model.config_name}")
        except Exception as e:
            logger.error(f"Failed to initialize device: {e}")
            raise

    def screenshot(self):
        """
        Capture a screenshot from the device.

        Returns:
            np.ndarray: The captured screenshot as a numpy array

        Raises:
            Exception: If screenshot capture fails
        """
        try:
            if not self.cnn:
                raise RuntimeError("Connection not initialized")

            self.image = self.cnn.get_screenshot()
            if self.image is None:
                raise RuntimeError("Failed to capture screenshot - got None")

            logger.debug("Screenshot captured successfully")
            return self.image
        except Exception as e:
            logger.error(f"Failed to capture screenshot: {e}")
            raise

    def click(self, x: int, y: int):
        """
        Perform a click at the specified coordinates.

        Args:
            x (int): X coordinate
            y (int): Y coordinate

        Raises:
            Exception: If click operation fails
        """
        try:
            if not self.device:
                raise RuntimeError("Device not initialized")

            logger.info(f"[Device] Click ({x}, {y})")
            result = self.device.shell(f"input tap {x} {y}")

            if result is None:
                logger.warning(
                    f"Click command returned None for coordinates ({x}, {y})")

        except Exception as e:
            logger.error(f"Failed to click at ({x}, {y}): {e}")
            raise

    def swipe(self, start_x: int, start_y: int, end_x: int, end_y: int, duration: int = 300):
        """
        Perform a swipe gesture from start coordinates to end coordinates.

        Args:
            start_x (int): Starting X coordinate
            start_y (int): Starting Y coordinate
            end_x (int): Ending X coordinate
            end_y (int): Ending Y coordinate
            duration (int, optional): Swipe duration in milliseconds. Defaults to 300.

        Raises:
            Exception: If swipe operation fails
        """
        try:
            if not self.device:
                raise RuntimeError("Device not initialized")

            logger.info(
                f"[Device] Swipe from ({start_x},{start_y}) to ({end_x},{end_y}) in {duration}ms")
            result = self.device.shell(
                f"input swipe {start_x} {start_y} {end_x} {end_y} {duration}")

            if result is None:
                logger.warning(f"Swipe command returned None")

        except Exception as e:
            logger.error(
                f"Failed to swipe from ({start_x},{start_y}) to ({end_x},{end_y}): {e}")
            raise

    def stop_app(self, package_name: str):
        """
        Force stop an application by package name.

        Args:
            package_name (str): Android package name to stop

        Raises:
            Exception: If stop operation fails
        """
        try:
            if not self.device:
                raise RuntimeError("Device not initialized")

            if not package_name:
                raise ValueError("Package name cannot be empty")

            logger.info(f"[Device] Stopping application: {package_name}")
            result = self.device.shell(f"am force-stop {package_name}")

            if result is None:
                logger.warning(
                    f"Stop app command returned None for package: {package_name}")

        except Exception as e:
            logger.error(f"Failed to stop app {package_name}: {e}")
            raise

    def app_is_running(self) -> bool:
        """
        Check if the target application is currently running.

        Returns:
            bool: True if app is running, False otherwise
        """
        try:
            if not self.device:
                return False

            # This is a placeholder - actual implementation would check running processes
            # You would typically check running processes or use other methods
            logger.debug("Checking if app is running")
            return True  # Placeholder implementation

        except Exception as e:
            logger.error(f"Failed to check if app is running: {e}")
            return False

    def stuck_record_add(self, button: str):
        """
        Add a button to the stuck detection record.

        This is used when a button detection is expected to persist for a longer period.
        Call stuck_record_clear() when the condition is resolved.

        Args:
            button (str): Button identifier to add to stuck record
        """
        try:
            self.detect_record.add(str(button))
            logger.info(f'Added stuck record: {button}')
        except Exception as e:
            logger.error(
                f"Failed to add stuck record for button {button}: {e}")

    def stuck_record_clear(self):
        """
        Clear the stuck detection record and reset timers.

        This should be called when a stuck condition is resolved or
        when starting fresh detection.
        """
        try:
            self.detect_record.clear()
            self.stuck_timer.reset()
            self.stuck_timer_long.reset()
            logger.debug("Stuck detection record cleared")
        except Exception as e:
            logger.error(f"Failed to clear stuck record: {e}")

    def stuck_record_check(self):
        """
        Check if the device is stuck based on detection timers.

        Raises:
            GameStuckError: If device has been stuck too long
            GameNotRunningError: If game is not running
        """
        try:
            reached = self.stuck_timer.reached()
            reached_long = self.stuck_timer_long.reached()

            # Short timeout not reached - no action needed
            if not reached:
                return False

            # Long timeout not reached - check if we're in a state that's allowed to wait longer
            if not reached_long:
                for button in self.stuck_long_wait_list:
                    if button in self.detect_record:
                        logger.debug(f"Long wait allowed for button: {button}")
                        return False

            # We've been stuck too long
            logger.warning('Device has been stuck for too long')
            logger.warning(f'Waiting for buttons: {self.detect_record}')
            self.stuck_record_clear()

            # Check if the game is still running
            if self.app_is_running():
                raise GameStuckError(
                    'Device stuck - waited too long for UI response')
            else:
                raise GameNotRunningError('Game application is not running')

        except (GameStuckError, GameNotRunningError):
            # Re-raise these expected exceptions
            raise
        except Exception as e:
            logger.error(f"Error during stuck record check: {e}")
            raise

    def handle_control_check(self, button: str):
        """
        Handle control check after a successful interaction.

        This method should be called after any successful UI interaction
        to reset stuck detection and track click patterns.

        Args:
            button (str): Button identifier that was successfully interacted with
        """
        try:
            self.stuck_record_clear()
            self.click_record_add(button)
            self.click_record_check()
        except Exception as e:
            logger.error(
                f"Error during control check for button {button}: {e}")
            raise

    def click_record_add(self, button: str):
        """
        Add a button to the click history record.

        Args:
            button (str): Button identifier to add to click record
        """
        try:
            self.click_record.append(str(button))
            logger.debug(f"Added to click record: {button}")
        except Exception as e:
            logger.error(
                f"Failed to add click record for button {button}: {e}")

    def click_record_clear(self):
        """Clear the click history record."""
        try:
            self.click_record.clear()
            logger.debug("Click record cleared")
        except Exception as e:
            logger.error(f"Failed to clear click record: {e}")

    def click_record_remove(self, button: str) -> int:
        """
        Remove all instances of a button from the click record.

        Args:
            button (str): Button identifier to remove

        Returns:
            int: Number of instances removed
        """
        removed = 0
        try:
            button_str = str(button)
            maxlen = self.click_record.maxlen or self.CLICK_RECORD_SIZE
            for _ in range(maxlen):
                try:
                    self.click_record.remove(button_str)
                    removed += 1
                except ValueError:
                    # Value not in queue - no more instances to remove
                    break

            if removed > 0:
                logger.debug(
                    f"Removed {removed} instances of {button} from click record")

        except Exception as e:
            logger.error(
                f"Error removing button {button} from click record: {e}")

        return removed

    def click_record_check(self):
        """
        Check click patterns for potential infinite loops or stuck conditions.

        This method detects:
        1. Too many clicks on a single button
        2. Alternating clicks between two buttons (potential loop)

        Raises:
            GameTooManyClickError: If problematic click patterns are detected
        """
        try:
            if not self.click_record:
                return

            # Count occurrences of each button
            count = {}
            for button in self.click_record:
                count[button] = count.get(button, 0) + 1

            # Sort by click count (descending)
            sorted_counts = sorted(
                count.items(), key=lambda item: item[1], reverse=True)

            if not sorted_counts:
                return

            # Check for too many clicks on a single button
            most_clicked = sorted_counts[0]
            if most_clicked[1] >= self.MAX_SINGLE_BUTTON_CLICKS:
                logger.warning(
                    f'Too many clicks for button: {most_clicked[0]} ({most_clicked[1]} times)')
                logger.warning(f'Click history: {list(self.click_record)}')
                self.click_record_clear()
                raise GameTooManyClickError(
                    f'Too many clicks for button: {most_clicked[0]}')

            # Check for alternating clicks between two buttons
            if (len(sorted_counts) >= 2 and
                sorted_counts[0][1] >= self.MAX_DUAL_BUTTON_CLICKS and
                    sorted_counts[1][1] >= self.MAX_DUAL_BUTTON_CLICKS):

                button1, count1 = sorted_counts[0]
                button2, count2 = sorted_counts[1]

                logger.warning(
                    f'Too many alternating clicks between buttons: {button1} ({count1}), {button2} ({count2})')
                logger.warning(f'Click history: {list(self.click_record)}')
                self.click_record_clear()
                raise GameTooManyClickError(
                    f'Too many alternating clicks between: {button1}, {button2}')

        except GameTooManyClickError:
            # Re-raise expected exception
            raise
        except Exception as e:
            logger.error(f"Error during click record check: {e}")
            raise


if __name__ == '__main__':
    # Test device connection and basic functionality
    try:
        # Initialize device with default settings
        config = Config("osa")
        device = Device(config)

        # Test screenshot
        print("\nTesting screenshot capture...")
        screenshot = device.screenshot()
        if screenshot is not None:
            print(f"Screenshot captured successfully: {screenshot.shape}")

            # Save test screenshot
            import cv2
            cv2.imwrite("test_screenshot.png", screenshot)
            print("Screenshot saved as test_screenshot.png")

        # Test click patterns
        print("\nTesting click patterns...")
        test_points = [
            (100, 100),  # Top-left
            # (540, 960),  # Bottom-right
            # (540, 540),  # Center
            # (100, 540),  # Left-center
            # (980, 540),  # Right-center
        ]

        for x, y in test_points:
            print(f"Clicking at ({x}, {y})...")
            device.click(x, y)
            time.sleep(0.5)  # Wait between clicks

        # Test swipe patterns
        print("\nTesting swipe patterns...")
        test_swipes = [
            # (start_x, start_y, end_x, end_y, description)
            # (540, 960, 540, 100, "Up swipe"),      # Bottom to top
            # (540, 100, 540, 960, "Down swipe"),    # Top to bottom
            (100, 540, 980, 540, "Right swipe"),   # Left to right
            (980, 540, 100, 540, "Left swipe"),    # Right to left
            # (100, 100, 980, 960, "Diagonal swipe"),  # Diagonal
        ]

        for start_x, start_y, end_x, end_y, desc in test_swipes:
            print(
                f"Swiping {desc} from ({start_x}, {start_y}) to ({end_x}, {end_y})...")
            device.swipe(start_x, start_y, end_x, end_y)
            time.sleep(1.0)  # Wait between swipes

    except Exception as e:
        print(f"Error during testing: {e}")
