import requests
from PIL import Image
import pandas as pd

def extract_text(image_file):
    api_key = "K85885739088957"  # Pakai API key kamu
    payload = {
        'isOverlayRequired': False,
        'apikey': api_key,
        'language': 'ind'
    }

    files = {
        'file': (image_file.name, image_file.getvalue())
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
