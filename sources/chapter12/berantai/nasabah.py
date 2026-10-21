"""Layanan nasabah pada versi tanpa orkestrasi, langkah pertama alur kerja.

Layanan ini menjadi pintu masuk alur kerja pemesanan valuta asing, sebab
pemanggil luar mengirim permintaannya ke sini. Sesudah nasabah diperiksa,
konteksnya diteruskan sendiri ke layanan kurs.

Cara menjalankan: python server.py
"""

from berantai import pembantu

# Potongan alur kerja yang dipegang layanan ini.
BERIKUTNYA = "kurs"


def buat_aplikasi():
  """Membentuk aplikasi Flask layanan nasabah beserta penerusnya.

  Mengembalikan objek Flask yang siap dijalankan pada portnya sendiri.
  """
  return pembantu.buat_layanan("nasabah", BERIKUTNYA)
