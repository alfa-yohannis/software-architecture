"""Layanan pesanan, pemilik tunggal berkas data/pesanan.db.

Layanan ini menyimpan pesanan penukaran valuta asing. Kolom id_nasabah memang
memuat nomor nasabah, tetapi layanan ini tidak pernah membuka data/nasabah.db
untuk memeriksanya. Nomor itu diperlakukan sebagai penanda saja, dan pemeriksaan
namanya menjadi urusan pemanggil yang menggabungkan keduanya.

Aturan bisnis yang dijalankan layanan ini adalah penolakan pesanan yang belum
lunas. Pesanan berstatus batal tidak ikut dikeluarkan, sebab laporan penukaran
tidak boleh memuatnya.

Cara menjalankan: python layanan_pesanan.py
"""

import logging

import flask

import alamat
import basis_data

SKEMA = """CREATE TABLE IF NOT EXISTS pesanan (
  id TEXT PRIMARY KEY,
  id_nasabah TEXT NOT NULL,
  mata_uang TEXT NOT NULL,
  nominal REAL NOT NULL,
  status TEXT NOT NULL
)"""

SISIPKAN = ("INSERT OR REPLACE INTO pesanan "
            "(id, id_nasabah, mata_uang, nominal, status) VALUES (?, ?, ?, ?, ?)")

ISI_AWAL = [
  ("P-1001", "N-001", "USD", 250.0, "lunas"),
  ("P-1002", "N-001", "SGD", 400.0, "lunas"),
  ("P-1003", "N-001", "USD", 150.0, "lunas"),
  ("P-1004", "N-001", "EUR", 120.0, "batal"),
  ("P-1005", "N-002", "EUR", 300.0, "lunas"),
  ("P-1006", "N-003", "SGD", 180.0, "lunas"),
]

STATUS_SAH = "lunas"

KUERI_PESANAN_NASABAH = (
  "SELECT id, id_nasabah, mata_uang, nominal FROM pesanan "
  "WHERE id_nasabah = ? AND status = ? ORDER BY id")

TABEL_PESANAN = basis_data.Tabel(SKEMA, SISIPKAN, ISI_AWAL)
BASIS_DATA = basis_data.BasisDataLayanan("pesanan.db", [TABEL_PESANAN])

aplikasi = flask.Flask(__name__)


def bentuk_baris(baris: tuple) -> dict:
  """Mengubah satu baris hasil kueri menjadi bentuk yang dikirim lewat HTTP.

  Bentuk luar sengaja dipisahkan dari bentuk tabel, sehingga nama kolom boleh
  berubah tanpa memaksa pemanggilnya ikut berubah. Mengembalikan dict berisi
  satu pesanan.
  """
  nomor, id_nasabah, mata_uang, nominal = baris
  return {"id": nomor, "id_nasabah": id_nasabah, "mata_uang": mata_uang,
          "nominal": nominal}


@aplikasi.get("/sehat")
def periksa_sehat():
  """Menjawab pemeriksaan kesiapan dari skrip penjalan dan skrip pengukuran.

  Jawaban ini dipakai untuk menentukan kapan sebuah layanan benar-benar siap
  menerima permintaan sesudah dinyalakan. Mengembalikan dict berisi nama
  layanan beserta penanda sehat.
  """
  return {"layanan": "pesanan", "sehat": True}


@aplikasi.get("/pesanan")
def ambil_pesanan():
  """Memberikan seluruh pesanan lunas milik satu nasabah.

  Pesanan berstatus batal disaring di sini, bukan di gerbang, sebab arti status
  itu hanya dipahami layanan pemilik datanya. Mengembalikan dict berisi nomor
  nasabah beserta list pesanan, atau dict galat beserta kode 400 bila nomor
  nasabahnya tidak disertakan.
  """
  id_nasabah = flask.request.args.get("nasabah")
  if not id_nasabah:
    return {"galat": "parameter nasabah wajib diisi"}, 400
  baris = BASIS_DATA.baca(KUERI_PESANAN_NASABAH, (id_nasabah, STATUS_SAH))
  return {"id_nasabah": id_nasabah, "pesanan": [bentuk_baris(b) for b in baris]}


if __name__ == "__main__":
  logging.getLogger("werkzeug").setLevel(logging.ERROR)
  BASIS_DATA.siapkan()
  aplikasi.run(port=alamat.PORTA_PESANAN, threaded=True)
