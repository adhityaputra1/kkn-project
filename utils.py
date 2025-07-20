import requests
from PIL import Image, ImageEnhance
import pandas as pd
import io

def extract_text(image_file):
    api_key = "K85885739088957"  # <- Ganti jika API-nya limit

    # 1. Preprocessing: convert to grayscale & enhance contrast
    image = Image.open(image_file).convert("L")  # Grayscale
    enhancer = ImageEnhance.Contrast(image)
    enhanced_image = enhancer.enhance(2.0)  # Perkuat kontras 2x

    # 2. Simpan ke buffer
    img_bytes = io.BytesIO()
    enhanced_image.save(img_bytes, format='PNG')
    img_bytes.seek(0)

    # 3. Kirim ke OCR.Space API
    payload = {
        'isOverlayRequired': False,
        'apikey': api_key,
        'language': 'ind'
    }

    files = {
        'file': ('image.png', img_bytes.getvalue())
    }

    response = requests.post('https://api.ocr.space/parse/image',
                             data=payload,
                             files=files)

    result = response.json()

    try:
        parsed_text = result['ParsedResults'][0]['ParsedText']
        return parsed_text
    except Exception as e:
        return f"OCR failed: {e}"

def save_to_excel(data_dict, filename='hasil_ekstraksi.xlsx'):
    df = pd.DataFrame([data_dict])
    df.to_excel(filename, index=False)
    return filename
