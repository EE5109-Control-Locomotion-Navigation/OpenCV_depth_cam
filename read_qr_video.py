import cv2
from pyzbar.pyzbar import decode
import depthai as dai

def read_qr_code_from_oak():
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
            qr_codes = decode(frame)

            for qr_code in qr_codes:
                data = qr_code.data.decode('utf-8')
                print(f"QR Code Data: {data}")
                cv2.destroyAllWindows()
                return data

            # Display the camera feed
            cv2.imshow("OAK-D Lite QR Code Scanner", frame)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    cv2.destroyAllWindows()
    print("No QR code found.")
    return None

if __name__ == "__main__":
    read_qr_code_from_oak()
