"""Layanan audit pada versi tanpa orkestrasi, langkah terakhir alur kerja.

Tetapan BERIKUTNYA bernilai None, sehingga layanan ini mengembalikan konteks
akhir kepada pemanggilnya. Balasan itulah yang naik kembali melewati seluruh
layanan sebelumnya.

Cara menjalankan: python server.py
"""

from berantai import pembantu

# Potongan alur kerja yang dipegang layanan ini.
BERIKUTNYA = None


def buat_aplikasi():
  """Membentuk aplikasi Flask layanan audit sebagai ujung rantai.

  Mengembalikan objek Flask yang siap dijalankan pada portnya sendiri.
  """
  return pembantu.buat_layanan("audit", BERIKUTNYA)
