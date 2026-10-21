"""Gerbang antarmuka pada versi service-based.

Gerbang tidak memuat satu pun aturan bisnis. Tugasnya menerima permintaan
klien, meneruskannya ke layanan domain yang tepat lewat jaringan, lalu
merangkai jawabannya. Jalur permintaan dan bentuk jawabannya sama persis
dengan versi monolit, sehingga klien tidak dapat membedakan keduanya kecuali
dari angka lompatan.

Panggilan keluar memakai satu objek Session agar sambungan dipakai ulang,
sama seperti gerbang sungguhan. Tambahan waktu yang terukur pada Latihan 1
karena itu tidak digelembungkan oleh pembukaan sambungan baru pada setiap
permintaan.

Cara menjalankan:
  python basis_data.py
  python jalankan_layanan.py hidup
  curl -X POST http://127.0.0.1:8100/pesanan/1/tagihan
"""

from flask import Flask
import requests

import alamat
import kesalahan
import sarana

aplikasi = Flask(__name__)
sarana.pasang_penangan_galat(aplikasi)
sesi = requests.Session()


def minta(porta: int, jalur: str, metode: str = "GET",
          parameter: dict | None = None) -> dict:
  """Memanggil satu layanan domain lewat jaringan lalu membaca jawabannya.

  Layanan yang tidak menjawab dan layanan yang menjawab galat dipisahkan,
  sebab keduanya berbeda arti bagi klien. Kode 404 dan 409 diteruskan apa
  adanya, sedangkan kegagalan sambungan menjadi
  kesalahan.LayananTakTerjangkau. Mengembalikan dict hasil penguraian JSON
  jawaban layanan.
  """
  try:
    jawaban = sesi.request(metode, f"{alamat.alamat_dasar(porta)}{jalur}",
                           params=parameter,
                           timeout=alamat.BATAS_WAKTU_DETIK)
  except requests.RequestException as galat:
    raise kesalahan.LayananTakTerjangkau(
      f"layanan di porta {porta} tidak menjawab: {galat.__class__.__name__}")
  if jawaban.status_code == sarana.STATUS_TIDAK_DITEMUKAN:
    raise kesalahan.TidakDitemukan(jawaban.json()["galat"])
  if jawaban.status_code == sarana.STATUS_ATURAN_DILANGGAR:
    raise kesalahan.AturanDilanggar(jawaban.json()["galat"])
  if jawaban.status_code >= sarana.STATUS_TIDAK_DITEMUKAN:
    raise kesalahan.LayananTakTerjangkau(
      f"layanan di porta {porta} menjawab {jawaban.status_code}")
  return jawaban.json()


@aplikasi.get("/sehat")
def periksa_sehat() -> dict:
  """Menyatakan bahwa gerbang sudah siap menerima permintaan.

  Kesehatan ketiga layanan domain sengaja tidak ikut diperiksa di sini, agar
  skrip penjalan dapat menunggu setiap proses secara terpisah. Mengembalikan
  dict berisi status dan nama versinya.
  """
  return {"status": "sehat", "versi": "service-based"}


@aplikasi.get("/kurs/<kode>")
def baca_kurs(kode: str) -> dict:
  """Meneruskan permintaan nilai tukar ke layanan kurs.

  Mengembalikan dict berisi kode, nilai, dan jumlah lompatan jaringannya,
  yaitu satu lompatan dari klien ditambah satu lompatan ke layanan kurs.
  """
  hasil = minta(alamat.PORTA_KURS, f"/kurs/{kode}")
  hasil["lompatan"] += alamat.LOMPATAN_KLIEN
  return hasil


@aplikasi.get("/pesanan/<int:nomor>")
def baca_pesanan(nomor: int) -> dict:
  """Meneruskan permintaan satu pesanan ke layanan pemesanan.

  Mengembalikan dict berisi data pesanan beserta jumlah lompatan
  jaringannya.
  """
  hasil = minta(alamat.PORTA_PEMESANAN, f"/pesanan/{nomor}")
  hasil["lompatan"] += alamat.LOMPATAN_KLIEN
  return hasil


@aplikasi.get("/tagihan/<int:nomor>")
def baca_tagihan(nomor: int) -> dict:
  """Meneruskan permintaan tagihan ke layanan penagihan.

  Mengembalikan dict berisi data tagihan beserta jumlah lompatan
  jaringannya.
  """
  hasil = minta(alamat.PORTA_PENAGIHAN, f"/tagihan/{nomor}")
  hasil["lompatan"] += alamat.LOMPATAN_KLIEN
  return hasil


@aplikasi.post("/pesanan/<int:nomor>/tagihan")
def terbitkan_tagihan(nomor: int) -> dict:
  """Merangkai jawaban gabungan dari ketiga layanan domain sekaligus.

  Urutannya membaca pesanan, membaca kurs mata uangnya, lalu meminta layanan
  penagihan menerbitkan tagihan memakai kurs tersebut. Mengembalikan dict
  berisi pesanan, kurs, tagihan, dan jumlah lompatan jaringannya, yaitu satu
  lompatan klien ditambah tiga lompatan ke layanan domain.
  """
  pesanan = minta(alamat.PORTA_PEMESANAN, f"/pesanan/{nomor}")
  kurs = minta(alamat.PORTA_KURS, f"/kurs/{pesanan['mata_uang']}")
  tagihan = minta(alamat.PORTA_PENAGIHAN, f"/tagihan/{nomor}", "POST",
                  {"nilai_kurs": kurs["nilai"]})
  return {
    "pesanan": pesanan,
    "kurs": kurs,
    "tagihan": tagihan,
    "lompatan": (alamat.LOMPATAN_KLIEN + pesanan["lompatan"]
                 + kurs["lompatan"] + tagihan["lompatan"]),
  }


if __name__ == "__main__":
  sarana.redam_catatan_web()
  aplikasi.run(host=alamat.TUAN_RUMAH, port=alamat.PORTA_GERBANG,
               threaded=True)
