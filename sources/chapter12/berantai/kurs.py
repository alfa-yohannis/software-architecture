"""Layanan kurs pada versi tanpa orkestrasi, langkah kedua workflow.

Sesudah kurs jual dihitung, konteksnya diteruskan sendiri ke layanan saldo.
Tetapan BERIKUTNYA di bawah inilah yang wajib disunting ketika sebuah langkah
baru disisipkan sesudah langkah kurs.

Cara menjalankan: python server.py
"""

from berantai import pembantu

# Potongan workflow yang dipegang layanan ini.
BERIKUTNYA = "saldo"


def buat_aplikasi():
  """Membentuk aplikasi Flask layanan kurs beserta layanan berikutnya.

  Mengembalikan objek Flask yang siap dijalankan pada port-nya sendiri.
  """
  return pembantu.buat_layanan("kurs", BERIKUTNYA)
