"""Pipe yang menyambung filter gambar menjadi satu pipeline.

Pipe tidak mengubah satu piksel pun. Tugasnya hanya menyambungkan keluaran satu
filter menjadi masukan filter berikutnya. Karena penyambungnya terpusat di sini,
urutan stage dapat diubah tanpa menyentuh isi satu filter pun.

Setiap stage dapat dibungkus counter, sehingga jumlah gambar yang melewati stage
itu dapat dilaporkan. Angka itulah yang dipakai pada Latihan 1.

Setiap panggilan ditulis satu per satu, bukan disarangkan menjadi a(b(c())),
agar nilai antaranya terlihat saat latihan.

Cara menjalankan:
  python pipa.py
  python pipa.py hitung
"""

import sys

import penyaring

DIREKTORI_MASUKAN = "masukan"
BERKAS_TANDA = "tanda_air.png"
LEBAR_BAKU = 800
KUALITAS_BAKU = 85
DIREKTORI_KELUARAN = "keluaran/sedang"
JUMLAH_CONTOH = 3


class Counter:
  """Pembungkus satu stage yang mencatat jumlah gambar yang melewatinya.

  Pembungkus dipisah dari filternya agar filter tetap bersih dari urusan
  pengukuran. Pipe yang memutuskan kapan pembungkus ini dipasang.
  """

  def __init__(self, nama: str, fungsi) -> None:
    """Menyimpan nama stage beserta fungsinya, dengan cacahan mulai dari nol."""
    self.nama = nama
    self.fungsi = fungsi
    self.jumlah = 0

  def __call__(self, masukan):
    """Menjalankan stage aslinya sambil mencacah keluarannya.

    Pencacahan dilakukan pada keluaran, sebab yang menarik adalah berapa banyak
    gambar yang lolos dari stage ini. Menghasilkan item yang sama persis dengan
    stage aslinya.
    """
    for item in self.fungsi(masukan):
      self.jumlah += 1
      yield item


def nama_tahap(tahap) -> str:
  """Mengambil nama sebuah stage, baik yang berupa fungsi maupun kelas.

  Nama dipakai hanya untuk laporan, sehingga pipe tetap tidak bergantung pada
  isi stage-nya. Mengembalikan str berisi nama fungsi atau nama kelasnya.
  """
  return getattr(tahap, "__name__", type(tahap).__name__)


def susunan_baku() -> list:
  """Menyusun stage baku, yaitu satu resolusi dengan tanda air.

  Susunan ditulis sebagai daftar objek, bukan daftar nama, sebab sebagian stage
  membutuhkan pengaturan. Mengembalikan list berisi stage siap sambung.
  """
  return [
    penyaring.ubah_mode,
    penyaring.Resize(LEBAR_BAKU),
    penyaring.Watermark(BERKAS_TANDA),
    penyaring.SaveJpeg(DIREKTORI_KELUARAN, KUALITAS_BAKU),
  ]


def rakit(susunan: list, dengan_counter: bool = False) -> list:
  """Membungkus setiap stage dengan counter bila diminta.

  Tanpa pembungkus, pipeline berjalan seperti biasa tanpa biaya tambahan.
  Mengembalikan list berisi stage, atau list berisi Counter.
  """
  if not dengan_counter:
    return list(susunan)
  daftar = []
  for tahap in susunan:
    nama = nama_tahap(tahap)
    daftar.append(Counter(nama, tahap))
  return daftar


def jalankan(sumber: str, tahap: list, batas: int | None = None):
  """Menyambung seluruh stage menjadi satu pipeline, lalu mengembalikannya.

  Penyambungan dilakukan malas, sehingga belum satu file pun dibuka ketika
  fungsi ini selesai. Mengembalikan iterable berisi keluaran stage terakhir.
  """
  aliran = penyaring.baca_gambar(sumber, batas)
  for fungsi in tahap:
    aliran = fungsi(aliran)
  return aliran


def jalankan_sekaligus(sumber: str, tahap: list,
                       batas: int | None = None) -> list:
  """Menjalankan stage yang sama secara batch, satu stage sampai tuntas.

  Setiap stage dijadikan list lebih dahulu, sehingga seluruh gambar harus
  selesai diproses sebelum stage berikutnya mulai. Cara ini menjadi pembanding
  pada Latihan 3. Mengembalikan list berisi seluruh keluaran stage terakhir.
  """
  gambar = penyaring.baca_gambar(sumber, batas)
  aliran = list(gambar)
  for fungsi in tahap:
    hasil = fungsi(aliran)
    aliran = list(hasil)
  return aliran


if __name__ == "__main__":
  susunan = susunan_baku()
  if len(sys.argv) > 1 and sys.argv[1] == "hitung":
    tahap = rakit(susunan, dengan_counter=True)
    aliran = jalankan(DIREKTORI_MASUKAN, tahap)
    jumlah_akhir = sum(1 for _ in aliran)
    for pembungkus in tahap:
      print(f"  {pembungkus.nama:<12} meneruskan {pembungkus.jumlah} gambar")
      # Keluarannya baris pertama: ubah_mode meneruskan 60 gambar
    print(f"Keluaran akhir: {jumlah_akhir} file")
    # Keluarannya: Keluaran akhir: 60 file
  else:
    tahap = rakit(susunan)
    hasil = jalankan(DIREKTORI_MASUKAN, tahap)
    for nomor, (nama, direktori, ukuran) in enumerate(hasil, 1):
      print(f"{nama} -> {direktori}/ {ukuran:,} bait")
      if nomor == JUMLAH_CONTOH:
        break
    # Keluarannya baris pertama: contoh_001.jpg -> sedang/ 118,054 bait
