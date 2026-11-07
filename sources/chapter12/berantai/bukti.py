"""Layanan bukti pada versi tanpa orkestrasi, langkah kelima alur kerja.

Sesudah teks bukti tersusun, konteksnya diteruskan sendiri ke layanan audit.

Cara menjalankan: python server.py
"""

from berantai import pembantu

# Potongan alur kerja yang dipegang layanan ini.
BERIKUTNYA = "audit"


def buat_aplikasi():
  """Membentuk aplikasi Flask layanan bukti beserta layanan berikutnya.

  Mengembalikan objek Flask yang siap dijalankan pada port-nya sendiri.
  """
  return pembantu.buat_layanan("bukti", BERIKUTNYA)
