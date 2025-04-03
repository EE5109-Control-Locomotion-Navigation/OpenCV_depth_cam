import wlkatapython
import serial
from enum import Enum
import time

class PositionMode(Enum):
    ABSOLUTE = 0  # Absolute movement
    INCREMENTAL = 1  # Incremental movement

class Motion(Enum):
    FAST_MOVEMENT = 0  # Fast movement
    LINEAR_MOVEMENT = 1  # Linear movement

class WlkataRobotController:
    """Controller for the WLKata robot using serial communication.
       Replace COM3 and baudrate with your actual settings."""
    
    def __init__(self, port="COM3", baudrate=115200, timeout=1):
        """Initialize the WLKata robot controller."""
        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout
        self.serial_conn = None
        self.mirobot = None
        self.connect()  # Attempt to connect on initialization
        print("Robot controller initialized.")
    
    def connect(self):
        """Connect to the robot and initialize the controller."""
        try:
            print(f"Attempting to connect to {self.port}...")
            self.serial_conn = serial.Serial(self.port, self.baudrate, timeout=self.timeout)
            print(f"Connected to {self.port}")
            
            self.mirobot = wlkatapython.Wlkata_UART()
            self.mirobot.init(self.serial_conn, -1)
            
            if not self.mirobot:
                print("Mirobot initialization failed!")
                return False
            
            print("Mirobot initialized successfully.")
            return True
        except Exception as e:
            print(f"Connection failed: {e}")
            return False
    
    def disconnect(self):
        """Close the serial connection."""
        if self.serial_conn and self.serial_conn.is_open:
            print("Closing serial connection...")
            self.serial_conn.close()
            self.serial_conn = None  # Ensure it's fully released
            print("Serial connection closed.")

    def wait_for_completion(self, timeout=30):
        """Wait for the robot to finish its current operation."""
        start_time = time.time()
        
        while True:
            # Check the robot's status (this is a placeholder method)
            status = self.mirobot.getStatus()  # Hypothetical method that gets current status
            
            # Debugging print
            # print(f"Robot status: {status}")
            
            # If status indicates the operation is complete
            if status["state"] == "Idle":  # status will be "Idle" when operation is complete
                print("Operation completed.")
                break
            
            # Check for timeout
            if time.time() - start_time > timeout:
                print("Timeout waiting for completion.")
                break
            
            time.sleep(1)  # Sleep for a bit to avoid busy-waiting
    
    def home(self):
        """Send homing command to the robot."""
        if self.mirobot:
            print("Sending home command...")
            self.mirobot.homing()
            self.wait_for_completion()
            print("Homing completed.")
        else:
            print("Mirobot not initialized! Home command not sent.")
    
    def set_joint_angles(self, angles, mode=PositionMode.ABSOLUTE):
        """Set joint angles for the robot."""
        if self.mirobot:
            command = [mode.value] + angles
            print(f"Sending joint angles: {command}")
            self.mirobot.writeangle(*command)
            self.wait_for_completion()  # Wait for the robot to finish moving
            
        else:
            print("Mirobot not initialized! Cannot set joint angles.")
    
    def set_coordinates(self, coordinates, motion=Motion.LINEAR_MOVEMENT, mode=PositionMode.ABSOLUTE):
        """Set cartesian coordinates for the robot."""
        if self.mirobot:
            command = [motion.value, mode.value] + coordinates
            print(f"Sending coordinates: {command}")
            self.mirobot.writecoordinate(*command)
            self.wait_for_completion() # Wait for the robot to finish moving
        else:
            print("Mirobot not initialized! Cannot set coordinates.")
    
    def __enter__(self):
        """Context manager entry point."""
        if self.connect():
            return self
        else:
            print("Failed to connect within context manager.")
            raise Exception("Failed to connect to the robot.")
            #return None
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit point."""
        print("Exiting context manager...")
        self.disconnect()

# Example usage in a main script
if __name__ == "__main__":
    # Example usage of the WlkataRobotController 
    # replace "COM3" with your actual port
    # and ensure the baudrate matches your robot's settings
    with WlkataRobotController(port="COM3", baudrate=115200, timeout=1) as robot:
        robot.home()
        robot.set_joint_angles([30, 0, 0, 0, 0, 0])
        robot.set_coordinates([150, 50, 50, 0, 0, 0])
