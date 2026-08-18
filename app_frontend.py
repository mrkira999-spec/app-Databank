import streamlit as st
import requests
import pandas as pd
from PIL import Image
import os
import io

API_URL = "http://localhost:8000"

st.set_page_config(page_title="Bank Data F-SB SEMAR", layout="wide")
st.title("📑 Bank Data Anggota & KTP - F-SB SEMAR")

# Membagi aplikasi menjadi 3 Tab utama
tab1, tab2, tab3 = st.tabs(["➕ 1. Input Data Anggota", "📋 2. Data Semua Anggota", "🔍 3. Cari Data Anggota"])

# ================= TAB 1: INPUT DATA =================
with tab1:
    st.subheader("Formulir Pendaftaran Anggota Baru")
    with st.form("form_tambah", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            nama = st.text_input("Nama Lengkap*")
            nik = st.text_input("NIK (Opsional)")
            telp = st.text_input("No. Telepon / WhatsApp")
            ttl = st.text_input("Tempat, Tanggal Lahir")
            alamat = st.text_area("Alamat / Jalan / RT-RW*")
        with col2:
            kel = st.text_input("Kelurahan / Desa*")
            kec = st.text_input("Kecamatan*")
            kota = st.text_input("Kota / Kabupaten*")
            prov = st.text_input("Provinsi*")
            foto = st.file_uploader("Upload Foto KTP (Opsional)", type=['jpg', 'jpeg', 'png'])

        submit = st.form_submit_button("Simpan Data Anggota")

        if submit:
            if not nama or not kel or not kec or not kota or not prov or not alamat:
                st.error("Harap isi semua kolom wajib dengan tanda (*)")
            else:
                data_payload = {
                    "nama_lengkap": nama, "nik": nik, "no_telepon": telp,
                    "tempat_tgl_lahir": ttl, "alamat": alamat, "kelurahan": kel,
                    "kecamatan": kec, "kota_kabupaten": kota, "provinsi": prov
                }
                files = {"foto_ktp": (foto.name, foto.getvalue(), foto.type)} if foto else None
                res = requests.post(f"{API_URL}/anggota/", data=data_payload, files=files)
                
                if res.status_code == 200:
                    st.success("✅ Data berhasil disimpan ke database lokal & otomatis tersinkron ke Google Sheets!")
                else:
                    st.error("❌ Gagal menyimpan data.")

# ================= TAB 2: DATA SEMUA ANGGOTA =================
with tab2:
    st.subheader("Daftar Seluruh Anggota Terdaftar")
    
    try:
        response = requests.get(f"{API_URL}/anggota/all")
        if response.status_code == 200:
            data = response.json()
            if data:
                # Konversi data ke Pandas DataFrame untuk tombol Download
                df_download = pd.DataFrame(data)
                
                # Tombol Download Excel / CSV
                col_dl1, col_dl2, _ = st.columns([1, 1, 2])
                
                # Download CSV
                csv_data = df_download.to_csv(index=False).encode('utf-8')
                col_dl1.download_button(
                    label="📥 Download as CSV",
                    data=csv_data,
                    file_name="data_anggota_fsb_semar.csv",
                    mime="text/csv",
                )
                
                # Download Excel (menggunakan buffer)
                output = io.BytesIO()
                with pd.ExcelWriter(output, engine='openpyxl') as writer:
                    df_download.to_excel(writer, index=False, sheet_name='Anggota')
                excel_data = output.getvalue()
                
                col_dl2.download_button(
                    label="📊 Download as Excel",
                    data=excel_data,
                    file_name="data_anggota_fsb_semar.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                )
                
                st.divider()

                # Tampilkan daftar list ekspansi data
                for item in data:
                    with st.expander(f"👤 {item['nama_lengkap']} — NIK: {item['nik'] or '-'}"):
                        c1, c2 = st.columns([2, 1])
                        with c1:
                            st.write(f"**Tanggal Input:** {item['tanggal_input']}")
                            st.write(f"**Tempat, Tgl Lahir:** {item['tempat_tgl_lahir'] or '-'}")
                            st.write(f"**No. Telepon:** {item['no_telepon'] or '-'}")
                            st.write(f"**Alamat Lengkap:** {item['alamat_lengkap']}")
                        with c2:
                            st.write("**Foto KTP:**")
                            if item['foto_path'] and os.path.exists(item['foto_path']):
                                img = Image.open(item['foto_path'])
                                st.image(img, caption="KTP Anggota", width=250)
                            else:
                                st.info("Tidak ada foto KTP")
                        
                        if st.button(f"🗑️ Hapus Anggota Ini", key=item['id']):
                            requests.delete(f"{API_URL}/anggota/{item['id']}")
                            st.success("Data berhasil dihapus!")
                            st.rerun()
            else:
                st.info("Belum ada data anggota yang tersimpan.")
    except Exception as e:
        st.error(f"Gagal memuat data: {e}")

# ================= TAB 3: PENCARIAN DATA =================
with tab3:
    st.subheader("Panel Pencarian & Filter Data Anggota")
    
    col_s1, col_s2 = st.columns(2)
    keyword = col_s1.text_input("Cari berdasarkan Nama atau NIK")
    wilayah = col_s2.text_input("Filter Wilayah (Kecamatan / Kabupaten / Provinsi)")
    
    if st.button("🔍 Cari Data"):
        params = {"q": keyword, "wilayah": wilayah}
        res = requests.get(f"{API_URL}/anggota/search", params=params)
        if res.status_code == 200:
            hasil = res.json()
            if hasil:
                st.success(f"Ditemukan {len(hasil)} data yang sesuai.")
                df = pd.DataFrame(hasil)[['tanggal_input', 'nik', 'nama_lengkap', 'no_telepon', 'tempat_tgl_lahir', 'alamat_lengkap', 'status_ktp']]
                st.dataframe(df, use_container_width=True)
            else:
                st.warning("Tidak ada data yang cocok dengan pencarian Anda.")