def extract_text(image_file):
    import requests
    from PIL import ImageEnhance, Image
    import io

    api_key = "K85885739088957"

    # Preprocessing
    image = Image.open(image_file).convert("L")
    enhancer = ImageEnhance.Contrast(image)
    enhanced_image = enhancer.enhance(2.0)

    buffer = io.BytesIO()
    enhanced_image.save(buffer, format="PNG")
    buffer.seek(0)

    payload = {
        'isOverlayRequired': False,
        'apikey': api_key,
        'language': 'ind'
    }

    files = {
        'file': ('image.png', buffer.getvalue())
    }

    response = requests.post('https://api.ocr.space/parse/image', data=payload, files=files)
    
    try:
        result = response.json()
        print(result)  # Untuk debug lokal (tidak terlihat di Streamlit Cloud)
        st.json(result)  # Tampilkan hasil JSON di UI (sementara)
        parsed_text = result['ParsedResults'][0]['ParsedText']
        return parsed_text
    except Exception as e:
        return f"OCR failed: {e} | Response: {result}"
