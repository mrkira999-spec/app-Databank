import streamlit as st
import pandas as pd
import os
from supabase import create_client, Client

# --- PENGATURAN HALAMAN & TAMPILAN CYBERPUNK RED-BLACK ---
st.set_page_config(page_title="Bank Data F-SB SEMAR", page_icon="⚡", layout="wide")

st.markdown("""
    <style>
    /* Background Utama Hitam Pekat dengan Corak Cyberpunk Grid & Neon Merah/Biru */
    .stApp {
        background-color: #020205;
        background-image: 
            linear-gradient(rgba(255, 0, 51, 0.03) 1px, transparent 1px),
            linear-gradient(90deg, rgba(255, 0, 51, 0.03) 1px, transparent 1px),
            radial-gradient(circle at 10% 20%, rgba(255, 0, 51, 0.12) 0%, transparent 40%),
            radial-gradient(circle at 90% 80%, rgba(0, 102, 255, 0.08) 0%, transparent 40%);
        background-size: 30px 30px, 30px 30px, 100% 100%, 100% 100%;
        color: #ffffff;
        font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
        background-attachment: fixed;
    }
    
    /* Sidebar dengan Gradasi Hitam ke Merah Menyala */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #090305 0%, #1a0508 50%, #050203 100%);
        border-right: 2px solid #ff0033;
        box-shadow: 5px 0 25px rgba(255, 0, 51, 0.2);
    }

    /* Tombol Collapse / Panah Kecil Sidebar (<<) */
    [data-testid="collapsedControl"], button[kind="header"] {
        background: linear-gradient(135deg, #ff0033 0%, #660014 100%) !important;
        color: #000000 !important;
        border: 1px solid #ff4d6d !important;
        box-shadow: 0 0 10px rgba(255, 0, 51, 0.6);
    }
    [data-testid="collapsedControl"] svg {
        fill: #000000 !important;
    }

    /* Judul Utama dengan Gradasi Merah Menyala */
    h1 {
        font-weight: 900;
        background: linear-gradient(90deg, #ff0033, #ff7b93, #ffffff);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-shadow: 0px 0px 15px rgba(255, 0, 51, 0.4);
        letter-spacing: 1px;
    }
    
    /* Judul Sub-menu & Bagian Lain Warna Putih */
    h2, h3, h4, h5, h6 {
        color: #ffffff !important;
        font-weight: 700;
    }

    /* Kotak Kartu Statistik / Metric dengan Efek Cyber */
    div[data-testid="stMetric"] {
        background: linear-gradient(135deg, rgba(20, 5, 8, 0.9) 0%, rgba(10, 10, 15, 0.9) 100%);
        border: 1px solid rgba(255, 0, 51, 0.4);
        padding: 15px;
        border-radius: 8px;
        box-shadow: 0 0 15px rgba(255, 0, 51, 0.15);
        backdrop-filter: blur(5px);
    }
    div[data-testid="stMetric"] label {
        color: #9ca3af !important;
    }
    div[data-testid="stMetric"] div[data-testid="stMetricValue"] {
        color: #ff334b !important;
        font-weight: bold;
        text-shadow: 0 0 8px rgba(255, 51, 75, 0.4);
    }

    /* Tombol Utama (Gradasi Merah Cyberpunk) */
    .stButton>button {
        background: linear-gradient(135deg, #cc0000 0%, #ff0033 100%);
        color: white;
        border-radius: 6px;
        padding: 0.5rem 1rem;
        font-weight: bold;
        border: 1px solid #ff6680;
        box-shadow: 0 0 12px rgba(255, 0, 51, 0.4);
        transition: 0.2s ease;
    }
    .stButton>button:hover {
        background: linear-gradient(135deg, #ff0033 0%, #ff4d6d 100%);
        box-shadow: 0 0 20px rgba(255, 0, 51, 0.8);
        color: white;
    }

    /* KOTAK INPUT & FORM LOGIN (Wajib Putih Terang & Jelas) */
    .stTextInput input, .stTextArea textarea {
        background-color: rgba(12, 12, 18, 0.95) !important;
        color: #ffffff !important;
        border: 1px solid rgba(255, 0, 51, 0.3) !important;
        border-radius: 6px !important;
    }
    
    .stTextInput input:focus, .stTextArea textarea:focus {
        border-color: #ff0033 !important;
        box-shadow: 0 0 12px rgba(255, 0, 51, 0.6) !important;
        color: #ffffff !important;
    }

    /* Label Formulir & Input Berwarna Putih Bersih */
    .stTextInput label, .stTextArea label, .stSelectbox label, .stFileUploader label {
        color: #ffffff !important;
        font-weight: 500;
    }

    /* Dropdown Selectbox */
    .stSelectbox div[data-baseweb="select"] {
        background-color: rgba(12, 12, 18, 0.95) !important;
        color: #ffffff !important;
        border: 1px solid rgba(255, 0, 51, 0.3) !important;
        border-radius: 6px !important;
    }
    
    /* Placeholder teks di dalam input */
    ::placeholder {
        color: #6b7280 !important;
        opacity: 1;
    }

    /* Kotak Peringatan & Info */
    .stAlert {
        background-color: rgba(15, 5, 8, 0.9);
        color: #ffffff;
        border: 1px solid rgba(255, 0, 51, 0.4);
    }
    </style>
""", unsafe_allow_html=True)

# Mengambil konfigurasi dari Streamlit Secrets
SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

UPLOAD_DIR = "storage"
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)

st.title("⚡ BANK DATA ANGGOTA & KTP — F-SB SEMAR")
st.markdown("---")

# --- SISTEM LOGIN ADMIN ---
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

st.sidebar.subheader("🔒 Panel Admin")

if not st.session_state.logged_in:
    with st.sidebar.form("login_form"):
        st.write("Silakan Login Terlebih Dahulu")
        username_input = st.text_input("Username")
        password_input = st.text_input("Password", type="password")
        submit_login = st.form_submit_button("Masuk Sistem")
        
        if submit_login:
            if username_input == "Marhaendra99" and password_input == "akira123#":
                st.session_state.logged_in = True
                st.success("Login Berhasil!")
                st.rerun()
            else:
                st.error("Username/Password salah!")
    
    choice = ""
else:
    st.sidebar.success("Status: Terhubung (Admin)")
    if st.sidebar.button("Keluar (Logout)"):
        st.session_state.logged_in = False
        st.rerun()
    
    menu = ["1. Input Data Anggota", "2. Data Semua Anggota", "3. Cari Data Anggota", "4. Hapus Data Anggota"]
    choice = st.sidebar.selectbox("📂 Pilih Menu Utama", menu)

if not st.session_state.logged_in:
    st.warning("⚠️ Akses dibatasi. Silakan **Login** melalui panel di sidebar sebelah kiri untuk mengelola data.")
else:
    # --- MENU 1: INPUT DATA ---
    if choice == "1. Input Data Anggota":
        st.subheader("📝 Formulir Pendaftaran Anggota Baru")
        st.markdown("Lengkapi formulir di bawah ini dengan data yang valid.")
        
        with st.form("form_tambah", clear_on_submit=True):
            col1, col2 = st.columns(2)
            with col1:
                nama = st.text_input("Nama Lengkap*")
                nik = st.text_input("NIK*")
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

            st.markdown("")
            submit = st.form_submit_button("💾 Simpan Data Anggota")

        if submit:
            if not nama or not nik or not alamat or not kel or not kec or not kota or not prov:
                st.warning("Mohon lengkapi kolom bertanda bintang (*), termasuk NIK!")
            else:
                cek_nik = supabase.table("anggota").select("nik").eq("nik", nik).execute()
                
                if len(cek_nik.data) > 0:
                    st.error(f"❌ Gagal menyimpan: NIK '{nik}' sudah terdaftar di dalam database!")
                else:
                    foto_path = ""
                    if foto is not None:
                        foto_path = os.path.join(UPLOAD_DIR, foto.name)
                        with open(foto_path, "wb") as f:
                            f.write(foto.getbuffer())

                    data_baru = {
                        "nama": nama, "nik": nik, "telp": telp, "ttl": ttl, 
                        "alamat": alamat, "kel": kel, "kec": kec, "kota": kota, 
                        "prov": prov, "foto": foto_path, "status": status
                    }
                    
                    supabase.table("anggota").insert(data_baru).execute()
                    st.success(f"✨ Data anggota atas nama **{nama}** berhasil disimpan!")

    # --- MENU 2: LIHAT SEMUA DATA ---
    elif choice == "2. Data Semua Anggota":
        st.subheader("📋 Daftar Seluruh Anggota Terdaftar")
        
        response = supabase.table("anggota").select("*").execute()
        data = response.data
        
        if data:
            df = pd.DataFrame(data)
            
            total_anggota = len(df)
            total_aktif = len(df[df['status'] == 'Aktif']) if 'status' in df.columns else 0
            
            col_m1, col_m2 = st.columns(2)
            with col_m1:
                st.metric(label="👥 Total Seluruh Anggota", value=total_anggota)
            with col_m2:
                st.metric(label="🟢 Anggota Berstatus Aktif", value=total_aktif)
            
            st.markdown("---")
            
            if 'nama' in df.columns:
                df = df.sort_values(by='nama', ascending=True)
            
            df = df.reset_index(drop=True)
            df['id_tampil'] = range(1, len(df) + 1)
            
            df['Keterangan_NIK'] = df['nik'].apply(lambda x: '⚠️ DOBEL / KEMBAR' if df['nik'].duplicated(keep=False)[df['nik'] == x].any() else 'Normal')
            
            cols = ['id_tampil', 'Keterangan_NIK'] + [col for col in df.columns if col not in ['id_tampil', 'Keterangan_NIK']]
            df = df[cols]
            
            st.info("💡 Kolom **Keterangan_NIK** mendeteksi otomatis jika ada data ganda.")
            st.dataframe(df, use_container_width=True)
        else:
            st.info("Belum ada data anggota yang tersimpan di Supabase.")

    # --- MENU 3: CARI DATA ---
    elif choice == "3. Cari Data Anggota":
        st.subheader("🔍 Pencarian Data Anggota")
        cari = st.text_input("Ketik nama lengkap atau nomor NIK...")
        
        if cari:
            response = supabase.table("anggota").select("*").or_(f"nama.ilike.%{cari}%,nik.ilike.%{cari}%").execute()
            data = response.data
            
            if data:
                df = pd.DataFrame(data)
                df = df.sort_values(by='nama', ascending=True).reset_index(drop=True)
                df['id_tampil'] = range(1, len(df) + 1)
                st.success(f"Ditemukan {len(df)} data yang cocok.")
                st.dataframe(df, use_container_width=True)
            else:
                st.warning("Data tidak ditemukan.")

    # --- MENU 4: HAPUS DATA ANGGOTA ---
    elif choice == "4. Hapus Data Anggota":
        st.subheader("🗑️ Kelola & Hapus Data Anggota")
        st.markdown("Gunakan menu ini untuk membersihkan data ganda atau anggota yang tidak aktif.")
        
        response = supabase.table("anggota").select("id, nama, nik, status").execute()
        data = response.data
        
        if data:
            df = pd.DataFrame(data)
            df = df.sort_values(by='nama', ascending=True).reset_index(drop=True)
            
            df['no_tampil'] = range(1, len(df) + 1)
            cols = ['no_tampil'] + [col for col in df.columns if col != 'no_tampil']
            df = df[cols]
            
            edited_df = st.data_editor(
                df.assign(Pilih=False),
                column_config={"Pilih": st.column_config.CheckboxColumn("Centang untuk Hapus", required=True)},
                disabled=["no_tampil", "id", "nama", "nik", "status"],
                use_container_width=True
            )
            
            st.markdown("")
            if st.button("🗑️ Hapus Anggota yang Dicentang"):
                selected_rows = edited_df[edited_df["Pilih"] == True]
                if not selected_rows.empty:
                    for idx, row in selected_rows.iterrows():
                        supabase.table("anggota").delete().eq("id", row["id"]).execute()
                    
                    st.success("Berhasil menghapus data yang dipilih dari database!")
                    st.rerun()
                else:
                    st.warning("Belum ada data yang Anda centang pada tabel.")
        else:
            st.info("Belum ada data anggota di Supabase.")
