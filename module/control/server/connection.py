import os
from pathlib import Path
import sys
from typing import Optional
from ppadb.client import Client as AdbClient
import numpy as np
import cv2
from module.base.logger import logger
from module.control.config.config import Config


class Connection:
    """
    ADB connection management class for Android device communication.

    This class handles:
    - ADB device connection establishment
    - Screenshot capture and decoding
    - Connection state management
    - Error handling and recovery
    """

    # Default ADB server port
    ADB_SERVER_PORT = 5037

    def __init__(self, config: Config) -> None:
        """
        Initialize the ADB connection.

        Args:
            config (Config): Configuration object containing device settings

        Raises:
            ConnectionError: If device connection fails
            ValueError: If configuration is invalid
        """
        self.config: Config = config
        self.host: str = "127.0.0.1"
        self.port: Optional[int] = None
        self.adb: Optional[AdbClient] = None
        self.device = None
        self.screenshot = None

        # Parse device serial from configuration
        try:
            self._parse_device_serial()
            self._initialize_connection()
        except Exception as e:
            logger.error(f"Failed to initialize connection: {e}")
            raise ConnectionError(
                f"Could not establish device connection: {e}")

    def _parse_device_serial(self) -> None:
        """
        Parse device serial string to extract host and port.

        Raises:
            ValueError: If serial format is invalid
        """
        try:
            serial = self.config.model.script.device.serial
            if not serial:
                raise ValueError("Device serial not configured")

            if ":" not in serial:
                raise ValueError(
                    f"Invalid serial format: {serial}. Expected 'host:port'")

            parts = serial.split(":")
            if len(parts) != 2:
                raise ValueError(
                    f"Invalid serial format: {serial}. Expected 'host:port'")

            self.host = parts[0].strip()
            self.port = int(parts[1].strip())

            if not self.host:
                raise ValueError("Host cannot be empty")
            if self.port <= 0 or self.port > 65535:
                raise ValueError(f"Invalid port: {self.port}")

            logger.info(f"Parsed device address: {self.host}:{self.port}")

        except (ValueError, AttributeError) as e:
            logger.error(f"Failed to parse device serial: {e}")
            raise ValueError(f"Invalid device configuration: {e}")

    def _initialize_connection(self) -> None:
        """
        Initialize ADB connection and connect to device.

        Raises:
            ConnectionError: If connection establishment fails
        """
        try:
            # List available ADB devices
            logger.info("Listing ADB devices...")
            result = os.system("adb devices")
            if result != 0:
                logger.warning(
                    "adb devices command returned non-zero exit code")

            # Connect to device
            self.device = self.connect_device()

            if not self.device:
                raise ConnectionError("Failed to establish device connection")

            logger.info(
                f"Successfully connected to device: {self.host}:{self.port}")

        except Exception as e:
            logger.error(f"Failed to initialize ADB connection: {e}")
            raise ConnectionError(f"ADB connection failed: {e}")

    def connect_device(self):
        """
        Establish connection to the target device.

        Returns:
            Device: Connected ADB device object

        Raises:
            ConnectionError: If device connection fails
        """
        try:
            # Create ADB client
            self.adb = AdbClient(host=self.host, port=self.ADB_SERVER_PORT)
            logger.info(
                f"Created ADB client for {self.host}:{self.ADB_SERVER_PORT}")

            # Connect to remote device
            logger.info(f"Connecting to remote device {self.host}:{self.port}")
            if self.adb and self.port:
                connect_result = self.adb.remote_connect(self.host, self.port)

                if not connect_result:
                    raise ConnectionError(
                        f"Failed to connect to {self.host}:{self.port}")

                # Get device instance
                device_serial = f"{self.host}:{self.port}"
                device = self.adb.device(device_serial)
            else:
                raise ConnectionError("ADB client or port not initialized")

            if not device:
                raise ConnectionError(f"Device {device_serial} not found")

            # Test device connection with a simple command
            try:
                device.shell("echo test")
                logger.info(
                    f"Device connection test successful: {device_serial}")
            except Exception as e:
                raise ConnectionError(f"Device connection test failed: {e}")

            return device

        except Exception as e:
            logger.error(f"Failed to connect to device: {e}")
            raise ConnectionError(f"Device connection failed: {e}")

    def decode_image(self, image_data: bytes) -> Optional[np.ndarray]:
        """
        Decode raw image bytes to OpenCV format.

        Args:
            image_data (bytes): Raw image data from device

        Returns:
            Optional[np.ndarray]: Decoded image as numpy array, None if decoding fails
        """
        try:
            if not image_data:
                logger.warning("Empty image data received")
                return None

            # Convert bytes to numpy array
            image_bytes = np.frombuffer(image_data, dtype=np.uint8)

            # Decode image using OpenCV
            image = cv2.imdecode(image_bytes, cv2.IMREAD_COLOR)

            if image is None:
                logger.warning("Failed to decode image data")
                return None

            logger.debug(f"Successfully decoded image: {image.shape}")
            return image

        except Exception as e:
            logger.error(f"Failed to decode image: {e}")
            return None

    def get_screenshot(self) -> Optional[np.ndarray]:
        """
        Capture and decode a screenshot from the device.

        Returns:
            Optional[np.ndarray]: Screenshot as numpy array, None if capture fails

        Raises:
            ConnectionError: If device is not connected
        """
        try:
            if not self.is_connected():
                raise ConnectionError("Device not connected")

            logger.debug("Capturing screenshot...")
            if not self.device:
                raise ConnectionError("Device is None")
            raw_image = self.device.screencap()

            if not raw_image:
                logger.warning("No screenshot data received from device")
                return None

            # Decode the image
            decoded_image = self.decode_image(raw_image)

            if decoded_image is not None:
                self.screenshot = decoded_image
                logger.debug("Screenshot captured and decoded successfully")
            else:
                logger.warning("Failed to decode screenshot")

            return decoded_image

        except Exception as e:
            logger.error(f"Failed to capture screenshot: {e}")
            # Try to reconnect if connection is lost
            if "connection" in str(e).lower() or "broken" in str(e).lower():
                logger.info("Attempting to reconnect...")
                try:
                    self.reconnect()
                    return self.get_screenshot()  # Retry once after reconnect
                except Exception as reconnect_error:
                    logger.error(f"Reconnection failed: {reconnect_error}")
            raise

    def capture_screenshot(self, filepath: str | Path) -> bool:
        """
        Capture screenshot and save to file.

        Args:
            filepath (str | Path): Path where to save the screenshot

        Returns:
            bool: True if screenshot was saved successfully, False otherwise
        """
        try:
            image = self.get_screenshot()
            if image is None:
                logger.error("No screenshot captured")
                return False

            filepath = Path(filepath)

            # Create directory if it doesn't exist
            filepath.parent.mkdir(parents=True, exist_ok=True)

            # Save image
            success = cv2.imwrite(str(filepath), image)

            if success:
                logger.info(f"Screenshot saved to: {filepath}")
                return True
            else:
                logger.error(f"Failed to save screenshot to: {filepath}")
                return False

        except Exception as e:
            logger.error(f"Failed to capture and save screenshot: {e}")
            return False

    def is_connected(self) -> bool:
        """
        Check if device is currently connected.

        Returns:
            bool: True if device is connected, False otherwise
        """
        try:
            if not self.device:
                return False

            # Test connection with a simple command
            self.device.shell("echo test")
            return True

        except Exception:
            return False

    def reconnect(self) -> None:
        """
        Attempt to reconnect to the device.

        Raises:
            ConnectionError: If reconnection fails
        """
        try:
            logger.info("Attempting to reconnect to device...")

            # Clean up existing connection
            self.device = None
            self.adb = None

            # Re-establish connection
            self._initialize_connection()

            logger.info("Device reconnection successful")

        except Exception as e:
            logger.error(f"Failed to reconnect: {e}")
            raise ConnectionError(f"Reconnection failed: {e}")

    def disconnect(self) -> None:
        """
        Disconnect from the device and clean up resources.
        """
        try:
            if self.device:
                logger.info(
                    f"Disconnecting from device: {self.host}:{self.port}")
                # Note: ppadb doesn't have explicit disconnect methods
                # The connection will be cleaned up when the object is destroyed

            self.device = None
            self.adb = None
            self.screenshot = None

            logger.info("Device disconnected and resources cleaned up")

        except Exception as e:
            logger.error(f"Error during disconnect: {e}")

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - clean up resources."""
        self.disconnect()


# Test functionality
if __name__ == "__main__":
    import sys
    from pathlib import Path

    # Add module path for imports
    sys.path.append(str(Path(__file__).parent.parent.parent))

    try:
        from control.config.config import Config
        from module.base.logger import logger

        if len(sys.argv) < 2:
            print("Usage: python connection.py <filename>")
            sys.exit(1)

        filename = sys.argv[1]
        config = Config("osa")

        # Use context manager for proper resource cleanup
        with Connection(config) as conn:
            filepath = Path.cwd() / f"{filename}"  # 截图保存路径
            success = conn.capture_screenshot(filepath)

            if success:
                print(f"Screenshot saved successfully: {filepath}")
            else:
                print("Failed to capture screenshot")
                sys.exit(1)

    except ImportError as e:
        print(f"Import error: {e}")
        print("Make sure you're running this from the correct directory")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
