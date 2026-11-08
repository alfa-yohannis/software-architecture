"""Mengukur waktu bolak-balik satu request ke server.

Waktu yang diukur mencakup pengiriman request, perhitungan di server, dan
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
  """Mengirim request yang sama berulang kali lalu mencatat lama setiap request.

  Setiap request diukur sendiri-sendiri, sebab yang dilaporkan adalah
  sebarannya, bukan rata-ratanya. Mengembalikan list berisi waktu setiap request
  dalam milidetik, sesuai urutan pengirimannya.
  """
  waktu = []
  for _ in range(pengulangan):
    mulai = time.perf_counter()
    klien.minta_konversi("USD", "IDR", 100)
    waktu.append((time.perf_counter() - mulai) * MILIDETIK)
  return waktu


if __name__ == "__main__":
  waktu_mentah = ukur_bolak_balik(JUMLAH_PENGULANGAN)
  hasil = sorted(waktu_mentah)
  p95 = hasil[int(len(hasil) * AMBANG_PERSENTIL) - 1]
  median = statistics.median(hasil)
  print(f"Request          : {JUMLAH_PENGULANGAN}")
  print(f"Median           : {median:.3f} ms")
  print(f"Persentil ke-95  : {p95:.3f} ms")
  print(f"Terkecil         : {hasil[0]:.3f} ms")
  print(f"Terbesar         : {hasil[-1]:.3f} ms")
  # Keluarannya: Median           : 0.273 ms
