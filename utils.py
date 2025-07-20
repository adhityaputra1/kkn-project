import pytesseract
from PIL import Image
import pandas as pd

def extract_text(image_file):
    image = Image.open(image_file)
    text = pytesseract.image_to_string(image, lang='ind')
    return text

def save_to_excel(data_dict, filename='hasil_ekstraksi.xlsx'):
    df = pd.DataFrame([data_dict])
    df.to_excel(filename, index=False)
    return filename