"""Mengukur coupling antar modul pada satu repositori Python.

Skrip ini membaca seluruh file .py di dalam satu direktori paket, lalu
menghitung tiga angka untuk setiap modul, yaitu jumlah baris, fan-out, dan
fan-in. Fan-out adalah banyaknya modul sepaket yang diimpor modul itu,
sedangkan fan-in adalah banyaknya modul sepaket yang mengimpornya.

Ketiganya dipakai sebagai keadaan awal pada dimensi maintainability. Modul
dengan fan-in besar mahal diubah, sebab perubahannya merambat ke banyak
pemanggil. Modul dengan fan-out besar sulit diuji sendirian, sebab menyeret
banyak modul lain ikut dimuat.

Impornya dibaca lewat ast, bukan lewat teks biasa, sehingga impor di dalam
fungsi dan impor bersyarat ikut terhitung. File yang gagal diurai dilaporkan
apa adanya, bukan dilewati diam-diam.

Cara menjalankan: python ukur_kopling.py ../../../exim/app
"""

import ast
import os
import sys


def kunci_baris(butir: tuple) -> int:
  """Mengembalikan int berisi jumlah baris satu butir, dipakai sebagai kunci urut."""
  return butir[1]["baris"]


def kunci_fan_in(butir: tuple) -> int:
  """Mengembalikan int berisi fan-in satu butir, dipakai sebagai kunci urut."""
  return butir[1]["fan_in"]


def kunci_fan_out(butir: tuple) -> int:
  """Mengembalikan int berisi fan-out satu butir, dipakai sebagai kunci urut."""
  return butir[1]["fan_out"]

# Direktori paket yang diukur bila tidak disebutkan di baris perintah.
JALUR_BAKU = "exim/app"
# Lebar kolom nama modul pada tabel keluaran.
LEBAR_NAMA = 18


def daftar_modul(jalur_paket: str) -> list:
  """Menyusun nama seluruh modul Python di dalam satu direktori paket.

  Nama modul diambil dari nama file-nya tanpa akhiran .py, sehingga dapat
  dicocokkan langsung dengan nama pada pernyataan impor. Mengembalikan list
  berisi nama modul, terurut menurut abjad.
  """
  daftar = []
  for nama_berkas in sorted(os.listdir(jalur_paket)):
    if not nama_berkas.endswith(".py"):
      continue
    nama_modul = nama_berkas[:-3]
    daftar.append(nama_modul)
  return daftar


def hitung_baris(jalur_berkas: str) -> int:
  """Menghitung jumlah baris satu file sumber.

  Mengembalikan int berisi jumlah baris, termasuk baris kosong dan komentar,
  sebab keduanya tetap harus dibaca orang yang mengubah modul itu.
  """
  berkas = open(jalur_berkas, encoding="utf-8")
  isi = berkas.read()
  berkas.close()
  return len(isi.splitlines())


def baca_impor_sepaket(jalur_berkas: str, nama_sepaket: list) -> set:
  """Mengumpulkan modul sepaket yang diimpor satu file.

  Hanya impor relatif yang dihitung, yaitu yang berbentuk ``from .modul
  import ...``, sebab impor itulah yang menyatakan ketergantungan di dalam
  paket yang sama. Mengembalikan set berisi nama modul sepaket.
  """
  berkas = open(jalur_berkas, encoding="utf-8")
  isi = berkas.read()
  berkas.close()
  pohon = ast.parse(isi, filename=jalur_berkas)
  terpakai = set()
  for simpul in ast.walk(pohon):
    if not isinstance(simpul, ast.ImportFrom):
      continue
    if simpul.level == 0:
      continue
    if simpul.module is not None and simpul.module in nama_sepaket:
      terpakai.add(simpul.module)
      continue
    for alias in simpul.names:
      if alias.name in nama_sepaket:
        terpakai.add(alias.name)
  return terpakai


def kumpulkan_ukuran(jalur_paket: str) -> dict:
  """Mengukur seluruh modul di dalam satu paket.

  Mengembalikan dict berisi nama modul dan dict ukurannya, yaitu baris,
  fan_out, fan_in, dan daftar modul yang diimpornya.
  """
  nama_sepaket = daftar_modul(jalur_paket)
  ukuran = {}
  for nama_modul in nama_sepaket:
    jalur_berkas = os.path.join(jalur_paket, f"{nama_modul}.py")
    impor = baca_impor_sepaket(jalur_berkas, nama_sepaket)
    ukuran[nama_modul] = {
      "baris": hitung_baris(jalur_berkas),
      "impor": sorted(impor),
      "fan_out": len(impor),
      "fan_in": 0,
    }
  for nama_modul in nama_sepaket:
    for nama_diimpor in ukuran[nama_modul]["impor"]:
      ukuran[nama_diimpor]["fan_in"] += 1
  return ukuran


def cetak_tabel(ukuran: dict) -> None:
  """Mencetak tabel ukuran seluruh modul, terurut menurut jumlah barisnya.

  Urutan menurun dipakai sebab modul terbesar biasanya menjadi calon pertama
  yang dipecah. Tidak mengembalikan apa pun.
  """
  print(f"{'Modul':<{LEBAR_NAMA}}{'Baris':>7}{'Fan-out':>9}{'Fan-in':>8}")
  daftar_terurut = sorted(ukuran.items(), key=kunci_baris, reverse=True)
  for nama_modul, angka in daftar_terurut:
    print(f"{nama_modul:<{LEBAR_NAMA}}{angka['baris']:>7}"
          f"{angka['fan_out']:>9}{angka['fan_in']:>8}")


def cetak_ringkasan(ukuran: dict) -> None:
  """Mencetak ringkasan seluruh paket beserta modul yang paling terikat.

  Tidak mengembalikan apa pun.
  """
  jumlah_modul = len(ukuran)
  jumlah_baris = sum(angka["baris"] for angka in ukuran.values())
  jumlah_sisi = sum(angka["fan_out"] for angka in ukuran.values())
  terbesar_fan_in = max(ukuran.items(), key=kunci_fan_in)
  terbesar_fan_out = max(ukuran.items(), key=kunci_fan_out)
  print()
  print(f"Jumlah modul        : {jumlah_modul}")
  print(f"Jumlah baris        : {jumlah_baris}")
  print(f"Jumlah ketergantungan: {jumlah_sisi}")
  print(f"Fan-in terbesar     : {terbesar_fan_in[0]}, "
        f"{terbesar_fan_in[1]['fan_in']} modul mengimpornya")
  print(f"Fan-out terbesar    : {terbesar_fan_out[0]}, "
        f"mengimpor {terbesar_fan_out[1]['fan_out']} modul")


if __name__ == "__main__":
  if len(sys.argv) > 1:
    jalur_paket_utama = sys.argv[1]
  else:
    jalur_paket_utama = JALUR_BAKU
  print(f"Paket diukur        : {jalur_paket_utama}\n")
  ukuran_utama = kumpulkan_ukuran(jalur_paket_utama)
  cetak_tabel(ukuran_utama)
  cetak_ringkasan(ukuran_utama)
