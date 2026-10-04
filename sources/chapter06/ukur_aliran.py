"""Membandingkan pemrosesan streaming dengan pemrosesan batch.

Streaming menyerahkan satu gambar melewati seluruh stage sebelum gambar
berikutnya dibuka. Batch menuntaskan satu stage untuk seluruh gambar, baru
lanjut ke stage berikutnya. Keduanya memakai stage yang sama persis, dan hanya
cara penyambungannya yang berbeda.

Dua hal diukur. Pertama, waktu sampai file pertama selesai ditulis, sebab itulah
yang dirasakan pengguna. Kedua, puncak Resident Set Size (RSS) proses, yaitu
memori yang benar-benar dipegang proses menurut sistem operasi.

Puncak RSS diambil lewat proses anak, satu proses untuk setiap jalur. Alasannya,
ru_maxrss adalah tanda air tertinggi yang tidak pernah turun, sehingga mengukur
kedua jalur di dalam satu proses akan melaporkan angka jalur termahal dua kali.
tracemalloc sengaja tidak dipakai, sebab penyangga piksel Pillow dialokasikan di
luar jangkauannya lalu menyembunyikan selisih yang justru menjadi pokok bahasan.

Setiap panggilan ditulis satu per satu, bukan disarangkan menjadi a(b(c())),
agar nilai antaranya terlihat saat latihan.

Cara menjalankan:
  python ukur_aliran.py
  python ukur_aliran.py memori streaming
  python ukur_aliran.py memori batch
"""

import pathlib
import resource
import statistics
import subprocess
import sys
import time

import penyaring
import pipa

JUMLAH_PUTARAN = 100
BATAS_PUTARAN = 10
BATAS_MEMORI = 60
PUTARAN_PER_LAPORAN = 20
DETIK_KE_MILIDETIK = 1000.0
KIBIBAIT_KE_MEBIBAIT = 1024.0


def susunan_ukur(tujuan: str) -> list:
  """Menyusun stage yang dipakai kedua cara pemrosesan.

  Susunan sengaja sama persis, sehingga yang dibandingkan benar-benar cara
  penyambungannya. Mengembalikan list berisi stage siap sambung.
  """
  return [
    penyaring.ubah_mode,
    penyaring.Resize(pipa.LEBAR_BAKU),
    penyaring.Watermark(pipa.BERKAS_TANDA),
    penyaring.SaveJpeg(tujuan, pipa.KUALITAS_BAKU),
  ]


def waktu_file_pertama_streaming() -> float:
  """Mengukur waktu sampai satu file pertama selesai ditulis.

  Stream dihentikan sesudah item pertama muncul, sebab yang diukur adalah waktu
  tunggu pengguna, bukan waktu seluruh kumpulan. Mengembalikan float berisi lama
  dalam milidetik.
  """
  susunan = susunan_ukur("keluaran/aliran")
  mulai = time.perf_counter()
  aliran = pipa.jalankan(pipa.DIREKTORI_MASUKAN, susunan, BATAS_PUTARAN)
  pembaca = iter(aliran)
  next(pembaca)
  selesai = time.perf_counter()
  return (selesai - mulai) * DETIK_KE_MILIDETIK


def waktu_file_pertama_batch() -> float:
  """Mengukur waktu sampai file pertama muncul pada pemrosesan batch.

  File pertama baru ada sesudah stage terakhir selesai untuk seluruh gambar,
  sebab setiap stage dituntaskan lebih dahulu. Mengembalikan float berisi lama
  dalam milidetik.
  """
  susunan = susunan_ukur("keluaran/sekaligus")
  mulai = time.perf_counter()
  pipa.jalankan_sekaligus(pipa.DIREKTORI_MASUKAN, susunan, BATAS_PUTARAN)
  selesai = time.perf_counter()
  return (selesai - mulai) * DETIK_KE_MILIDETIK


def puncak_rss_proses_ini(jalur: str) -> float:
  """Menjalankan satu jalur sampai habis lalu membaca puncak RSS prosesnya.

  Fungsi ini dipanggil di dalam proses anak, sehingga angkanya hanya mewakili
  jalur yang diminta. Mengembalikan float berisi puncak RSS dalam MiB.
  """
  susunan = susunan_ukur("keluaran/memori")
  if jalur == "batch":
    pipa.jalankan_sekaligus(pipa.DIREKTORI_MASUKAN, susunan, BATAS_MEMORI)
  else:
    aliran = pipa.jalankan(pipa.DIREKTORI_MASUKAN, susunan, BATAS_MEMORI)
    for _ in aliran:
      pass
  pemakaian = resource.getrusage(resource.RUSAGE_SELF)
  return pemakaian.ru_maxrss / KIBIBAIT_KE_MEBIBAIT


def ukur_puncak_rss(jalur: str) -> float:
  """Meminta proses anak menjalankan satu jalur lalu melaporkan puncak RSS-nya.

  Proses anak dipakai agar tanda air tertinggi RSS tidak tercampur antar jalur.
  Mengembalikan float berisi puncak RSS dalam MiB.
  """
  berkas_ini = pathlib.Path(__file__)
  perintah = [sys.executable, str(berkas_ini), "memori", jalur]
  hasil = subprocess.run(perintah, capture_output=True, text=True, check=True)
  keluaran = hasil.stdout.strip()
  return float(keluaran)


def jalankan_putaran() -> tuple[list, list]:
  """Menjalankan kedua cara bergantian sebanyak putaran yang diminta.

  Keduanya diukur di dalam putaran yang sama agar menghadapi keadaan mesin yang
  serupa. Mengembalikan tuple berisi dua list waktu file pertama.
  """
  streaming, batch = [], []
  mulai = time.perf_counter()
  print(f"Menjalankan {JUMLAH_PUTARAN} putaran, {BATAS_PUTARAN} gambar tiap"
        " putaran.", flush=True)
  for nomor in range(1, JUMLAH_PUTARAN + 1):
    streaming.append(waktu_file_pertama_streaming())
    batch.append(waktu_file_pertama_batch())
    if nomor % PUTARAN_PER_LAPORAN == 0:
      lewat = time.perf_counter() - mulai
      sisa = lewat / nomor * (JUMLAH_PUTARAN - nomor)
      print(f"  putaran {nomor:3d}/{JUMLAH_PUTARAN}"
            f"  streaming {statistics.median(streaming):.1f} ms"
            f"  batch {statistics.median(batch):.1f} ms"
            f"  sisa sekitar {sisa:3.0f} detik", flush=True)
  return streaming, batch


if __name__ == "__main__":
  if len(sys.argv) > 2 and sys.argv[1] == "memori":
    puncak = puncak_rss_proses_ini(sys.argv[2])
    print(f"{puncak:.1f}")
    sys.exit(0)

  hasil_streaming, hasil_batch = jalankan_putaran()
  median_streaming = statistics.median(hasil_streaming)
  median_batch = statistics.median(hasil_batch)
  selisih = median_batch - median_streaming
  range_streaming = max(hasil_streaming) - min(hasil_streaming)
  menang = sum(1 for a, b in zip(hasil_streaming, hasil_batch) if a < b)
  rss_streaming = ukur_puncak_rss("streaming")
  rss_batch = ukur_puncak_rss("batch")

  print(f"Putaran                       : {JUMLAH_PUTARAN}")
  print(f"Median file pertama streaming : {median_streaming:.1f} ms")
  # Keluarannya: Median file pertama streaming : 87.0 ms
  print(f"Median file pertama batch     : {median_batch:.1f} ms")
  print(f"Selisih median                : {selisih:.1f} ms")
  print(f"Batch lebih lambat            : {median_batch / median_streaming:.1f} kali")
  print(f"Range dalam jalur streaming   : {range_streaming:.1f} ms")
  print(f"Range dibagi selisih          : {range_streaming / selisih:.2f} kali")
  print(f"Putaran streaming lebih cepat : {menang} dari {JUMLAH_PUTARAN}")
  print(f"Puncak RSS streaming          : {rss_streaming:.1f} MiB")
  print(f"Puncak RSS batch              : {rss_batch:.1f} MiB")
  # Keluarannya: Putaran streaming lebih cepat : 100 dari 100
