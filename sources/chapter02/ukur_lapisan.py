"""Mengukur selisih waktu jalur tertutup dan jalur terbuka.

Skrip ini menjalankan kedua jalur berulang kali, lalu melaporkan waktu median
dan persentil ke-95. Pengukuran bersifat mengamati, tidak membebani sistem
milik pihak lain.

Cara menjalankan: python ukur_lapisan.py
"""

import statistics
import time

import aplikasi_terbuka
import aplikasi_tertutup
import basis_data

JUMLAH_PENGULANGAN = 2000
MILIDETIK = 1000.0
AMBANG_PERSENTIL = 0.95


def ukur(fungsi, pengulangan):
  """Menjalankan sebuah fungsi berulang kali dan mengembalikan daftar waktunya.

  Waktu diambil dengan perf_counter karena jam tersebut tidak terpengaruh oleh
  perubahan waktu sistem.
  """
  waktu = []
  for _ in range(pengulangan):
    mulai = time.perf_counter()
    fungsi()
    waktu.append((time.perf_counter() - mulai) * MILIDETIK)
  return waktu


def ringkas(nama, waktu):
  """Mencetak median dan persentil ke-95 dari satu daftar waktu."""
  urut = sorted(waktu)
  p95 = urut[int(len(urut) * AMBANG_PERSENTIL) - 1]
  print(f"{nama:<10} median {statistics.median(urut):.4f} ms  p95 {p95:.4f} ms")


if __name__ == "__main__":
  basis_data.siapkan_basis_data()
  ringkas("tertutup", ukur(aplikasi_tertutup.tampilkan_daftar_kurs, JUMLAH_PENGULANGAN))
  ringkas("terbuka", ukur(aplikasi_terbuka.tampilkan_daftar_kurs, JUMLAH_PENGULANGAN))
  # Keluarannya: tertutup   median 0.0694 ms  p95 0.0814 ms
  # Keluarannya: terbuka    median 0.0707 ms  p95 0.1059 ms
