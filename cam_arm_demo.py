import threading
import time
import cv2
import wmi
import psutil
from wlkata_controller import WlkataRobotController, PositionMode, Motion
from OpenCV_depth_cam.oakd_lite_camera import OakDLiteCamera
from OpenCV_depth_cam.oakd_qr_code_reader import OakDQRCodeReader



def main():

    # Initialize devices
    # replace COM3 and baudrate with your actual settings
    robot = WlkataRobotController(port="COM3", baudrate=115200, timeout=1)
    camera = OakDLiteCamera(preview_size=(640, 480), fps=15)  # Lower FPS for bandwidth

    robot.home()

    with OakDQRCodeReader(preview_size=(640, 480), fps=30) as scanner:
        # Scan with display window
        qr_data = scanner.read_qr_code(display=True)
        if qr_data:
            print(f"Successfully read QR code: {qr_data}")

    # forward kinematics, use this to set the joint angles
    # Example angles: [joint1, joint2, joint3, joint4, joint5, joint6]
    robot.set_joint_angles([45, -15, 30, 0, 0, 0])

    time.sleep(1)  # Wait for the robot to reach the position

    # inverse kinematics, use this to set the robot to a specific position
    # Example coordinates: [x, y, z, roll, pitch, yaw]   
    robot.set_coordinates([150, 50, 50, 0, 0, 0])


if __name__ == "__main__":

    main()