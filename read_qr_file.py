import cv2
from pyzbar.pyzbar import decode

def read_qr_code(image_path):
    # Load the image
    image = cv2.imread(image_path)
    
    # Decode the QR code
    qr_codes = decode(image)
    
    # Extract and print data from QR codes
    for qr_code in qr_codes:
        data = qr_code.data.decode('utf-8')
        print(f"QR Code Data: {data}")
        return data
    
    print("No QR code found.")
    return None

if __name__ == "__main__":
    image_path = "qr_code.png"  # Replace with your QR code image file
    read_qr_code(image_path)