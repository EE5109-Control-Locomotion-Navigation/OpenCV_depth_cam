import cv2
import depthai as dai

# Create pipeline
pipeline = dai.Pipeline()

# Define a source - color camera
cam_rgb = pipeline.create(dai.node.ColorCamera)
cam_rgb.setPreviewSize(640, 480)
cam_rgb.setInterleaved(False)
cam_rgb.setFps(30)

# Create an output stream
xout = pipeline.create(dai.node.XLinkOut)
xout.setStreamName("video")
cam_rgb.preview.link(xout.input)

# Start pipeline
with dai.Device(pipeline) as device:
    video = device.getOutputQueue(name="video", maxSize=1, blocking=False)

    while True:
        frame = video.get().getCvFrame()  # Get frame as OpenCV image

        cv2.imshow("OAK-D Lite RGB Stream", frame)

        if cv2.waitKey(1) == ord('q'):
            break

cv2.destroyAllWindows()
