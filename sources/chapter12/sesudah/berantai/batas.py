"""Layanan batas pada versi tanpa orkestrasi, sisipan baru di tengah rantai.

Langkah pemeriksaan batas harian harus berdiri sesudah layanan kurs, sebab
angka rupiah yang diperiksanya baru dihitung di sana. Menambahkan file ini
saja belum cukup, sebab layanan kurs yang memegang nama layanan berikutnya, sehingga
layanan kurs yang sudah berjalan ikut wajib disunting dan dipasang ulang.

Cara menjalankan: python server.py
"""

from berantai import pembantu

# Potongan alur kerja yang dipegang layanan ini.
BERIKUTNYA = "saldo"


def buat_aplikasi():
  """Membentuk aplikasi Flask layanan batas beserta layanan berikutnya.

  Mengembalikan objek Flask yang siap dijalankan pada port-nya sendiri.
  """
  return pembantu.buat_layanan("batas", BERIKUTNYA)
