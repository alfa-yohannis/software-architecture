"""Membuat berkas tanda air yang disatukan dengan setiap gambar keluaran.

Tanda air dibuat oleh skrip agar tidak ada berkas gambar yang perlu dilacak Git.
Bentuknya teks putih di atas latar tembus pandang, sehingga penyatuannya dengan
foto memakai alpha channel, bukan penimpaan biasa.

Cara menjalankan: python buat_tanda_air.py
"""

import pathlib

from PIL import Image, ImageDraw

BERKAS_TANDA = pathlib.Path(__file__).parent / "tanda_air.png"
TEKS = "IF231303"
LEBAR = 600
TINGGI = 160
WARNA_TEKS = (255, 255, 255, 210)
WARNA_BAYANG = (0, 0, 0, 120)
GESER_BAYANG = 4


def buat_tanda() -> pathlib.Path:
  """Menggambar teks tanda air di atas kanvas tembus pandang.

  Bayangan tipis ditambahkan agar tanda air tetap terbaca di atas foto terang
  maupun gelap. Mengembalikan Path berkas tanda air yang ditulis.
  """
  tanda = Image.new("RGBA", (LEBAR, TINGGI), (0, 0, 0, 0))
  pena = ImageDraw.Draw(tanda)
  pena.text((GESER_BAYANG, GESER_BAYANG), TEKS, fill=WARNA_BAYANG,
            font_size=110)
  pena.text((0, 0), TEKS, fill=WARNA_TEKS, font_size=110)
  tanda.save(BERKAS_TANDA)
  return BERKAS_TANDA


if __name__ == "__main__":
  berkas = buat_tanda()
  print(f"Tanda air ditulis ke {berkas.name}, ukuran {LEBAR}x{TINGGI}")
  # Keluarannya: Tanda air ditulis ke tanda_air.png, ukuran 600x160
