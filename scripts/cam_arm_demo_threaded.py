import threading
import time
import cv2
import wmi
import psutil
from wlkata_controller import WlkataRobotController, PositionMode, Motion
from OpenCV_depth_cam.oakd_lite_camera import OakDLiteCamera

def get_usb_controllers():
    """Get list of USB host controllers on Windows."""
    c = wmi.WMI()
    return [
        {'name': controller.Name, 'device_id': controller.DeviceID, 'status': controller.Status}
        for controller in c.Win32_USBController()
    ]

def assign_devices_to_separate_controllers():
    """Assign robot and camera to different USB controllers (for reference)."""
    controllers = get_usb_controllers()
    if len(controllers) < 2:
        raise RuntimeError("Need at least 2 USB controllers.")
    print("Available USB Controllers:")
    for i, c in enumerate(controllers):
        print(f"{i}: {c['name']} (Status: {c['status']})")
    return controllers[0]['device_id'], controllers[1]['device_id']

def robot_worker(robot):
    """Thread function for robot movements."""
    try:
        robot.home()
        while True:
            robot.set_joint_angles([45, -15, 30, 0, 0, 0])
            time.sleep(2)  # Delay to reduce USB load
            robot.set_joint_angles([-45, 15, -30, 0, 0, 0])
            time.sleep(2)
    except Exception as e:
        print(f"Robot error: {e}")

def camera_worker(camera):
    """Thread function for camera streaming."""
    try:
        camera.stream_video(window_name="OAK-D Lite + Robot")
    except Exception as e:
        print(f"Camera error: {e}")

def main():
    try:
        # Assign USB controllers (for logging)
        robot_ctrl, camera_ctrl = assign_devices_to_separate_controllers()
        print(f"\nRobot on USB: {robot_ctrl}\nCamera on USB: {camera_ctrl}\n")

        # Initialize devices
        robot = WlkataRobotController(port="COM3", baudrate=115200, timeout=1)
        camera = OakDLiteCamera(preview_size=(640, 480), fps=15)  # Lower FPS for bandwidth

        # Start threads
        robot_thread = threading.Thread(target=robot_worker, args=(robot,), daemon=True)
        camera_thread = threading.Thread(target=camera_worker, args=(camera,), daemon=True)

        robot_thread.start()
        camera_thread.start()

        # Keep main thread alive
        while True:
            time.sleep(1)

    except KeyboardInterrupt:
        print("\nStopping threads...")
    finally:
        print("Cleaning up...")
        cv2.destroyAllWindows()

if __name__ == "__main__":
    # Disable USB selective suspend (run as Admin)
    try:
        import subprocess
        subprocess.run([
            'powercfg', '/setdcvalueindex', 'SCHEME_CURRENT', 
            '2a737441-1930-4402-8d77-b2bebba308a3', 
            '48e6b7a6-50f5-4782-a5d4-53bb8f07e226', '0'
        ], check=True)
        print("Disabled USB selective suspend")
    except Exception as e:
        print(f"Couldn't disable USB suspend (run as Admin): {e}")

    # Set high process priority
    p = psutil.Process()
    p.nice(psutil.HIGH_PRIORITY_CLASS)
    
    main()