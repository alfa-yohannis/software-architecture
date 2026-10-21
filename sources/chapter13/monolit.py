"""Versi monolit, satu proses dengan satu basis data yang memuat tiga tabel.

Versi ini menjadi pembanding bagi versi mikroservis. Aturan bisnisnya sama
persis, dan isi datanya pun sama, sebab definisi tabelnya diambil langsung dari
ketiga modul layanan. Yang berbeda hanya dua hal, yaitu jumlah prosesnya dan
jumlah berkas basis datanya.

Perbedaan itu membawa akibat yang diukur sepanjang bab. Laporan gabungan di
sini cukup satu kueri SQL dengan dua JOIN, sebab ketiga tabelnya berada pada
berkas yang sama. Merilis perubahan kurs di sini berarti menjalankan ulang
seluruh proses, sebab tidak ada bagian yang dapat dinyalakan sendiri.

Cara menjalankan: python monolit.py
"""

import logging

import flask

import alamat
import basis_data
import layanan_kurs
import layanan_nasabah
import layanan_pesanan

KUERI_LAPORAN = """SELECT n.nama, n.kota, n.rekening,
       p.id, p.mata_uang, p.nominal, k.dasar, k.margin
FROM nasabah AS n
JOIN pesanan AS p ON p.id_nasabah = n.id
JOIN kurs AS k ON k.mata_uang = p.mata_uang
WHERE n.id = ? AND p.status = ?
ORDER BY p.id"""

BASIS_DATA = basis_data.BasisDataLayanan("monolit.db", [
  layanan_nasabah.TABEL_NASABAH,
  layanan_pesanan.TABEL_PESANAN,
  layanan_kurs.TABEL_KURS,
])

LOMPATAN_MONOLIT = 1

aplikasi = flask.Flask(__name__)


def bentuk_baris_laporan(baris: tuple) -> dict:
  """Mengubah satu baris hasil JOIN menjadi satu baris laporan siap kirim.

  Kurs jual dihitung dengan fungsi yang sama seperti pada layanan kurs, agar
  angka kedua versi tidak mungkin berbeda. Mengembalikan dict berisi satu baris
  laporan lengkap dengan nilai rupiahnya.
  """
  jual = layanan_kurs.hitung_jual(baris[6], baris[7])
  return {"id": baris[3], "mata_uang": baris[4], "nominal": baris[5],
          "kurs_jual": jual, "rupiah": round(baris[5] * jual, 2)}


@aplikasi.get("/sehat")
def periksa_sehat():
  """Menjawab pemeriksaan kesiapan dari skrip penjalan dan skrip pengukuran.

  Satu jawaban dari sini sudah mewakili seluruh sistem, sebab seluruh
  kemampuannya berada di dalam proses ini. Mengembalikan dict berisi nama
  proses beserta penanda sehat.
  """
  return {"layanan": "monolit", "sehat": True}


@aplikasi.get("/nasabah/<id_nasabah>")
def ambil_nasabah(id_nasabah: str):
  """Memberikan satu nasabah beserta nomor rekening sesuai hak pemanggilnya.

  Aturan penyamaran rekening dipakai ulang dari modul layanan nasabah, sehingga
  jawabannya sama persis dengan versi mikroservis. Mengembalikan dict berisi
  data nasabah beserta jumlah lompatan, atau dict galat beserta kode 404.
  """
  baris = BASIS_DATA.baca(layanan_nasabah.KUERI_SATU_NASABAH, (id_nasabah,))
  if not baris:
    return {"galat": f"nasabah {id_nasabah} tidak ada"}, 404
  nomor, nama, kota, rekening = baris[0]
  token = flask.request.headers.get("X-Token")
  return {"id": nomor, "nama": nama, "kota": kota,
          "rekening": layanan_nasabah.samarkan_rekening(rekening, token),
          "lompatan": LOMPATAN_MONOLIT}


@aplikasi.get("/kurs/<mata_uang>")
def ambil_kurs(mata_uang: str):
  """Memberikan kurs jual satu mata uang tanpa membuka margin banknya.

  Kueri dan perhitungannya dipakai ulang dari modul layanan kurs, sehingga
  kedua versi menjawab angka yang sama. Mengembalikan dict berisi mata uang,
  kurs jual, dan jumlah lompatan, atau dict galat beserta kode 404.
  """
  baris = BASIS_DATA.baca(layanan_kurs.KUERI_SATU_KURS, (mata_uang.upper(),))
  if not baris:
    return {"galat": f"kurs {mata_uang} tidak ada"}, 404
  kode, dasar, margin = baris[0]
  return {"mata_uang": kode, "jual": layanan_kurs.hitung_jual(dasar, margin),
          "lompatan": LOMPATAN_MONOLIT}


@aplikasi.get("/laporan/<id_nasabah>")
def susun_laporan(id_nasabah: str):
  """Menyusun laporan gabungan lewat satu kueri SQL dengan dua JOIN.

  Penggabungan dikerjakan mesin basis data, sebab ketiga tabelnya berada pada
  berkas yang sama. Tidak ada permintaan jaringan tambahan, sehingga jumlah
  lompatannya tetap satu berapa pun banyak mata uang yang dipesan.
  Mengembalikan dict berisi laporan lengkap, atau dict galat beserta kode 404
  bila nasabahnya tidak ada atau belum punya pesanan lunas.
  """
  baris = BASIS_DATA.baca(KUERI_LAPORAN, (id_nasabah, layanan_pesanan.STATUS_SAH))
  if not baris:
    return {"galat": f"laporan {id_nasabah} kosong"}, 404
  token = flask.request.headers.get("X-Token")
  isi = [bentuk_baris_laporan(satu) for satu in baris]
  return {
    "nasabah": {"id": id_nasabah, "nama": baris[0][0], "kota": baris[0][1],
                "rekening": layanan_nasabah.samarkan_rekening(baris[0][2], token)},
    "pesanan": isi,
    "total_rupiah": round(sum(satu["rupiah"] for satu in isi), 2),
    "lengkap": True,
    "lompatan": LOMPATAN_MONOLIT,
  }


if __name__ == "__main__":
  logging.getLogger("werkzeug").setLevel(logging.ERROR)
  BASIS_DATA.siapkan()
  aplikasi.run(port=alamat.PORTA_MONOLIT, threaded=True)
