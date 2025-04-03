import cv2
import depthai as dai
import numpy as np

# Create pipeline
pipeline = dai.Pipeline()

# Define stereo depth node
stereo = pipeline.create(dai.node.StereoDepth)
left = pipeline.create(dai.node.MonoCamera)
right = pipeline.create(dai.node.MonoCamera)

# Configure cameras
left.setBoardSocket(dai.CameraBoardSocket.LEFT)
left.setResolution(dai.MonoCameraProperties.SensorResolution.THE_400_P)
right.setBoardSocket(dai.CameraBoardSocket.RIGHT)
right.setResolution(dai.MonoCameraProperties.SensorResolution.THE_400_P)

# Link cameras to stereo depth
left.out.link(stereo.left)
right.out.link(stereo.right)

# Enable Extended Disparity (Optional: for better long-range depth)
stereo.setExtendedDisparity(True)

# Apply Median Filtering (Removes small noise)
stereo.setMedianFilter(dai.StereoDepthProperties.MedianFilter.KERNEL_7x7)

# Create an output stream (Fixes the issue)
xout_depth = pipeline.create(dai.node.XLinkOut)
xout_depth.setStreamName("depth")
stereo.depth.link(xout_depth.input)  # Ensures depth output is used

# Variable to store depth map
depth_frame = None

# Function to get depth on mouse click
def get_depth(event, x, y, flags, param):
    if event == cv2.EVENT_LBUTTONDOWN:  # Left mouse button click
        if depth_frame is not None:
            distance = depth_frame[y, x] / 1000.0  # Convert mm to meters
            print(f"Depth at ({x}, {y}): {distance:.2f} meters")

# OpenCV window and mouse callback
cv2.namedWindow("Depth Image")
cv2.setMouseCallback("Depth Image", get_depth)

# Start the pipeline
with dai.Device(pipeline) as device:
    depth_queue = device.getOutputQueue(name="depth", maxSize=1, blocking=False)

    while True:
        depth_data = depth_queue.get()
        depth_frame = depth_data.getFrame()  # Get depth data

        # Normalize depth for visualization
        depth_vis = cv2.normalize(depth_frame, None, 0, 255, cv2.NORM_MINMAX, dtype=cv2.CV_8U)

        # Apply colormap
        depth_colored = cv2.applyColorMap(depth_vis, cv2.COLORMAP_TURBO)

        # Show depth image
        cv2.imshow("Depth Image", depth_colored)

        if cv2.waitKey(1) == ord('q'):
            break

cv2.destroyAllWindows()
