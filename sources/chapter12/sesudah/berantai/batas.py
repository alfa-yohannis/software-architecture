"""Layanan batas pada versi tanpa orkestrasi, sisipan baru di tengah rantai.

Langkah pemeriksaan batas harian harus berdiri sesudah layanan kurs, sebab
angka rupiah yang diperiksanya baru dihitung di sana. Menambahkan berkas ini
saja belum cukup, sebab layanan kurs yang memegang nama penerusnya, sehingga
layanan kurs yang sudah berjalan ikut wajib disunting dan dipasang ulang.

Cara menjalankan: python server.py
"""

from berantai import pembantu

# Potongan alur kerja yang dipegang layanan ini.
BERIKUTNYA = "saldo"


def buat_aplikasi():
  """Membentuk aplikasi Flask layanan batas beserta penerusnya.

  Mengembalikan objek Flask yang siap dijalankan pada portnya sendiri.
  """
  return pembantu.buat_layanan("batas", BERIKUTNYA)
