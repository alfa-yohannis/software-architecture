"""Layanan saldo pada versi tanpa orkestrasi, langkah ketiga alur kerja.

Layanan inilah yang dimatikan pada skrip kegagalan, sebab di sinilah uang
benar-benar berpindah. Sesudah saldo dipotong, konteksnya diteruskan sendiri ke
layanan transaksi.

Cara menjalankan: python server.py
"""

from berantai import pembantu

# Potongan alur kerja yang dipegang layanan ini.
BERIKUTNYA = "transaksi"


def buat_aplikasi():
  """Membentuk aplikasi Flask layanan saldo beserta penerusnya.

  Mengembalikan objek Flask yang siap dijalankan pada portnya sendiri.
  """
  return pembantu.buat_layanan("saldo", BERIKUTNYA)
