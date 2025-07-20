import streamlit as st
from utils import extract_text, save_to_excel
from ocr_parser import parse_sppt_text
import os

# Konfigurasi tampilan
st.set_page_config(page_title="Ekstraksi SPPT ke Excel", layout="centered")
st.title("📄 Ekstrak Data SPPT PBB dari Gambar")

# Upload gambar
uploaded_file = st.file_uploader("Unggah gambar SPPT", type=["png", "jpg", "jpeg", "pdf"])

if uploaded_file:
    st.image(uploaded_file, caption="Gambar Terunggah", use_column_width=True)

    if st.button("🔍 Ekstrak Data"):
        with st.spinner("Sedang memproses gambar..."):
            # Menggunakan OCR.Space API dari utils.py
            text = extract_text(uploaded_file)

        st.subheader("📃 Hasil OCR Mentah:")
        st.text_area("Teks Hasil OCR", value=text, height=300)

        # Parsing teks hasil OCR menjadi dictionary
        parsed = parse_sppt_text(text)

        if parsed:
            st.success("✅ Data berhasil diambil. Silakan koreksi jika ada yang salah:")

            with st.form("edit_form"):
                edited = {}

                # Form input manual
                for k, v in parsed.items():
                    if k == "NJOP Bumi (total)":
                        continue  # Otomatis dihitung di bawah
                    edited[k] = st.text_input(k, value=v, key=k)

                # Hitung otomatis NJOP Bumi (total)
                try:
                    luas = float(edited.get("Luas Bumi (m2)", "0").replace(".", "").replace(",", "."))
                    njop = float(edited.get("NJOP Bumi per m2", "0").replace(".", "").replace(",", "."))
                    njop_total = int(luas * njop)
                    njop_total_str = f"{njop_total:,}".replace(",", ".")
                except:
                    njop_total_str = ""

                st.text_input("NJOP Bumi (total)", value=njop_total_str, disabled=True, key="NJOP Bumi (total)")
                edited["NJOP Bumi (total)"] = njop_total_str

                submitted = st.form_submit_button("💾 Simpan ke Excel")

            if submitted:
                file_path = save_to_excel(edited)
                if os.path.exists(file_path):
                    st.success(f"📁 File berhasil disimpan: {file_path}")
                    with open(file_path, "rb") as f:
                        st.download_button("⬇️ Download Excel", f, file_name="hasil_ekstraksi.xlsx")
                else:
                    st.error("❌ Gagal menyimpan file Excel. Cek izin folder atau error lainnya.")
        else:
            st.warning("⚠️ Data tidak dikenali. Pastikan gambar jelas dan sesuai format SPPT.")
