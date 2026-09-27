"""Automated check, memeriksa apakah core benar-benar tidak mengenal plugin.

Skrip ini membaca kode tanpa menjalankannya. Klaim yang diuji adalah klaim
microkernel yang paling sering diucapkan, yaitu menambah kemampuan cukup dengan
menambah file, tanpa menyunting core. Klaim itu dapat dibuktikan salah, sebab
satu penyebutan nama modul plugin di dalam core sudah cukup menggugurkannya.

Setiap panggilan ditulis satu per satu, bukan disarangkan menjadi a(b(c())),
agar nilai antaranya terlihat saat latihan.

Cara menjalankan: python periksa_inti.py
"""

import ast
import json
import pathlib

BERKAS_INTI = "inti.py"
POLA_MANIFES = "plugin_*.json"
DIREKTORI = pathlib.Path(__file__).parent
DIREKTORI_PLUGIN = DIREKTORI / "plugins"


def baca_penanda_plugin():
  """Mengumpulkan nama modul dan nama kelas setiap plugin dari manifest-nya.

  Keduanya diperiksa, sebab core dapat menyebut sebuah plugin lewat nama
  modulnya maupun lewat nama kelasnya. Mengembalikan dua list, yaitu daftar
  nama modul dan daftar nama kelas.
  """
  modul, kelas = [], []
  daftar_file = sorted(DIREKTORI_PLUGIN.glob(POLA_MANIFES))
  for berkas in daftar_file:
    teks = berkas.read_text(encoding="utf-8")
    isi = json.loads(teks)
    modul.append(isi["modul"])
    kelas.append(isi["kelas"])
  return modul, kelas


def kumpulkan_teks(pohon):
  """Mengumpulkan seluruh nama dan teks harfiah di dalam satu pohon sintaks.

  Keduanya diperiksa sekaligus, sebab sebuah core dapat menyebut plugin lewat
  impor langsung maupun lewat teks nama modul. Mengembalikan set berisi seluruh
  nama yang muncul.
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


def hitung_baris(jalur):
  """Menghitung baris kode sebuah file, tanpa baris kosong.

  Mengembalikan int berisi jumlah baris yang benar-benar berisi kode.
  """
  teks = jalur.read_text(encoding="utf-8")
  daftar_baris = teks.splitlines()
  jumlah = 0
  for baris in daftar_baris:
    if baris.strip():
      jumlah += 1
  return jumlah


def hitung_baris_plugin(nama_modul):
  """Menjumlahkan baris kode seluruh modul plugin yang tercatat di manifest.

  Nama modulnya berbentuk plugins.plugin_kurs, sehingga bagian terakhirnya
  dipakai sebagai nama file. Mengembalikan int berisi jumlah barisnya.
  """
  jumlah = 0
  for nama in nama_modul:
    bagian = nama.split(".")
    nama_file = bagian[-1]
    jalur = DIREKTORI_PLUGIN / f"{nama_file}.py"
    jumlah += hitung_baris(jalur)
  return jumlah


def laporkan():
  """Mencetak hasil pemeriksaan beserta angka yang menjadi dasarnya.

  Tidak mengembalikan apa pun, sebab yang dipakai mahasiswa adalah baris
  keluarannya, bukan nilai baliknya.
  """
  nama_modul, nama_kelas = baca_penanda_plugin()
  jalur_inti = DIREKTORI / BERKAS_INTI
  teks_sumber = jalur_inti.read_text(encoding="utf-8")
  pohon = ast.parse(teks_sumber)
  teks_inti = kumpulkan_teks(pohon)
  seluruh_penanda = nama_modul + nama_kelas
  penyebutan = []
  for nama in seluruh_penanda:
    if nama in teks_inti:
      penyebutan.append(nama)
  penyebutan.sort()

  jumlah_manifes = len(nama_modul)
  jumlah_penyebutan = len(penyebutan)
  baris_inti = hitung_baris(jalur_inti)
  baris_plugin = hitung_baris_plugin(nama_modul)
  bagian_plugin = baris_plugin / (baris_inti + baris_plugin)

  print(f"File core              : {BERKAS_INTI}")
  print(f"Manifest ditemukan     : {jumlah_manifes}")
  print(f"Plugin disebut core    : {jumlah_penyebutan} {penyebutan}")
  print(f"Baris core             : {baris_inti}")
  print(f"Baris seluruh plugin   : {baris_plugin}")
  print(f"Bagian plugin          : {bagian_plugin:.0%} dari kode yang dibaca")
  # Keluarannya: File core              : inti.py
  #              Manifest ditemukan     : 4
  #              Plugin disebut core    : 0 []
  #              Baris core             : 142
  #              Baris seluruh plugin   : 112
  #              Bagian plugin          : 44% dari kode yang dibaca


if __name__ == "__main__":
  laporkan()
