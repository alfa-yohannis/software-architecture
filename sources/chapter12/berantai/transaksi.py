"""Layanan transaksi pada versi tanpa orkestrasi, langkah keempat alur kerja.

Sesudah pesanan tercatat di buku transaksi, konteksnya diteruskan sendiri ke
layanan bukti.

Cara menjalankan: python server.py
"""

from berantai import pembantu

# Potongan alur kerja yang dipegang layanan ini.
BERIKUTNYA = "bukti"


def buat_aplikasi():
  """Membentuk aplikasi Flask layanan transaksi beserta penerusnya.

  Mengembalikan objek Flask yang siap dijalankan pada portnya sendiri.
  """
  return pembantu.buat_layanan("transaksi", BERIKUTNYA)
