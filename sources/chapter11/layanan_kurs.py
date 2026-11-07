"""Layanan domain kurs, salah satu dari tiga proses pada versi service-based.

Proses ini hanya memuat bidang kurs. Kode bidangnya sama persis dengan yang
dipakai versi monolit, yaitu domain_kurs.py, sehingga pemecahan menjadi
layanan tidak menuntut penulisan ulang aturan apa pun. Yang bertambah hanya
selubung web di file ini.

Cara menjalankan:
  python basis_data.py
  python layanan_kurs.py
  curl http://127.0.0.1:8101/kurs/USD
"""

from flask import Flask

import alamat
import domain_kurs
import sarana

aplikasi = Flask(__name__)
sarana.pasang_penangan_galat(aplikasi)


@aplikasi.get("/sehat")
def periksa_sehat() -> dict:
  """Menyatakan bahwa layanan kurs sudah siap menerima request.

  Mengembalikan dict berisi status dan nama layanannya, dipakai skrip
  penjalan sebagai tanda bahwa port-nya sudah terbuka.
  """
  return {"status": "sehat", "layanan": "kurs"}


@aplikasi.get("/kurs/<kode>")
def baca_kurs(kode: str) -> dict:
  """Melayani request nilai tukar satu mata uang dari gerbang.

  Mengembalikan dict berisi kode, nilai, dan satu hop jaringan, yaitu
  hop yang dipakai gerbang untuk sampai ke layanan ini.
  """
  hasil = domain_kurs.ambil_kurs(kode)
  hasil["lompatan"] = alamat.LOMPATAN_LAYANAN
  return hasil


if __name__ == "__main__":
  sarana.redam_catatan_web()
  aplikasi.run(host=alamat.TUAN_RUMAH, port=alamat.PORTA_KURS, threaded=True)
