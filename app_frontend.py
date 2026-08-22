import streamlit as st
import pandas as pd
import os
import sqlalchemy

SUPABASE_URL = "postgresql://postgres:43cwB%2BscN%2Bhq25X@db.sxlrjdizbdwiumahezip.supabase.co:5432/postgres"

engine = sqlalchemy.create_engine(SUPABASE_URL)

UPLOAD_DIR = "storage"
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)

def init_db():
    with engine.begin() as conn:
        conn.execute(sqlalchemy.text('''
            CREATE TABLE IF NOT EXISTS anggota (
                id SERIAL PRIMARY KEY,
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
            )
        '''))

init_db()
st.title("Bank Data Anggota & KTP - F-SB SEMAR")

# --- SISTEM LOGIN ADMIN ---
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

st.sidebar.subheader("🔒 Status Akses")

if not st.session_state.logged_in:
    with st.sidebar.form("login_form"):
        st.write("Login Khusus Admin")
        username_input = st.text_input("Username")
        password_input = st.text_input("Password", type="password")
        submit_login = st.form_submit_button("Login")
        
        if submit_login:
            if username_input == "Marhaendra99" and password_input == "akira123#":
                st.session_state.logged_in = True
                st.success("Login Berhasil!")
                st.rerun()
            else:
                st.error("Username atau Password salah!")
    
    menu = []
else:
    st.sidebar.success("Status: Login sebagai Admin")
    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.rerun()
    
    menu = ["1. Input Data Anggota", "2. Data Semua Anggota", "3. Cari Data Anggota", "4. Hapus Data Anggota"]

if not st.session_state.logged_in:
    st.warning("⚠️ Silakan **Login** terlebih dahulu di sidebar sebelah kiri.")
    choice = ""
else:
    choice = st.sidebar.selectbox("Pilih Menu", menu)

# --- MENU 1: INPUT DATA ---
if choice == "1. Input Data Anggota" and st.session_state.logged_in:
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
            c.execute("""
                INSERT INTO anggota (nama, nik, telp, ttl, alamat, kel, kec, kota, prov, foto, status) 
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (nama, nik, telp, ttl, alamat, kel, kec, kota, prov, foto_path, status))
            conn.commit()
            conn.close()
            st.success(f"Data anggota atas nama {nama} berhasil disimpan!")

# --- MENU 2: LIHAT SEMUA DATA ---
elif choice == "2. Data Semua Anggota" and st.session_state.logged_in:
    st.subheader("Daftar Seluruh Anggota Terdaftar")
    conn = sqlite3.connect(DB_NAME)
    df = pd.read_sql("SELECT * FROM anggota", conn)
    conn.close()
    
    if not df.empty:
        df = df.reset_index(drop=True)
        df['id'] = range(1, len(df) + 1)
        st.dataframe(df, use_container_width=True)
    else:
        st.info("Belum ada data anggota yang tersimpan.")

# --- MENU 3: CARI DATA ---
elif choice == "3. Cari Data Anggota" and st.session_state.logged_in:
    st.subheader("Cari Data Anggota")
    cari = st.text_input("Masukkan nama atau NIK yang dicari")
    
    if cari:
        conn = sqlite3.connect(DB_NAME)
        df = pd.read_sql(f"SELECT * FROM anggota WHERE nama LIKE '%{cari}%' OR nik LIKE '%{cari}%'", conn)
        conn.close()
        
        if not df.empty:
            df = df.reset_index(drop=True)
            df['id'] = range(1, len(df) + 1)
            st.dataframe(df, use_container_width=True)
        else:
            st.warning("Data tidak ditemukan.")

# --- MENU 4: HAPUS DATA ANGGOTA ---
elif choice == "4. Hapus Data Anggota" and st.session_state.logged_in:
    st.subheader("Kelola & Hapus Data Anggota Tidak Aktif")
    conn = sqlite3.connect(DB_NAME)
    df = pd.read_sql("SELECT id, nama, nik, status FROM anggota", conn)
    conn.close()
    
    if not df.empty:
        st.info("💡 Centang baris anggota pada tabel di bawah ini untuk dihapus.")
        
        # Penomoran id di tabel hapus juga dirapikan mulai dari 1
        df = df.reset_index(drop=True)
        df['id'] = range(1, len(df) + 1)
        
        edited_df = st.data_editor(
            df.assign(Pilih=False),
            column_config={"Pilih": st.column_config.CheckboxColumn("Centang untuk Hapus", required=True)},
            disabled=["id", "nama", "nik", "status"],
            use_container_width=True
        )
        
        if st.button("Hapus Anggota yang Dicentang"):
            selected_rows = edited_df[edited_df["Pilih"] == True]
            if not selected_rows.empty:
                ids_to_delete = selected_rows["id"].tolist()
                
                # Mengambil ulang data asli dari database untuk mencocokkan baris yang benar
                conn = sqlite3.connect(DB_NAME)
                df_real = pd.read_sql("SELECT id, nama FROM anggota", conn)
                c = conn.cursor()
                
                # Hapus berdasarkan data yang dipilih melalui indeks yang sesuai
                for idx in selected_rows.index:
                    real_id = df_real.iloc[idx]['id']
                    c.execute("DELETE FROM anggota WHERE id = ?", (real_id,))
                
                conn.commit()
                conn.close()
                
                st.success("Berhasil menghapus data anggota yang dicentang!")
                st.rerun()
            else:
                st.warning("Belum ada data yang Anda centang pada tabel.")
    else:
        st.info("Belum ada data anggota yang tersimpan.")
        