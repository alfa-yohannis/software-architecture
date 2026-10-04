"""Membuat berkas gambar contoh yang diolah pipa pada bab ini.

Gambar dibuat oleh skrip, bukan diunduh, agar latihan dapat diulang pada mesin
mana pun tanpa berkas besar ikut dilacak. Jumlahnya sengaja cukup banyak, sebab
selisih antara pemrosesan mengalir dan pemrosesan sekaligus baru terlihat pada
kumpulan yang besar.

Cara menjalankan: python buat_gambar.py
"""

import pathlib
import random

from PIL import Image, ImageDraw

DIREKTORI_MASUKAN = pathlib.Path(__file__).parent / "masukan"
JUMLAH_GAMBAR = 200
LEBAR = 640
TINGGI = 480
JUMLAH_BENTUK = 12
BENIH_ACAK = 20260913


def satu_gambar(acak: random.Random) -> Image.Image:
  """Menggambar sejumlah bentuk acak di atas kanvas berwarna.

  Isinya sengaja beragam agar tahap kabur dan ambang punya sesuatu untuk
  dikerjakan. Mengembalikan objek Image berukuran LEBAR kali TINGGI.
  """
  latar = tuple(acak.randint(120, 255) for _ in range(3))
  gambar = Image.new("RGB", (LEBAR, TINGGI), latar)
  pena = ImageDraw.Draw(gambar)
  for _ in range(JUMLAH_BENTUK):
    x1, y1 = acak.randint(0, LEBAR), acak.randint(0, TINGGI)
    x2, y2 = acak.randint(0, LEBAR), acak.randint(0, TINGGI)
    warna = tuple(acak.randint(0, 120) for _ in range(3))
    if acak.random() < 0.5:
      pena.ellipse([min(x1, x2), min(y1, y2), max(x1, x2), max(y1, y2)], warna)
    else:
      pena.rectangle([min(x1, x2), min(y1, y2), max(x1, x2), max(y1, y2)], warna)
  return gambar


def tulis_berkas() -> int:
  """Menulis seluruh gambar contoh ke direktori masukan.

  Benih acaknya tetap, sehingga kumpulan gambar yang dihasilkan sama pada setiap
  mesin. Mengembalikan int berisi jumlah berkas yang ditulis.
  """
  DIREKTORI_MASUKAN.mkdir(exist_ok=True)
  acak = random.Random(BENIH_ACAK)
  for nomor in range(1, JUMLAH_GAMBAR + 1):
    satu_gambar(acak).save(DIREKTORI_MASUKAN / f"contoh_{nomor:03d}.png")
  return JUMLAH_GAMBAR


if __name__ == "__main__":
  print(f"{tulis_berkas()} gambar ditulis ke {DIREKTORI_MASUKAN.name}/")
  # Keluarannya: 200 gambar ditulis ke masukan/
