"""Gerbang versi mikroservis, penyusun laporan gabungan dari tiga layanan.

Gerbang tidak memiliki basis data sama sekali. Seluruh datanya diminta lewat
HTTP kepada layanan pemiliknya, lalu digabungkan di dalam kode. Penggabungan
lewat SQL tidak lagi mungkin di sini, sebab ketiga tabelnya berada pada tiga
berkas yang hanya boleh dibuka pemiliknya masing-masing.

Setiap jawaban memuat kunci lompatan, yaitu jumlah perjalanan HTTP yang
dibutuhkan untuk melayani satu permintaan, terhitung sejak permintaan klien.
Angka itulah yang dibandingkan dengan angka satu pada versi monolit.

Cara menjalankan: python gerbang.py
"""

import logging

import flask
import requests

import alamat

TENGGANG_DETIK = 2.0
LOMPATAN_KLIEN = 1

SESI = requests.Session()

aplikasi = flask.Flask(__name__)


def ambil_json(url: str, token: str | None = None) -> dict | None:
  """Meminta satu dokumen JSON kepada layanan lain lewat HTTP.

  Objek Session dipakai ulang agar sambungan TCP tidak dibuat baru setiap
  panggilan, sama seperti klien HTTP pada sistem sungguhan. Pemakaiannya aman
  di sini sebab skrip pengukuran bab ini mengirim permintaan satu per satu.
  Mengembalikan dict berisi badan jawaban, atau None bila layanannya tidak
  menjawab atau menjawab dengan kode selain 200.
  """
  kepala = {"X-Token": token} if token else {}
  try:
    jawaban = SESI.get(url, headers=kepala, timeout=TENGGANG_DETIK)
  except requests.RequestException:
    return None
  if jawaban.status_code != 200:
    return None
  return jawaban.json()


def gabungkan_baris(pesanan: dict, kurs: dict | None) -> dict:
  """Menggabungkan satu baris pesanan dengan kurs jual mata uangnya.

  Inilah pekerjaan yang pada versi monolit dikerjakan klausa JOIN. Bedanya,
  pencocokan di sini dikerjakan kode Python atas dua dokumen JSON yang datang
  dari dua proses berbeda. Mengembalikan dict berisi satu baris laporan, dengan
  rupiah bernilai None bila layanan kurs tidak menjawab.
  """
  if kurs is None:
    return {"id": pesanan["id"], "mata_uang": pesanan["mata_uang"],
            "nominal": pesanan["nominal"], "kurs_jual": None, "rupiah": None}
  return {"id": pesanan["id"], "mata_uang": pesanan["mata_uang"],
          "nominal": pesanan["nominal"], "kurs_jual": kurs["jual"],
          "rupiah": round(pesanan["nominal"] * kurs["jual"], 2)}


def kumpulkan_kurs(daftar_pesanan: list[dict]) -> dict:
  """Meminta kurs sekali untuk setiap mata uang yang benar-benar dipakai.

  Mata uang yang sama tidak diminta dua kali, sehingga jumlah panggilannya
  mengikuti banyak mata uang, bukan banyak pesanan. Mengembalikan dict yang
  memetakan mata uang ke dokumen kursnya, atau ke None bila layanan kurs tidak
  menjawab.
  """
  terkumpul = {}
  for pesanan in daftar_pesanan:
    mata_uang = pesanan["mata_uang"]
    if mata_uang not in terkumpul:
      terkumpul[mata_uang] = ambil_json(f"{alamat.KURS}/kurs/{mata_uang}")
  return terkumpul


@aplikasi.get("/sehat")
def periksa_sehat():
  """Menjawab pemeriksaan kesiapan gerbang sendiri, bukan kesiapan layanan.

  Gerbang yang sehat belum berarti seluruh layanan sehat, dan pemisahan itu
  disengaja agar skrip penjalan dapat menunggu tiap proses sendiri-sendiri.
  Mengembalikan dict berisi nama proses beserta penanda sehat.
  """
  return {"layanan": "gerbang", "sehat": True}


@aplikasi.get("/nasabah/<id_nasabah>")
def teruskan_nasabah(id_nasabah: str):
  """Meneruskan permintaan satu nasabah kepada layanan pemiliknya.

  Fungsi ini memang hanya meneruskan, sebab pembacaan satu nasabah tidak
  menyentuh data layanan lain sehingga tidak ada aturan lintas layanan yang
  perlu ditegakkan di sini. Keberadaannya tetap penting, yaitu menjadi ukuran
  biaya satu lompatan tambahan yang murni. Mengembalikan dict jawaban layanan
  nasabah beserta jumlah lompatan, atau dict galat beserta kode 503.
  """
  token = flask.request.headers.get("X-Token")
  jawaban = ambil_json(f"{alamat.NASABAH}/nasabah/{id_nasabah}", token)
  if jawaban is None:
    return {"galat": "layanan nasabah tidak menjawab"}, 503
  jawaban["lompatan"] = LOMPATAN_KLIEN + 1
  return jawaban


@aplikasi.get("/kurs/<mata_uang>")
def teruskan_kurs(mata_uang: str):
  """Meneruskan permintaan satu kurs kepada layanan pemiliknya.

  Sama seperti pembacaan nasabah, tidak ada aturan lintas layanan di sini,
  sehingga gerbang tidak menambahkan apa pun selain satu lompatan.
  Mengembalikan dict jawaban layanan kurs beserta jumlah lompatan, atau dict
  galat beserta kode 503.
  """
  jawaban = ambil_json(f"{alamat.KURS}/kurs/{mata_uang}")
  if jawaban is None:
    return {"galat": "layanan kurs tidak menjawab"}, 503
  jawaban["lompatan"] = LOMPATAN_KLIEN + 1
  return jawaban


@aplikasi.get("/laporan/<id_nasabah>")
def susun_laporan(id_nasabah: str):
  """Menyusun laporan gabungan dengan memanggil tiga layanan berurutan.

  Layanan nasabah dan layanan pesanan wajib menjawab, sebab tanpa keduanya
  laporan tidak punya isi. Layanan kurs boleh tidak menjawab, dan laporannya
  tetap keluar dengan kunci lengkap bernilai false. Mengembalikan dict berisi
  laporan beserta jumlah lompatan, atau dict galat beserta kode 503 atau 404.
  """
  token = flask.request.headers.get("X-Token")
  nasabah = ambil_json(f"{alamat.NASABAH}/nasabah/{id_nasabah}", token)
  if nasabah is None:
    return {"galat": "layanan nasabah tidak menjawab"}, 503
  jawaban_pesanan = ambil_json(f"{alamat.PESANAN}/pesanan?nasabah={id_nasabah}")
  if jawaban_pesanan is None:
    return {"galat": "layanan pesanan tidak menjawab"}, 503
  daftar_pesanan = jawaban_pesanan["pesanan"]
  if not daftar_pesanan:
    return {"galat": f"laporan {id_nasabah} kosong"}, 404
  kurs = kumpulkan_kurs(daftar_pesanan)
  isi = [gabungkan_baris(satu, kurs[satu["mata_uang"]]) for satu in daftar_pesanan]
  terpakai = [satu["rupiah"] for satu in isi if satu["rupiah"] is not None]
  return {
    "nasabah": nasabah,
    "pesanan": isi,
    "total_rupiah": round(sum(terpakai), 2),
    "lengkap": len(terpakai) == len(isi),
    "lompatan": LOMPATAN_KLIEN + 2 + len(kurs),
  }


if __name__ == "__main__":
  logging.getLogger("werkzeug").setLevel(logging.ERROR)
  aplikasi.run(port=alamat.PORTA_GERBANG, threaded=True)
