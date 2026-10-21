"""Layanan domain penagihan pada versi service-based.

Proses ini memuat bidang penagihan, yaitu aturan yang menghitung nilai rupiah
sebuah pesanan beserta pajaknya. Nilai kurs tidak dicari sendiri, melainkan
diterima sebagai parameter dari gerbang, sebab layanan ini tidak berhak
menebak kurs mana yang berlaku.

Bidang penagihan tetap membaca tabel pesanan langsung dari basis data
bersama. Pembacaan itulah yang membedakan service-based architecture dari
mikroservis, sebab mikroservis memisahkan basis datanya sehingga data pesanan
hanya dapat diminta lewat antarmuka layanan pemesanan.

Cara menjalankan:
  python basis_data.py
  python layanan_penagihan.py
  curl http://127.0.0.1:8103/tagihan/1
"""

from flask import Flask, request

import alamat
import domain_penagihan
import kesalahan
import sarana

aplikasi = Flask(__name__)
sarana.pasang_penangan_galat(aplikasi)


@aplikasi.get("/sehat")
def periksa_sehat() -> dict:
  """Menyatakan bahwa layanan penagihan sudah siap menerima permintaan.

  Mengembalikan dict berisi status dan nama layanannya, dipakai skrip
  penjalan sebagai tanda bahwa portanya sudah terbuka.
  """
  return {"status": "sehat", "layanan": "penagihan"}


@aplikasi.get("/tagihan/<int:nomor>")
def baca_tagihan(nomor: int) -> dict:
  """Melayani permintaan tagihan yang sudah pernah diterbitkan.

  Mengembalikan dict berisi data tagihan beserta satu lompatan jaringan yang
  dipakai gerbang untuk sampai ke layanan ini.
  """
  hasil = domain_penagihan.ambil_tagihan(nomor)
  hasil["lompatan"] = alamat.LOMPATAN_LAYANAN
  return hasil


@aplikasi.post("/tagihan/<int:nomor>")
def terbitkan_tagihan(nomor: int) -> dict:
  """Menerbitkan tagihan satu pesanan memakai kurs kiriman gerbang.

  Parameter nilai_kurs wajib ada, dan permintaan tanpa parameter itu ditolak
  sebagai pelanggaran kontrak. Mengembalikan dict berisi tagihan yang baru
  tersimpan beserta satu lompatan jaringan.
  """
  nilai_kurs = request.args.get("nilai_kurs", type=float)
  if nilai_kurs is None:
    raise kesalahan.AturanDilanggar("parameter nilai_kurs wajib disertakan")
  hasil = domain_penagihan.terbitkan_tagihan(nomor, nilai_kurs)
  hasil["lompatan"] = alamat.LOMPATAN_LAYANAN
  return hasil


if __name__ == "__main__":
  sarana.redam_catatan_web()
  aplikasi.run(host=alamat.TUAN_RUMAH, port=alamat.PORTA_PENAGIHAN,
               threaded=True)
