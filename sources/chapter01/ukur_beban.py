"""Mengukur perubahan latensi ketika jumlah klien serentak bertambah.

Satu server melayani banyak klien. Skrip ini menambah jumlah klien serentak
secara bertahap, lalu mencatat latensi pada setiap tahap. Hanya dijalankan
terhadap server milik sendiri.

Cara menjalankan: python ukur_beban.py
"""

import statistics
import time
from concurrent.futures import ThreadPoolExecutor

import klien

JUMLAH_KLIEN = [1, 2, 4, 8, 16]
PERMINTAAN_PER_KLIEN = 20
MILIDETIK = 1000.0


def satu_klien(jumlah_request):
  """Menjalankan sejumlah request berurutan, seperti satu pengguna yang menunggu.

  Request berikutnya baru dikirim sesudah jawaban sebelumnya tiba, sehingga
  satu klien tidak pernah membebani server dengan dua request sekaligus.
  Mengembalikan list berisi waktu setiap request dalam milidetik.
  """
  waktu = []
  for _ in range(jumlah_request):
    mulai = time.perf_counter()
    klien.minta_konversi("USD", "IDR", 100)
    waktu.append((time.perf_counter() - mulai) * MILIDETIK)
  return waktu


def jalankan_tahap(jumlah_klien):
  """Menjalankan sejumlah klien serentak lalu menggabungkan seluruh waktunya.

  Setiap klien berjalan pada utasnya sendiri, sehingga request mereka benar-benar
  datang bersamaan di server. Mengembalikan list berisi waktu seluruh request
  dari seluruh klien pada tahap tersebut, dalam milidetik.
  """
  with ThreadPoolExecutor(max_workers=jumlah_klien) as kolam:
    hasil = kolam.map(satu_klien, [PERMINTAAN_PER_KLIEN] * jumlah_klien)
  return [w for daftar in hasil for w in daftar]


if __name__ == "__main__":
  print(f"{'Klien':>6}  {'Median (ms)':>12}  {'Terbesar (ms)':>14}")
  for banyak in JUMLAH_KLIEN:
    waktu = jalankan_tahap(banyak)
    median = statistics.median(waktu)
    terbesar = max(waktu)
    print(f"{banyak:>6}  {median:>12.3f}  {terbesar:>14.3f}")
  # Keluarannya:      1         0.310          10.023
