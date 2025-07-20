import re

def parse_sppt_text(text):
    data = {
        "NOP": "",
        "NPWP": "",
        "Alamat Objek Pajak": "",
        "Nama Wajib Pajak": "",
        "Alamat Wajib Pajak": "",
        "Kota": "",
        "Luas Bumi (m2)": "",
        "Kelas Bumi": "",
        "NJOP Bumi per m2": "",
        "NJOP Bumi (total)": "",
        "Luas Bangunan (m2)": "",
        "Kelas Bangunan": "",
        "NJOP Bangunan per m2": "",
        "NJOP Bangunan (total)": "",
        "Total NJOP": "",
        "NJKP": "",
        "PBB Terutang": "",
        "Tanggal Jatuh Tempo": ""
    }

    # Contoh regex sederhana (disesuaikan dengan pola nyata)
    # NOP dan NPWP
    nop_match = re.search(r'NOP\s*[:\-]?\s*([\d\.\-]+)', text, re.IGNORECASE)
    if nop_match:
        data["NOP"] = nop_match.group(1).strip()
    npwp_match = re.search(r'NPWP\s*:\s*([\d\.\-]+)', text, re.IGNORECASE)
    if npwp_match:
        data["NPWP"] = npwp_match.group(1).strip()

    # Letak Objek Pajak (LOP) dan Nama/Alamat Wajib Pajak (NAWP) pakai regex multiline
    lop_match = re.search(r'LETAK OBJEK PAJAK[\s\n\r]*([\s\S]*?)\n\s*(NAMA DAN ALAMAT WAJIB PAJAK|NPWP|OBJEK PAJAK|LUAS|NJOP)', text, re.IGNORECASE)
    if lop_match:
        # Ambil hanya baris yang mengandung GG, RT, RW, NAGRI, PURWAKARTA dan bukan label/nama
        alamat_lop_lines = [l.strip() for l in lop_match.group(1).split('\n')]
        alamat_lop_clean = []
        for l in alamat_lop_lines:
            if l and not re.search(r'(NAMA DAN ALAMAT WAJIB PAJAK|NPWP|OBJEK PAJAK|LUAS|NJOP)', l, re.IGNORECASE):
                # Hanya ambil baris yang mengandung GG, RT, RW, NAGRI, PURWAKARTA
                if re.search(r'(GG|RT|RW|NAGRI|PURWAKARTA)', l, re.IGNORECASE):
                    # Hapus nama orang jika ada di belakang (misal "SISWADI")
                    l = re.sub(r'\b([A-Z][A-Z ]+)$', '', l).strip(' ,:')
                    alamat_lop_clean.append(l)
        # Gabungkan, hapus koma ganda dan spasi berlebih
        alamat_lop_str = ', '.join(alamat_lop_clean)
        alamat_lop_str = re.sub(r',\s*,', ',', alamat_lop_str)
        alamat_lop_str = re.sub(r'\s+', ' ', alamat_lop_str)
        alamat_lop_str = alamat_lop_str.strip(' ,')
        data["Alamat Objek Pajak"] = alamat_lop_str
    nawp_match = re.search(r'NAMA DAN ALAMAT WAJIB PAJAK[\s\n\r]*([\s\S]*?)(\n\s*(NPWP|OBJEK PAJAK|LUAS|NJOP|$))', text, re.IGNORECASE)
    if nawp_match:
        nawp_block = nawp_match.group(1).strip().split('\n')
        if nawp_block:
            # Ambil hanya kata terakhir dari baris pertama (nama wajib pajak)
            nama_line = nawp_block[0].strip()
            nama_parts = nama_line.split()
            if nama_parts:
                data["Nama Wajib Pajak"] = nama_parts[-1]
            if len(nawp_block) > 1:
                alamat_nawp_lines = [x.strip() for x in nawp_block[1:] if x.strip()]
                alamat_nawp_clean = []
                for l in alamat_nawp_lines:
                    # Hanya ambil baris yang mengandung GG, RT, RW, NAGRI, PURWAKARTA
                    if re.search(r'(GG|RT|RW|NAGRI|PURWAKARTA)', l, re.IGNORECASE):
                        # Hapus awalan RT:000 RW:00 PRSL: jika ada
                        l = re.sub(r'RT:\d{2,3}\s*RW:\d{2,3}\s*PRSL:?', '', l, flags=re.IGNORECASE)
                        l = re.sub(r'RT:\d{2,3}\s*RW:\d{2,3}', '', l, flags=re.IGNORECASE)
                        l = re.sub(r'PRSL:?', '', l, flags=re.IGNORECASE)
                        l = re.sub(r'[^A-Za-z0-9.,\s:-]', '', l)
                        l = l.strip(' ,:')
                        # Hapus label/angka tidak relevan
                        if l and not re.search(r'(NPWP|NAMA|OBJEK PAJAK|LUAS|NJOP)', l, re.IGNORECASE):
                            alamat_nawp_clean.append(l)
                # Gabungkan, hapus koma ganda dan spasi berlebih
                alamat_nawp_str = ', '.join(alamat_nawp_clean)
                alamat_nawp_str = re.sub(r',\s*,', ',', alamat_nawp_str)
                alamat_nawp_str = re.sub(r'\s+', ' ', alamat_nawp_str)
                alamat_nawp_str = alamat_nawp_str.strip(' ,')
                data["Alamat Wajib Pajak"] = alamat_nawp_str

    # Kota: regex cari PURWAKARTA (atau kota lain) setelah blok NAWP
    kota_match = re.search(r'(PURWAKARTA|KOTA\s+[A-Z]+)', text, re.IGNORECASE)
    if kota_match:
        data["Kota"] = kota_match.group(1).strip().upper()
    # Fallback Kota: dua baris setelah NAWP
    alamat_lines = text.splitlines()
    for i, line in enumerate(alamat_lines):
        if 'NAMA DAN ALAMAT WAJIB PAJAK' in line.upper():
            if i+2 < len(alamat_lines) and not data["Kota"]:
                data["Kota"] = alamat_lines[i+2].strip()
            break

    # Tabel Bumi dan Bangunan: regex dua baris angka, ambil langsung dari OCR
    tabel_match = re.search(r'OBJEK PAJAK.*?LUAS.*?NJOP PER M.*?TOTAL NJOP.*?\n([\d.,]+)\s+([\d.,]+)\s*\n([\d.,]+)\s+([\d.,]+)', text, re.IGNORECASE)
    if tabel_match:
        # Baris pertama: bumi, baris kedua: bangunan
        data["NJOP Bumi per m2"] = tabel_match.group(1).strip()
        data["NJOP Bumi (total)"] = tabel_match.group(2).strip()
        data["NJOP Bangunan per m2"] = tabel_match.group(3).strip()
        data["NJOP Bangunan (total)"] = tabel_match.group(4).strip()

    # Kolom lain (Total NJOP, NJKP, PBB Terutang, Tanggal Jatuh Tempo)
    total_njop = re.search(r'Total NJOP\s*[:\-]?\s*([\d\.]+)', text, re.IGNORECASE)
    if total_njop:
        data["Total NJOP"] = total_njop.group(1)
    njkp = re.search(r'NJKP\s*[:\-]?\s*([\d\.]+)', text, re.IGNORECASE)
    if njkp:
        data["NJKP"] = njkp.group(1)
    pbb_terutang = re.search(r'PBB Terutang\s*[:\-]?\s*([\d\.]+)', text, re.IGNORECASE)
    if pbb_terutang:
        data["PBB Terutang"] = pbb_terutang.group(1)
    tgl_jatuh_tempo = re.search(r'Tanggal Jatuh Tempo\s*[:\-]?\s*([\d\-/]+)', text, re.IGNORECASE)
    if tgl_jatuh_tempo:
        data["Tanggal Jatuh Tempo"] = tgl_jatuh_tempo.group(1)

    return data
