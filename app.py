import streamlit as st
from utils import extract_text, save_to_excel
from ocr_parser import parse_sppt_text




st.set_page_config(page_title="Ekstraksi SPPT ke Excel", layout="centered")

st.title("📄 Ekstrak Data SPPT PBB dari Gambar")
uploaded_file = st.file_uploader("Unggah gambar SPPT", type=["png", "jpg", "jpeg"])

if uploaded_file:
    st.image(uploaded_file, caption="Gambar Terunggah", use_column_width=True)

    if st.button("🔍 Ekstrak Data"):
        with st.spinner("Memproses..."):
            text = extract_text(uploaded_file)
            st.subheader("Hasil OCR Mentah:")
            st.text(text)
            parsed = parse_sppt_text(text)

            if parsed:
                st.success("✅ Data berhasil diambil. Silakan koreksi jika ada yang salah:")
                with st.form("edit_form"):
                    edited = {}
                    # Input manual dan otomatis
                    for k, v in parsed.items():
                        if k == "NJOP Bumi (total)":
                            continue  # akan diisi otomatis di bawah
                        elif k == "Luas Bumi (m2)":
                            edited[k] = st.text_input(k, value=v, key=k)
                        elif k == "NJOP Bumi per m2":
                            edited[k] = st.text_input(k, value=v, key=k)
                        else:
                            edited[k] = st.text_input(k, value=v, key=k)
                    # Hitung otomatis NJOP Bumi (total)
                    try:
                        luas = float(edited.get("Luas Bumi (m2)", "0").replace(",", "").replace(".", ""))
                        njop = float(edited.get("NJOP Bumi per m2", "0").replace(",", "").replace(".", ""))
                        njop_total = int(luas * njop)
                        njop_total_str = f"{njop_total:,}".replace(",", ".")
                    except:
                        njop_total_str = ""
                    st.text_input("NJOP Bumi (total)", value=njop_total_str, disabled=True, key="NJOP Bumi (total)")
                    edited["NJOP Bumi (total)"] = njop_total_str
                    submitted = st.form_submit_button("💾 Simpan ke Excel")
                if submitted:
                    import os
                    file_path = save_to_excel(edited)
                    if os.path.exists(file_path):
                        st.success(f"📁 File berhasil disimpan di: {file_path}")
                        with open(file_path, "rb") as f:
                            st.download_button("⬇️ Download Excel", f, file_name=file_path)
                    else:
                        st.error("❌ File Excel gagal dibuat. Cek izin folder atau error lain.")
            else:
                st.warning("Data tidak dikenali. Periksa kembali format gambar.")