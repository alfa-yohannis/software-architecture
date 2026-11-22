"""Layanan nasabah pada versi tanpa orkestrasi, langkah pertama workflow.

Layanan ini menjadi pintu masuk workflow pemesanan valuta asing, sebab
pemanggil luar mengirim request-nya ke sini. Sesudah nasabah diperiksa,
konteksnya diteruskan sendiri ke layanan kurs.

Cara menjalankan: python server.py
"""

from berantai import pembantu

# Potongan workflow yang dipegang layanan ini.
BERIKUTNYA = "kurs"


def buat_aplikasi():
  """Membentuk aplikasi Flask layanan nasabah beserta layanan berikutnya.

  Mengembalikan objek Flask yang siap dijalankan pada port-nya sendiri.
  """
  return pembantu.buat_layanan("nasabah", BERIKUTNYA)
