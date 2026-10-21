"""Layanan domain pemesanan pada versi service-based.

Proses ini hanya memuat bidang pemesanan. Tabel pesanan yang dibacanya
berada di berkas basis data yang sama dengan kedua layanan lain, sehingga
pemisahan prosesnya tidak diikuti pemisahan datanya.

Cara menjalankan:
  python basis_data.py
  python layanan_pemesanan.py
  curl http://127.0.0.1:8102/pesanan/1
"""

from flask import Flask

import alamat
import domain_pemesanan
import sarana

aplikasi = Flask(__name__)
sarana.pasang_penangan_galat(aplikasi)


@aplikasi.get("/sehat")
def periksa_sehat() -> dict:
  """Menyatakan bahwa layanan pemesanan sudah siap menerima permintaan.

  Mengembalikan dict berisi status dan nama layanannya, dipakai skrip
  penjalan sebagai tanda bahwa portanya sudah terbuka.
  """
  return {"status": "sehat", "layanan": "pemesanan"}


@aplikasi.get("/pesanan/<int:nomor>")
def baca_pesanan(nomor: int) -> dict:
  """Melayani permintaan satu pesanan dari gerbang.

  Mengembalikan dict berisi data pesanan beserta satu lompatan jaringan
  yang dipakai gerbang untuk sampai ke layanan ini.
  """
  hasil = domain_pemesanan.ambil_pesanan(nomor)
  hasil["lompatan"] = alamat.LOMPATAN_LAYANAN
  return hasil


if __name__ == "__main__":
  sarana.redam_catatan_web()
  aplikasi.run(host=alamat.TUAN_RUMAH, port=alamat.PORTA_PEMESANAN,
               threaded=True)
