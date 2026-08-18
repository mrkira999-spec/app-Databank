import os
import uuid
import requests
from typing import Optional
from fastapi import FastAPI, UploadFile, File, Form, Depends
from sqlalchemy import create_engine, Column, String, Text, DateTime, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session

# Konfigurasi Database SQLite Lokal
SQLALCHEMY_DATABASE_URL = "sqlite:///./bank_data_db.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class Anggota(Base):
    __tablename__ = "anggota"
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tanggal_input = Column(DateTime(timezone=True), server_default=func.now())
    nik = Column(String(50), nullable=True)
    nama_lengkap = Column(String(255), nullable=False, index=True)
    alamat = Column(Text, nullable=False)
    no_telepon = Column(String(20))
    tempat_tgl_lahir = Column(String(100))
    kelurahan = Column(String(100))
    kecamatan = Column(String(100), index=True)
    kota_kabupaten = Column(String(100), index=True)
    provinsi = Column(String(100), index=True)
    foto_ktp_path = Column(Text, nullable=True)

Base.metadata.create_all(bind=engine)
app = FastAPI()

# Folder penyimpanan foto KTP lokal
STORAGE_DIR = "storage/secure_ktp"
os.makedirs(STORAGE_DIR, exist_ok=True)

def get_db():
    db = SessionLocal()
    try: yield db
    finally: db.close()

def simpan_ke_gsheets(data_anggota):
    url = "https://script.google.com/macros/s/AKfycbxA0iQsmyfwRHqh_Z_zZ7inf8kAgIZfk7jINYB4KIFrBbgGStPVoPBDPRnpFZHeJ7PErg/exec"
    try:
        requests.post(url, json=data_anggota)
    except Exception as e:
        print(f"Gagal sync ke Sheets: {e}")

@app.post("/anggota/")
def tambah_anggota(
    nama_lengkap: str = Form(...), alamat: str = Form(...), kelurahan: str = Form(...), 
    kecamatan: str = Form(...), kota_kabupaten: str = Form(...), provinsi: str = Form(...), 
    nik: Optional[str] = Form(""), no_telepon: Optional[str] = Form(None), 
    tempat_tgl_lahir: Optional[str] = Form(None), foto_ktp: Optional[UploadFile] = File(None), 
    db: Session = Depends(get_db)
):
    file_path = None
    if foto_ktp and foto_ktp.filename:
        file_ext = foto_ktp.filename.split(".")[-1]
        secure_filename = f"{uuid.uuid4()}.{file_ext}"
        file_path = os.path.join(STORAGE_DIR, secure_filename)
        with open(file_path, "wb") as f: 
            f.write(foto_ktp.file.read())
    
    new_anggota = Anggota(
        nik=nik or "", nama_lengkap=nama_lengkap, alamat=alamat, no_telepon=no_telepon or "",
        tempat_tgl_lahir=tempat_tgl_lahir or "", kelurahan=kelurahan, kecamatan=kecamatan, 
        kota_kabupaten=kota_kabupaten, provinsi=provinsi, foto_ktp_path=file_path
    )
    db.add(new_anggota)
    db.commit()
    
    # Kirim salinan data ke Google Sheets secara otomatis
    simpan_ke_gsheets({
        "tanggal_input": str(new_anggota.tanggal_input),
        "nik": new_anggota.nik,
        "nama_lengkap": new_anggota.nama_lengkap,
        "no_telepon": new_anggota.no_telepon,
        "tempat_tgl_lahir": new_anggota.tempat_tgl_lahir,
        "alamat_lengkap": f"{new_anggota.alamat}, Kel. {new_anggota.kelurahan}, Kec. {new_anggota.kecamatan}, Kab/Kota {new_anggota.kota_kabupaten}, Prov. {new_anggota.provinsi}"
    })

    return {"status": "success", "id": new_anggota.id}

@app.get("/anggota/all")
def ambil_semua_anggota(db: Session = Depends(get_db)):
    results = db.query(Anggota).order_by(Anggota.tanggal_input.desc()).all()
    return [{
        "id": str(item.id),
        "tanggal_input": item.tanggal_input.strftime("%Y-%m-%d %H:%M:%S"),
        "nik": item.nik,
        "nama_lengkap": item.nama_lengkap,
        "alamat_lengkap": f"{item.alamat}, Kel. {item.kelurahan}, Kec. {item.kecamatan}, Kab/Kota {item.kota_kabupaten}, Prov. {item.provinsi}",
        "no_telepon": item.no_telepon,
        "tempat_tgl_lahir": item.tempat_tgl_lahir,
        "status_ktp": "Ada Foto" if item.foto_ktp_path else "Tidak Ada",
        "foto_path": item.foto_ktp_path
    } for item in results]

@app.get("/anggota/search")
def cari_anggota(q: Optional[str] = None, wilayah: Optional[str] = None, db: Session = Depends(get_db)):
    query = db.query(Anggota)
    if q:
        query = query.filter((Anggota.nama_lengkap.contains(q)) | (Anggota.nik.contains(q)))
    if wilayah:
        query = query.filter((Anggota.kota_kabupaten.contains(wilayah)) | (Anggota.kecamatan.contains(wilayah)) | (Anggota.provinsi.contains(wilayah)))
    
    results = query.order_by(Anggota.tanggal_input.desc()).all()
    return [{
        "id": str(item.id),
        "tanggal_input": item.tanggal_input.strftime("%Y-%m-%d %H:%M:%S"),
        "nik": item.nik,
        "nama_lengkap": item.nama_lengkap,
        "alamat_lengkap": f"{item.alamat}, Kel. {item.kelurahan}, Kec. {item.kecamatan}, Kab/Kota {item.kota_kabupaten}, Prov. {item.provinsi}",
        "no_telepon": item.no_telepon,
        "tempat_tgl_lahir": item.tempat_tgl_lahir,
        "status_ktp": "Ada Foto" if item.foto_ktp_path else "Tidak Ada",
        "foto_path": item.foto_ktp_path
    } for item in results]

@app.delete("/anggota/{anggota_id}")
def hapus_anggota(anggota_id: str, db: Session = Depends(get_db)):
    item = db.query(Anggota).filter(Anggota.id == anggota_id).first()
    if item:
        if item.foto_ktp_path and os.path.exists(item.foto_ktp_path): 
            os.remove(item.foto_ktp_path)
        db.delete(item)
        db.commit()
    return {"status": "ok"}
