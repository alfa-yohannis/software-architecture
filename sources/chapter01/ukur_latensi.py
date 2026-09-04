"""Mengukur waktu bolak-balik satu permintaan ke server.

Waktu yang diukur mencakup pengiriman permintaan, perhitungan di server, dan
pengiriman jawaban kembali. Pengukuran bersifat mengamati, dan hanya dijalankan
terhadap server milik sendiri.

Cara menjalankan: python ukur_latensi.py
"""

import statistics
import time

import klien

JUMLAH_PENGULANGAN = 200
MILIDETIK = 1000.0
AMBANG_PERSENTIL = 0.95


def ukur_bolak_balik(pengulangan):
  """Mengirim permintaan berulang kali lalu mengumpulkan waktunya."""
  waktu = []
  for _ in range(pengulangan):
    mulai = time.perf_counter()
    klien.minta_konversi("USD", "IDR", 100)
    waktu.append((time.perf_counter() - mulai) * MILIDETIK)
  return waktu


if __name__ == "__main__":
  hasil = sorted(ukur_bolak_balik(JUMLAH_PENGULANGAN))
  p95 = hasil[int(len(hasil) * AMBANG_PERSENTIL) - 1]
  print(f"Permintaan       : {JUMLAH_PENGULANGAN}")
  print(f"Median           : {statistics.median(hasil):.3f} ms")
  print(f"Persentil ke-95  : {p95:.3f} ms")
  print(f"Terkecil         : {hasil[0]:.3f} ms")
  print(f"Terbesar         : {hasil[-1]:.3f} ms")
  # Keluarannya: Median           : 0.237 ms
