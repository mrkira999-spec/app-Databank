import streamlit as st
import sqlite3
import pandas as pd
import os

# Konfigurasi Database dan Folder Penyimpanan Foto
DB_NAME = "bank_data_db.db"
UPLOAD_DIR = "storage"

if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)

def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS anggota (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nama TEXT,
                    nik TEXT,
                    telp TEXT,
                    ttl TEXT,
                    alamat TEXT,
                    kel TEXT,
                    kec TEXT,
                    kota TEXT,
                    prov TEXT,
                    foto TEXT,
                    status TEXT
                )''')
    conn.commit()
    conn.close()

init_db()

st.title("Bank Data Anggota & KTP - F-SB SEMAR")

menu = ["1. Input Data Anggota", "2. Data Semua Anggota", "3. Cari Data Anggota"]
choice = st.sidebar.selectbox("Menu", menu)

if choice == "1. Input Data Anggota":
    st.subheader("Formulir Pendaftaran Anggota Baru")
    
    with st.form("form_tambah", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            nama = st.text_input("Nama Lengkap*")
            nik = st.text_input("NIK")
            telp = st.text_input("No. Telepon / WhatsApp")
            ttl = st.text_input("Tempat, Tanggal Lahir")
            alamat = st.text_area("Alamat / Jalan / RT-RW*")
        
        with col2:
            kel = st.text_input("Kelurahan / Desa*")
            kec = st.text_input("Kecamatan*")
            kota = st.text_input("Kota / Kabupaten*")
            prov = st.text_input("Provinsi*")
            foto = st.file_uploader("Upload Foto KTP (Opsional)", type=['jpg', 'jpeg', 'png'])
            status = st.selectbox("Status Anggota", ["Aktif", "Tidak Aktif"])

        submit = st.form_submit_button("Simpan Data Anggota")

    if submit:
        if not nama or not alamat or not kel or not kec or not kota or not prov:
            st.warning("Mohon lengkapi kolom bertanda bintang (*)")
        else:
            foto_path = ""
            if foto is not None:
                foto_path = os.path.join(UPLOAD_DIR, foto.name)
                with open(foto_path, "wb") as f:
                    f.write(foto.getbuffer())

            conn = sqlite3.connect(DB_NAME)
            c = conn.cursor()
            c.execute("""INSERT INTO anggota (nama, nik, telp, ttl, alamat, kel, kec, kota, prov, foto, status) 
                         VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                      (nama, nik, telp, ttl, alamat, kel, kec, kota, prov, foto_path, status))
            conn.commit()
            conn.close()
            st.success(f"Data anggota atas nama {nama} berhasil disimpan!")

elif choice == "2. Data Semua Anggota":
    st.subheader("Daftar Seluruh Anggota Terdaftar")
    conn = sqlite3.connect(DB_NAME)
    df = pd.read_sql("SELECT * FROM anggota", conn)
    conn.close()
    
    if not df.empty:
        st.dataframe(df, use_container_width=True)
    else:
        st.info("Belum ada data anggota yang tersimpan.")

elif choice == "3. Cari Data Anggota":
    st.subheader("Cari Data Anggota")
    cari = st.text_input("Masukkan nama atau NIK yang dicari")
    
    if cari:
        conn = sqlite3.connect(DB_NAME)
        df = pd.read_sql(f"SELECT * FROM anggota WHERE nama LIKE '%{cari}%' OR nik LIKE '%{cari}%'", conn)
        conn.close()
        
        if not df.empty:
            st.dataframe(df, use_container_width=True)
        else:
            st.warning("Data tidak ditemukan.")