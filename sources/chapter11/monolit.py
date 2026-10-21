"""Versi monolit, yaitu ketiga bidang domain di dalam satu proses.

Seluruh jalur permintaan dilayani proses ini sendiri. Pemanggilan antar
bidang berupa pemanggilan fungsi biasa, sehingga tidak ada satu pun lompatan
jaringan di dalam sistem. Jalur permintaan, bentuk jawaban, dan aturan
bisnisnya sama persis dengan versi service-based, agar yang dibandingkan
benar-benar letak prosesnya.

Cara menjalankan:
  python basis_data.py
  python monolit.py
  curl http://127.0.0.1:8000/pesanan/1
"""

from flask import Flask

import alamat
import domain_kurs
import domain_pemesanan
import domain_penagihan
import sarana

aplikasi = Flask(__name__)
sarana.pasang_penangan_galat(aplikasi)


@aplikasi.get("/sehat")
def periksa_sehat() -> dict:
  """Menyatakan bahwa proses ini sudah siap menerima permintaan.

  Dipakai skrip penjalan untuk menunggu proses benar-benar hidup sebelum
  pengukuran dimulai. Mengembalikan dict berisi status dan nama versinya.
  """
  return {"status": "sehat", "versi": "monolit"}


@aplikasi.get("/kurs/<kode>")
def baca_kurs(kode: str) -> dict:
  """Melayani permintaan nilai tukar satu mata uang.

  Mengembalikan dict berisi kode, nilai, dan jumlah lompatan jaringan yang
  dipakai permintaan ini, yaitu satu lompatan dari klien saja.
  """
  hasil = domain_kurs.ambil_kurs(kode)
  hasil["lompatan"] = alamat.LOMPATAN_KLIEN
  return hasil


@aplikasi.get("/pesanan/<int:nomor>")
def baca_pesanan(nomor: int) -> dict:
  """Melayani permintaan satu pesanan beserta statusnya.

  Mengembalikan dict berisi data pesanan ditambah kunci lompatan, sehingga
  bentuk jawabannya sama dengan jawaban gerbang pada versi service-based.
  """
  hasil = domain_pemesanan.ambil_pesanan(nomor)
  hasil["lompatan"] = alamat.LOMPATAN_KLIEN
  return hasil


@aplikasi.get("/tagihan/<int:nomor>")
def baca_tagihan(nomor: int) -> dict:
  """Melayani permintaan tagihan yang sudah pernah diterbitkan.

  Mengembalikan dict berisi data tagihan ditambah kunci lompatan.
  """
  hasil = domain_penagihan.ambil_tagihan(nomor)
  hasil["lompatan"] = alamat.LOMPATAN_KLIEN
  return hasil


@aplikasi.post("/pesanan/<int:nomor>/tagihan")
def terbitkan_tagihan(nomor: int) -> dict:
  """Melayani permintaan gabungan yang menyentuh ketiga bidang sekaligus.

  Ketiga bidang dipanggil sebagai fungsi biasa, yaitu membaca pesanan,
  membaca kurs, lalu menerbitkan tagihannya. Mengembalikan dict berisi
  pesanan, kurs, tagihan, dan jumlah lompatan jaringannya.
  """
  pesanan = domain_pemesanan.ambil_pesanan(nomor)
  kurs = domain_kurs.ambil_kurs(pesanan["mata_uang"])
  tagihan = domain_penagihan.terbitkan_tagihan(nomor, kurs["nilai"])
  return {
    "pesanan": pesanan,
    "kurs": kurs,
    "tagihan": tagihan,
    "lompatan": alamat.LOMPATAN_KLIEN,
  }


if __name__ == "__main__":
  sarana.redam_catatan_web()
  aplikasi.run(host=alamat.TUAN_RUMAH, port=alamat.PORTA_MONOLIT,
               threaded=True)
