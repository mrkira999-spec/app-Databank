import streamlit as st
import sqlite3
import pandas as pd

# Inisialisasi Database SQLite langsung di aplikasi
DB_NAME = "bank_data_db.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS anggota 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, nama TEXT, nik TEXT, status TEXT)''')
    conn.commit()
    conn.close()

init_db()

st.title("Bank Data Anggota & KTP - F-SB SEMAR")

menu = ["1. Input Data Anggota", "2. Data Semua Anggota", "3. Cari Data Anggota"]
choice = st.sidebar.selectbox("Menu", menu)

if choice == "1. Input Data Anggota":
    st.subheader("Tambah Anggota Baru")
    nama = st.text_input("Nama")
    nik = st.text_input("NIK")
    status = st.selectbox("Status", ["Aktif", "Tidak Aktif"])
    
    if st.button("Simpan Data"):
        if nama and nik:
            conn = sqlite3.connect(DB_NAME)
            c = conn.cursor()
            c.execute("INSERT INTO anggota (nama, nik, status) VALUES (?, ?, ?)", (nama, nik, status))
            conn.commit()
            conn.close()
            st.success(f"Data {nama} berhasil disimpan!")
        else:
            st.warning("Nama dan NIK wajib diisi!")

elif choice == "2. Data Semua Anggota":
    st.subheader("Daftar Seluruh Anggota")
    conn = sqlite3.connect(DB_NAME)
    df = pd.read_sql("SELECT * FROM anggota", conn)
    conn.close()
    if not df.empty:
        st.dataframe(df, use_container_width=True)
    else:
        st.info("Belum ada data anggota yang tersimpan.")

elif choice == "3. Cari Data Anggota":
    st.subheader("Cari Anggota")
    cari = st.text_input("Masukkan nama yang dicari")
    if cari:
        conn = sqlite3.connect(DB_NAME)
        df = pd.read_sql(f"SELECT * FROM anggota WHERE nama LIKE '%{cari}%'", conn)
        conn.close()
        if not df.empty:
            st.dataframe(df, use_container_width=True)
        else:
            st.warning("Data tidak ditemukan.")