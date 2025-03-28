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

# Enable Extended Disparity (improves long-range depth detection)
stereo.setExtendedDisparity(True)

# Apply Median Filtering (KERNEL_7x7 is strongest)
stereo.setMedianFilter(dai.StereoDepthProperties.MedianFilter.KERNEL_7x7)

# Configure advanced filtering
config = stereo.initialConfig.get()

# ✅ Spatial Filter (removes noise & fills holes)
config.postProcessing.spatialFilter.enable = True
config.postProcessing.spatialFilter.holeFillingRadius = 2
config.postProcessing.spatialFilter.alpha = 0.5  # 0 = less aggressive, 1 = more
config.postProcessing.spatialFilter.delta = 50   # Higher = preserves sharp edges

# ✅ Temporal Filter (stabilizes depth over time)
config.postProcessing.temporalFilter.enable = True
config.postProcessing.temporalFilter.persistencyMode = dai.StereoDepthConfig.PostProcessing.TemporalFilter.PersistencyMode.VALID_2_IN_LAST_3

# ✅ Speckle Filter (removes incorrect depth pixels)
config.postProcessing.speckleFilter.enable = True
config.postProcessing.speckleFilter.speckleRange = 50  # Adjust based on noise level

# Apply the new configuration
stereo.initialConfig.set(config)

# Create an output stream
xout_depth = pipeline.create(dai.node.XLinkOut)
xout_depth.setStreamName("depth")
stereo.depth.link(xout_depth.input)

# Start the pipeline
with dai.Device(pipeline) as device:
    depth_queue = device.getOutputQueue(name="depth", maxSize=1, blocking=False)

    while True:
        depth_frame = depth_queue.get().getFrame()

        # Normalize depth image for visualization
        depth_frame = (depth_frame * 255.0).astype(np.uint8)

        # Apply colormap
        depth_colored = cv2.applyColorMap(depth_frame, cv2.COLORMAP_TURBO)

        # Show depth image
        cv2.imshow("Filtered Depth Image", depth_colored)

        if cv2.waitKey(1) == ord('q'):
            break

cv2.destroyAllWindows()
