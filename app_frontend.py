import streamlit as st
import pandas as pd
import os
from supabase import create_client, Client

# Mengambil konfigurasi dari Streamlit Secrets
SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

UPLOAD_DIR = "storage"
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)

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
    
    choice = ""
else:
    st.sidebar.success("Status: Login sebagai Admin")
    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.rerun()
    
    menu = ["1. Input Data Anggota", "2. Data Semua Anggota", "3. Cari Data Anggota", "4. Hapus Data Anggota"]
    choice = st.sidebar.selectbox("Pilih Menu", menu)

if not st.session_state.logged_in:
    st.warning("⚠️ Silakan **Login** terlebih dahulu di sidebar sebelah kiri.")
else:
    # --- MENU 1: INPUT DATA ---
    if choice == "1. Input Data Anggota":
        st.subheader("Formulir Pendaftaran Anggota Baru")
        
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

            submit = st.form_submit_button("Simpan Data Anggota")

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
                    st.success(f"Data anggota atas nama {nama} berhasil disimpan ke Supabase!")

    # --- MENU 2: LIHAT SEMUA DATA ---
    elif choice == "2. Data Semua Anggota":
        st.subheader("Daftar Seluruh Anggota Terdaftar")
        
        response = supabase.table("anggota").select("*").execute()
        data = response.data
        
        if data:
            df = pd.DataFrame(data)
            df = df.reset_index(drop=True)
            df['id'] = range(1, len(df) + 1)
            st.dataframe(df, use_container_width=True)
        else:
            st.info("Belum ada data anggota yang tersimpan di Supabase.")

    # --- MENU 3: CARI DATA ---
    elif choice == "3. Cari Data Anggota":
        st.subheader("Cari Data Anggota")
        cari = st.text_input("Masukkan nama atau NIK yang dicari")
        
        if cari:
            response = supabase.table("anggota").select("*").or_(f"nama.ilike.%{cari}%,nik.ilike.%{cari}%").execute()
            data = response.data
            
            if data:
                df = pd.DataFrame(data)
                df = df.reset_index(drop=True)
                df['id'] = range(1, len(df) + 1)
                st.dataframe(df, use_container_width=True)
            else:
                st.warning("Data tidak ditemukan.")

    # --- MENU 4: HAPUS DATA ANGGOTA ---
    elif choice == "4. Hapus Data Anggota":
        st.subheader("Kelola & Hapus Data Anggota Tidak Aktif")
        
        response = supabase.table("anggota").select("id, nama, nik, status").execute()
        data = response.data
        
        if data:
            df = pd.DataFrame(data)
            st.info("💡 Centang baris anggota pada tabel di bawah ini untuk dihapus.")
            
            df = df.reset_index(drop=True)
            df['no_tampil'] = range(1, len(df) + 1)
            
            cols = ['no_tampil'] + [col for col in df.columns if col != 'no_tampil']
            df = df[cols]
            
            edited_df = st.data_editor(
                df.assign(Pilih=False),
                column_config={"Pilih": st.column_config.CheckboxColumn("Centang untuk Hapus", required=True)},
                disabled=["no_tampil", "id", "nama", "nik", "status"],
                use_container_width=True
            )
            
            if st.button("Hapus Anggota yang Dicentang"):
                selected_rows = edited_df[edited_df["Pilih"] == True]
                if not selected_rows.empty:
                    for idx, row in selected_rows.iterrows():
                        supabase.table("anggota").delete().eq("id", row["id"]).execute()
                    
                    st.success("Berhasil menghapus data yang dicentang dari Supabase!")
                    st.rerun()
                else:
                    st.warning("Belum ada data yang Anda centang pada tabel.")
        else:
            st.info("Belum ada data anggota di Supabase.")
