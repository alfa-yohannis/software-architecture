"""Memeriksa apakah inti benar-benar tidak mengenal satu pun plugin.

Skrip ini membaca kode tanpa menjalankannya. Klaim yang diuji adalah klaim
microkernel yang paling sering diucapkan, yaitu menambah kemampuan cukup dengan
menambah berkas, tanpa menyunting inti. Klaim itu dapat dibuktikan salah, sebab
satu penyebutan nama modul plugin di dalam inti sudah cukup untuk menggugurkannya.

Cara menjalankan: python periksa_inti.py
"""

import ast
import json
import pathlib

BERKAS_INTI = "inti.py"
POLA_MANIFES = "plugin_*.json"
DIREKTORI = pathlib.Path(__file__).parent


def baca_nama_modul_plugin():
  """Mengumpulkan nama modul setiap plugin dari berkas manifesnya."""
  nama = []
  for berkas in sorted(DIREKTORI.glob(POLA_MANIFES)):
    isi = json.loads(berkas.read_text(encoding="utf-8"))
    nama.append(isi["modul"])
  return nama


def kumpulkan_teks(pohon):
  """Mengumpulkan seluruh nama dan teks harfiah di dalam satu pohon sintaks.

  Keduanya diperiksa sekaligus, sebab sebuah inti dapat menyebut plugin lewat
  impor langsung maupun lewat teks nama modul.
  """
  ditemukan = set()
  for simpul in ast.walk(pohon):
    if isinstance(simpul, ast.Name):
      ditemukan.add(simpul.id)
    elif isinstance(simpul, ast.Constant) and isinstance(simpul.value, str):
      ditemukan.add(simpul.value)
    elif isinstance(simpul, ast.Attribute):
      ditemukan.add(simpul.attr)
    elif isinstance(simpul, ast.Import):
      for alias in simpul.names:
        ditemukan.add(alias.name)
    elif isinstance(simpul, ast.ImportFrom) and simpul.module:
      ditemukan.add(simpul.module)
  return ditemukan


def hitung_baris(nama_berkas):
  """Menghitung baris kode sebuah berkas, tanpa baris kosong."""
  isi = (DIREKTORI / nama_berkas).read_text(encoding="utf-8").splitlines()
  return sum(1 for baris in isi if baris.strip())


def laporkan():
  """Mencetak hasil pemeriksaan beserta angka yang menjadi dasarnya."""
  nama_plugin = baca_nama_modul_plugin()
  pohon = ast.parse((DIREKTORI / BERKAS_INTI).read_text(encoding="utf-8"))
  teks_inti = kumpulkan_teks(pohon)
  penyebutan = sorted(n for n in nama_plugin if n in teks_inti)

  baris_inti = hitung_baris(BERKAS_INTI)
  baris_plugin = sum(hitung_baris(f"{n}.py") for n in nama_plugin)

  print(f"Berkas inti            : {BERKAS_INTI}")
  print(f"Manifes ditemukan      : {len(nama_plugin)}")
  print(f"Plugin disebut inti    : {len(penyebutan)} {penyebutan}")
  # Keluarannya: Plugin disebut inti    : 0 []
  print(f"Baris inti             : {baris_inti}")
  print(f"Baris seluruh plugin   : {baris_plugin}")
  print(f"Bagian plugin          : {baris_plugin / (baris_inti + baris_plugin):.0%}"
        " dari kode yang dibaca")


if __name__ == "__main__":
  laporkan()
