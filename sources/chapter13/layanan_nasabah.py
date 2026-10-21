"""Layanan nasabah, pemilik tunggal berkas data/nasabah.db.

Layanan ini menyimpan identitas nasabah saja, yaitu nomor, nama, dan kota.
Tabel pesanan dan tabel kurs berada di berkas milik layanan lain, dan layanan
ini tidak pernah membukanya. Karena itu tidak ada satu pun kueri di sini yang
menyebut nama tabel milik layanan lain.

Aturan bisnis yang dijalankan layanan ini adalah penyembunyian nomor rekening.
Nomor rekening lengkap hanya diberikan kepada pemanggil yang menyertakan token
petugas, sedangkan pemanggil lain menerima bentuk tersamar. Aturan itu tinggal
di sini, sebab hanya layanan ini yang memegang datanya.

Cara menjalankan: python layanan_nasabah.py
"""

import logging

import flask

import alamat
import basis_data

SKEMA = """CREATE TABLE IF NOT EXISTS nasabah (
  id TEXT PRIMARY KEY,
  nama TEXT NOT NULL,
  kota TEXT NOT NULL,
  rekening TEXT NOT NULL
)"""

SISIPKAN = ("INSERT OR REPLACE INTO nasabah (id, nama, kota, rekening) "
            "VALUES (?, ?, ?, ?)")

ISI_AWAL = [
  ("N-001", "Rani Prameswari", "Tangerang", "8820341577"),
  ("N-002", "Bagas Nugroho", "Surabaya", "8820349013"),
  ("N-003", "Sekar Ayu Larasati", "Makassar", "8820352268"),
]

KUERI_SATU_NASABAH = "SELECT id, nama, kota, rekening FROM nasabah WHERE id = ?"

TABEL_NASABAH = basis_data.Tabel(SKEMA, SISIPKAN, ISI_AWAL)
BASIS_DATA = basis_data.BasisDataLayanan("nasabah.db", [TABEL_NASABAH])

TOKEN_PETUGAS = "petugas-13"
JUMLAH_DIGIT_TAMPAK = 4

aplikasi = flask.Flask(__name__)


def samarkan_rekening(rekening: str, token: str | None) -> str:
  """Menyembunyikan sebagian nomor rekening bagi pemanggil tanpa token petugas.

  Aturan ini milik layanan nasabah, bukan milik gerbang, sebab hanya layanan
  ini yang tahu kolom mana yang peka. Mengembalikan str berisi nomor rekening
  utuh untuk petugas, atau bentuk tersamar untuk pemanggil lain.
  """
  if token == TOKEN_PETUGAS:
    return rekening
  return "*" * (len(rekening) - JUMLAH_DIGIT_TAMPAK) + rekening[-JUMLAH_DIGIT_TAMPAK:]


@aplikasi.get("/sehat")
def periksa_sehat():
  """Menjawab pemeriksaan kesiapan dari skrip penjalan dan skrip pengukuran.

  Jawaban ini dipakai untuk menentukan kapan sebuah layanan benar-benar siap
  menerima permintaan sesudah dinyalakan. Mengembalikan dict berisi nama
  layanan beserta penanda sehat.
  """
  return {"layanan": "nasabah", "sehat": True}


@aplikasi.get("/nasabah/<id_nasabah>")
def ambil_nasabah(id_nasabah: str):
  """Memberikan satu nasabah beserta nomor rekening sesuai hak pemanggilnya.

  Token dibaca dari kepala permintaan, lalu dipakai menentukan bentuk nomor
  rekening yang boleh keluar. Mengembalikan dict berisi data nasabah, atau dict
  galat beserta kode 404 bila nomornya tidak ada.
  """
  baris = BASIS_DATA.baca(KUERI_SATU_NASABAH, (id_nasabah,))
  if not baris:
    return {"galat": f"nasabah {id_nasabah} tidak ada"}, 404
  nomor, nama, kota, rekening = baris[0]
  token = flask.request.headers.get("X-Token")
  return {"id": nomor, "nama": nama, "kota": kota,
          "rekening": samarkan_rekening(rekening, token)}


if __name__ == "__main__":
  logging.getLogger("werkzeug").setLevel(logging.ERROR)
  BASIS_DATA.siapkan()
  aplikasi.run(port=alamat.PORTA_NASABAH, threaded=True)
