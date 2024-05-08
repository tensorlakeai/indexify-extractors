import easyocr

def get_text(image):
    # Create an instance of the EasyOCR reader
    reader = easyocr.Reader(['en'])

    # Perform text detection and recognition
    result = reader.readtext(image, detail = 0)

    # Extract the recognized text
    text = ' '.join(result)

    return text