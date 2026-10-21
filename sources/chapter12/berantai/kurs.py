"""Layanan kurs pada versi tanpa orkestrasi, langkah kedua alur kerja.

Sesudah kurs jual dihitung, konteksnya diteruskan sendiri ke layanan saldo.
Tetapan BERIKUTNYA di bawah inilah yang wajib disunting ketika sebuah langkah
baru disisipkan sesudah langkah kurs.

Cara menjalankan: python server.py
"""

from berantai import pembantu

# Potongan alur kerja yang dipegang layanan ini.
BERIKUTNYA = "saldo"


def buat_aplikasi():
  """Membentuk aplikasi Flask layanan kurs beserta penerusnya.

  Mengembalikan objek Flask yang siap dijalankan pada portnya sendiri.
  """
  return pembantu.buat_layanan("kurs", BERIKUTNYA)
