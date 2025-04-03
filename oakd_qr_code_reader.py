import cv2
from pyzbar.pyzbar import decode
import depthai as dai

class OakDQRCodeReader:
    def __init__(self, preview_size=(640, 480), fps=30):
        """
        Initialize OAK-D QR Code Reader.
        
        Args:
            preview_size (tuple): Camera resolution (width, height)
            fps (int): Frames per second
        """
        self.preview_size = preview_size
        self.fps = fps
        self.pipeline = None
        self.device = None
        self.video_queue = None
        self.running = False

    def initialize_pipeline(self):
        """Set up the DepthAI pipeline for QR code scanning."""
        self.pipeline = dai.Pipeline()
        
        # Configure color camera
        cam_rgb = self.pipeline.create(dai.node.ColorCamera)
        cam_rgb.setPreviewSize(*self.preview_size)
        cam_rgb.setInterleaved(False)
        cam_rgb.setFps(self.fps)
        
        # Set up output stream
        xout = self.pipeline.create(dai.node.XLinkOut)
        xout.setStreamName("video")
        cam_rgb.preview.link(xout.input)

    def start_stream(self):
        """Start the camera stream."""
        try:
            self.initialize_pipeline()
            self.device = dai.Device(self.pipeline)
            self.video_queue = self.device.getOutputQueue(
                name="video", 
                maxSize=1, 
                blocking=False
            )
            self.running = True
            print("Camera stream started successfully")
        except Exception as e:
            print(f"Failed to start camera stream: {e}")
            self.running = False

    def read_qr_code(self, display=False):
        """
        Read QR codes from the camera stream.
        
        Args:
            display (bool): Whether to show the camera feed
            
        Returns:
            str: QR code data if found, None otherwise
        """
        if not self.running:
            self.start_stream()
            
        try:
            while self.running:
                frame = self.video_queue.get().getCvFrame()
                qr_codes = decode(frame)
                
                if display:
                    cv2.imshow("OAK-D QR Code Scanner", frame)
                
                for qr_code in qr_codes:
                    data = qr_code.data.decode('utf-8')
                    print(f"QR Code Detected: {data}")
                    self.stop_stream()
                    return data
                
                if display and cv2.waitKey(1) == ord('q'):
                    break
                    
        except Exception as e:
            print(f"Error during QR code scanning: {e}")
        finally:
            if display:
                cv2.destroyAllWindows()
                
        print("No QR code detected")
        return None

    def stop_stream(self):
        """Stop the camera stream and clean up resources."""
        self.running = False
        if hasattr(self, 'device') and self.device:
            self.device.close()
        cv2.destroyAllWindows()
        print("Camera stream stopped")

    def __enter__(self):
        """Context manager entry point."""
        self.start_stream()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit point."""
        self.stop_stream()


if __name__ == "__main__":
    # Example usage
    with OakDQRCodeReader(preview_size=(640, 480), fps=30) as scanner:
        # Scan with display window
        qr_data = scanner.read_qr_code(display=True)
        if qr_data:
            print(f"Successfully read QR code: {qr_data}")