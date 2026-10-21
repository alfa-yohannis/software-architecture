"""Layanan kurs, pemilik tunggal berkas data/kurs.db.

Layanan ini menyimpan kurs dasar beserta margin keuntungan bank. Angka dasarnya
mengikuti contoh Bab 2, yang meniru kurs acuan Bank Indonesia. Kurs jual dihitung
di sini, bukan di gerbang, sebab besar marginnya adalah aturan bank dan bukan
urusan penyusun laporan.

Layanan ini paling sering berubah di antara ketiganya, sebab kurs diperbarui
setiap hari kerja. Justru karena itulah layanan ini dipakai sebagai bahan
percobaan rilis pada Latihan 3.

Cara menjalankan: python layanan_kurs.py
"""

import logging

import flask

import alamat
import basis_data

SKEMA = """CREATE TABLE IF NOT EXISTS kurs (
  mata_uang TEXT PRIMARY KEY,
  dasar REAL NOT NULL,
  margin REAL NOT NULL
)"""

SISIPKAN = "INSERT OR REPLACE INTO kurs (mata_uang, dasar, margin) VALUES (?, ?, ?)"

ISI_AWAL = [
  ("USD", 16250.0, 75.0),
  ("EUR", 17600.0, 90.0),
  ("SGD", 12100.0, 60.0),
]

KUERI_SATU_KURS = "SELECT mata_uang, dasar, margin FROM kurs WHERE mata_uang = ?"

TABEL_KURS = basis_data.Tabel(SKEMA, SISIPKAN, ISI_AWAL)
BASIS_DATA = basis_data.BasisDataLayanan("kurs.db", [TABEL_KURS])

aplikasi = flask.Flask(__name__)


def hitung_jual(dasar: float, margin: float) -> float:
  """Menjumlahkan kurs dasar dengan margin keuntungan bank.

  Perhitungan ini sengaja tidak dikirim ke pemanggil dalam bentuk dua angka
  terpisah, agar margin bank tidak bocor ke luar layanan. Mengembalikan float
  berisi kurs jual dalam rupiah.
  """
  return dasar + margin


@aplikasi.get("/sehat")
def periksa_sehat():
  """Menjawab pemeriksaan kesiapan dari skrip penjalan dan skrip pengukuran.

  Jawaban ini dipakai untuk menentukan kapan sebuah layanan benar-benar siap
  menerima permintaan sesudah dinyalakan. Mengembalikan dict berisi nama
  layanan beserta penanda sehat.
  """
  return {"layanan": "kurs", "sehat": True}


@aplikasi.get("/kurs/<mata_uang>")
def ambil_kurs(mata_uang: str):
  """Memberikan kurs jual satu mata uang tanpa membuka margin banknya.

  Hanya satu mata uang dilayani setiap panggilan, sehingga penyusun laporan
  memanggil layanan ini sekali per mata uang yang benar-benar dipakai.
  Mengembalikan dict berisi mata uang beserta kurs jualnya, atau dict galat
  beserta kode 404 bila mata uangnya belum terdaftar.
  """
  baris = BASIS_DATA.baca(KUERI_SATU_KURS, (mata_uang.upper(),))
  if not baris:
    return {"galat": f"kurs {mata_uang} tidak ada"}, 404
  kode, dasar, margin = baris[0]
  return {"mata_uang": kode, "jual": hitung_jual(dasar, margin)}


if __name__ == "__main__":
  logging.getLogger("werkzeug").setLevel(logging.ERROR)
  BASIS_DATA.siapkan()
  aplikasi.run(port=alamat.PORTA_KURS, threaded=True)
