"""Memperlihatkan fan-out dan merge pada pipeline pengolah gambar.

Satu file sumber jarang cukup dalam satu ukuran. Situs yang sama biasanya
membutuhkan file kecil untuk daftar, sedang untuk halaman, dan besar untuk
tampilan penuh. Kebutuhan itu dijawab dengan fan-out, yaitu satu stream
digandakan, tiap cabang diolah dengan pengaturan berbeda, lalu laporannya
disatukan kembali.

Merge sebenarnya terjadi dua kali. Yang pertama di dalam setiap cabang, yaitu
ketika tanda air disatukan dengan fotonya. Yang kedua di ujung, yaitu ketika
laporan ketiga cabang disambung menjadi satu stream.

Setiap panggilan ditulis satu per satu, bukan disarangkan menjadi a(b(c())),
agar nilai antaranya terlihat saat latihan.

Cara menjalankan: python percabangan.py
"""

import collections
import itertools

import penyaring
import pipa

BERKAS_TANDA = "tanda_air.png"
# Tiga cabang beserta tujuan pemakaiannya. Lebar dan kualitas sengaja berbeda,
# sebab file untuk daftar tidak perlu setajam file untuk tampilan penuh.
CABANG = [
  ("kecil", 320, 75),
  ("sedang", 800, 85),
  ("besar", 1600, 90),
]


def cabangkan(aliran, jumlah: int):
  """Menggandakan satu stream menjadi beberapa stream yang berdiri sendiri.

  Fan-out memakai itertools.tee, sehingga sumbernya cukup dibaca sekali walaupun
  cabangnya banyak. Mengembalikan tuple berisi sejumlah stream sesuai yang
  diminta.
  """
  return itertools.tee(aliran, jumlah)


def gabungkan(*aliran):
  """Menyambung beberapa stream laporan menjadi satu stream tunggal.

  Merge-nya berurutan, yaitu stream berikutnya baru dibaca sesudah yang
  sebelumnya habis. Menghasilkan item dari seluruh stream yang diberikan.
  """
  return itertools.chain(*aliran)


def rakit_cabang(nama: str, lebar: int, kualitas: int) -> list:
  """Menyusun stage untuk satu cabang resolusi.

  Watermark dipasang sesudah Resize, sebab menempel pada kanvas kecil jauh lebih
  murah daripada menempel pada kanvas asli. Mengembalikan list berisi stage siap
  sambung untuk cabang tersebut.
  """
  return [
    penyaring.Resize(lebar),
    penyaring.Watermark(BERKAS_TANDA),
    penyaring.SaveJpeg(f"keluaran/{nama}", kualitas),
  ]


def jalankan_bercabang(sumber: str) -> dict:
  """Menjalankan ketiga cabang dari satu pembacaan sumber, lalu melaporkannya.

  Stage penyeragaman mode dikerjakan sekali di hulu, sebab hasilnya sama untuk
  ketiga cabang. Mengembalikan dict berisi jumlah file dan total bait untuk
  setiap cabang.
  """
  gambar = penyaring.baca_gambar(sumber)
  hulu = penyaring.ubah_mode(gambar)
  jumlah_cabang = len(CABANG)
  aliran_cabang = cabangkan(hulu, jumlah_cabang)

  laporan = []
  for (nama, lebar, kualitas), aliran in zip(CABANG, aliran_cabang):
    for tahap in rakit_cabang(nama, lebar, kualitas):
      aliran = tahap(aliran)
    laporan.append(aliran)

  ringkas = collections.defaultdict(lambda: [0, 0])
  gabungan = gabungkan(*laporan)
  for _, direktori, ukuran in gabungan:
    ringkas[direktori][0] += 1
    ringkas[direktori][1] += ukuran
  return dict(ringkas)


if __name__ == "__main__":
  hasil = jalankan_bercabang(pipa.DIREKTORI_MASUKAN)
  total_berkas = sum(jumlah for jumlah, _ in hasil.values())
  for nama, lebar, kualitas in CABANG:
    jumlah, bait = hasil[nama]
    print(f"  {nama:<7} lebar {lebar:<5} kualitas {kualitas}"
          f"  {jumlah} file  {bait / 1024:,.0f} KiB")
    # Keluarannya baris pertama: kecil lebar 320 kualitas 75  60 file  723 KiB
  print(f"Sumber dibaca sekali, keluaran {total_berkas} file")
