import qrcode

def generate_qr_code(data, file_name="qr_code.png"):
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(data)
    qr.make(fit=True)

    img = qr.make_image(fill="black", back_color="white")
    img.save(file_name)
    print(f"QR code saved as {file_name}")

if __name__ == "__main__":
    generate_qr_code("gearbox", "gearbox.png")
    generate_qr_code("engine", "gearbox.png")
