import cv2
import depthai as dai
import numpy as np

# Create pipeline
pipeline = dai.Pipeline()

# Define stereo depth camera nodes
stereo = pipeline.create(dai.node.StereoDepth)
left = pipeline.create(dai.node.MonoCamera)
right = pipeline.create(dai.node.MonoCamera)

# Set camera properties
left.setBoardSocket(dai.CameraBoardSocket.LEFT)
left.setResolution(dai.MonoCameraProperties.SensorResolution.THE_400_P)
right.setBoardSocket(dai.CameraBoardSocket.RIGHT)
right.setResolution(dai.MonoCameraProperties.SensorResolution.THE_400_P)

# Link cameras to stereo depth node
left.out.link(stereo.left)
right.out.link(stereo.right)

# Enable Extended Disparity mode
# stereo.setExtendedDisparity(True)

# Create an output stream
xout_depth = pipeline.create(dai.node.XLinkOut)
xout_depth.setStreamName("depth")
stereo.depth.link(xout_depth.input)

# Start pipeline
with dai.Device(pipeline) as device:
    depth_queue = device.getOutputQueue(name="depth", maxSize=1, blocking=True)

    while True:
        depth_frame = depth_queue.get().getFrame()  # Get depth frame

        # Normalize depth image for visualization (convert to 8-bit)
        #depth_frame = cv2.normalize(depth_frame, None, 0, 255, cv2.NORM_MINMAX, dtype=cv2.CV_8U)
        depth_frame = (depth_frame * 255.0).astype(np.uint8)
        # Apply a colormap for better visibility
        depth_colored = cv2.applyColorMap(depth_frame, cv2.COLORMAP_JET)

        # Show depth image
        cv2.imshow("Depth Image", depth_colored)

        if cv2.waitKey(1) == ord('q'):
            break

cv2.destroyAllWindows()
