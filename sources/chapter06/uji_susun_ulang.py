"""Membandingkan dua urutan stage yang memuat filter yang sama persis.

Urutan baku memperkecil gambar lebih dahulu, baru menempelkan tanda air. Urutan
kedua membalik keduanya. Keduanya sah menurut contract pipe, sebab kedua stage
menerima dan menghasilkan bentuk data yang sama. Tidak satu pun file filter
disunting, sebab yang berubah hanya isi daftar stage-nya.

Waktu diukur berulang, sebab selisih waktu yang dicari kecil dan satu putaran
tidak cukup untuk menyimpulkan apa pun. File keluarannya dibandingkan lewat
sidik ringkas, sebab pertanyaannya bukan mirip atau tidak, melainkan sama persis
atau tidak.

Setiap panggilan ditulis satu per satu, bukan disarangkan menjadi a(b(c())),
agar nilai antaranya terlihat saat latihan.

Cara menjalankan: python uji_susun_ulang.py
"""

import hashlib
import pathlib
import statistics
import time

import penyaring
import pipa

KUALITAS = 85
LEBAR = 800
BATAS_GAMBAR = 10
JUMLAH_PUTARAN = 100
PUTARAN_PER_LAPORAN = 20


def susunan_resize_dahulu(tujuan: str) -> list:
  """Menyusun stage dengan Resize lebih dahulu, lalu Watermark.

  Urutan ini yang dipakai pipeline baku. Mengembalikan list berisi stage siap
  sambung yang menulis ke direktori tujuan.
  """
  return [
    penyaring.ubah_mode,
    penyaring.Resize(LEBAR),
    penyaring.Watermark(pipa.BERKAS_TANDA),
    penyaring.SaveJpeg(tujuan, KUALITAS),
  ]


def susunan_watermark_dahulu(tujuan: str) -> list:
  """Menyusun stage dengan Watermark lebih dahulu, lalu Resize.

  Penukaran ini sah menurut contract pipe, sebab kedua stage menerima dan
  menghasilkan bentuk yang sama. Mengembalikan list berisi stage siap sambung
  yang menulis ke direktori tujuan.
  """
  return [
    penyaring.ubah_mode,
    penyaring.Watermark(pipa.BERKAS_TANDA),
    penyaring.Resize(LEBAR),
    penyaring.SaveJpeg(tujuan, KUALITAS),
  ]


def kosongkan_direktori(tujuan: str) -> None:
  """Menghapus file JPEG sisa penjalanan sebelumnya di direktori tujuan.

  Tanpa pembersihan ini, sidik direktori ikut menghitung file dari penjalanan
  lama yang mungkin memakai jumlah gambar berbeda, sehingga sidiknya berubah
  tanpa sebab yang terbaca. Tidak mengembalikan apa pun.
  """
  direktori = pathlib.Path(tujuan)
  if not direktori.exists():
    return
  daftar_file = sorted(direktori.glob("*.jpg"))
  for berkas in daftar_file:
    berkas.unlink()


def satu_putaran(susunan: list) -> float:
  """Menjalankan satu susunan sampai habis, lalu mengembalikan lamanya.

  Jumlah gambar dibatasi agar seratus putaran selesai dalam waktu yang masuk
  akal. Mengembalikan float berisi lama pemrosesan dalam detik.
  """
  mulai = time.perf_counter()
  aliran = pipa.jalankan(pipa.DIREKTORI_MASUKAN, susunan, BATAS_GAMBAR)
  sum(1 for _ in aliran)
  selesai = time.perf_counter()
  return selesai - mulai


def ukur_kedua_urutan() -> tuple[list, list]:
  """Menjalankan kedua urutan bergantian sebanyak putaran yang diminta.

  Keduanya diukur di dalam putaran yang sama agar menghadapi keadaan mesin yang
  serupa. Mengembalikan tuple berisi dua list waktu, satu untuk tiap urutan.
  """
  resize = susunan_resize_dahulu("keluaran/urut_resize")
  watermark = susunan_watermark_dahulu("keluaran/urut_watermark")
  kosongkan_direktori("keluaran/urut_resize")
  kosongkan_direktori("keluaran/urut_watermark")
  waktu_resize, waktu_watermark = [], []
  mulai = time.perf_counter()
  print(f"Menjalankan {JUMLAH_PUTARAN} putaran untuk kedua urutan,"
        f" {BATAS_GAMBAR} gambar tiap putaran.", flush=True)
  for nomor in range(1, JUMLAH_PUTARAN + 1):
    waktu_resize.append(satu_putaran(resize))
    waktu_watermark.append(satu_putaran(watermark))
    if nomor % PUTARAN_PER_LAPORAN == 0:
      lewat = time.perf_counter() - mulai
      sisa = lewat / nomor * (JUMLAH_PUTARAN - nomor)
      print(f"  putaran {nomor:3d}/{JUMLAH_PUTARAN}"
            f"  resize {statistics.median(waktu_resize):.4f} s"
            f"  watermark {statistics.median(waktu_watermark):.4f} s"
            f"  sisa sekitar {sisa:3.0f} detik", flush=True)
  return waktu_resize, waktu_watermark


def ringkas_lima_angka(deret: list) -> dict:
  """Menghitung lima angka ringkasan sederet waktu putaran.

  Lima angka itu yang dibutuhkan untuk menggambar boxplot, yaitu nilai
  terkecil, kuartil pertama, median, kuartil ketiga, dan nilai terbesar.
  Mengembalikan dict berisi kelimanya dalam detik.
  """
  terurut = sorted(deret)
  kuartil = statistics.quantiles(terurut, n=4, method="inclusive")
  return {
    "terkecil": terurut[0],
    "kuartil_1": kuartil[0],
    "median": kuartil[1],
    "kuartil_3": kuartil[2],
    "terbesar": terurut[-1],
  }


def cetak_lima_angka(judul: str, deret: list) -> None:
  """Mencetak lima angka ringkasan satu urutan dalam satu baris.

  Barisnya dipakai mahasiswa untuk menggambar ulang boxplot pada latihan.
  Tidak mengembalikan apa pun.
  """
  angka = ringkas_lima_angka(deret)
  print(f"{judul:30s}: min {angka['terkecil']:.4f}"
        f"  Q1 {angka['kuartil_1']:.4f}"
        f"  median {angka['median']:.4f}"
        f"  Q3 {angka['kuartil_3']:.4f}"
        f"  maks {angka['terbesar']:.4f}")


def sidik_direktori(tujuan: str) -> str:
  """Menghitung satu sidik ringkas atas seluruh file di dalam direktori.

  Sidik dipakai untuk menjawab satu pertanyaan saja, yaitu apakah kedua urutan
  menghasilkan file yang sama persis. Mengembalikan str berisi enam belas digit
  pertama sidik SHA-256 gabungan.
  """
  pencerna = hashlib.sha256()
  daftar_file = sorted(pathlib.Path(tujuan).glob("*.jpg"))
  for berkas in daftar_file:
    isi = berkas.read_bytes()
    pencerna.update(isi)
  ringkas = pencerna.hexdigest()
  return ringkas[:16]


if __name__ == "__main__":
  waktu_resize, waktu_watermark = ukur_kedua_urutan()
  median_resize = statistics.median(waktu_resize)
  median_watermark = statistics.median(waktu_watermark)
  selisih = abs(median_watermark - median_resize)
  range_resize = max(waktu_resize) - min(waktu_resize)
  range_watermark = max(waktu_watermark) - min(waktu_watermark)
  menang = sum(1 for a, b in zip(waktu_resize, waktu_watermark) if a < b)

  print(f"Median urutan Resize dahulu    : {median_resize:.4f} detik")
  # Keluarannya: Median urutan Resize dahulu    : 0.5835 detik
  print(f"Median urutan Watermark dahulu : {median_watermark:.4f} detik")
  print(f"Selisih median                 : {selisih:.4f} detik")
  print(f"Range urutan Resize            : {range_resize:.4f} detik")
  print(f"Range urutan Watermark         : {range_watermark:.4f} detik")
  print(f"Range dibagi selisih           : {range_resize / selisih:.1f} kali")
  print(f"Putaran Resize lebih cepat     : {menang} dari {JUMLAH_PUTARAN}")

  cetak_lima_angka("Lima angka urutan Resize", waktu_resize)
  # Keluarannya: Lima angka urutan Resize      : min 0.5406  Q1 0.5665 ...
  cetak_lima_angka("Lima angka urutan Watermark", waktu_watermark)

  sidik_resize = sidik_direktori("keluaran/urut_resize")
  sidik_watermark = sidik_direktori("keluaran/urut_watermark")
  print(f"Sidik urutan Resize            : {sidik_resize}")
  print(f"Sidik urutan Watermark         : {sidik_watermark}")
  print(f"File sama persis               : {sidik_resize == sidik_watermark}")
  # Keluarannya: File sama persis               : False
