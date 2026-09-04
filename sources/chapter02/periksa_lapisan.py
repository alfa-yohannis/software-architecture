"""Memeriksa susunan lapisan sebuah berkas aplikasi.

Skrip ini membaca kode tanpa menjalankannya, lalu melaporkan tiga hal. Pertama,
fungsi mana yang hanya meneruskan panggilan. Kedua, panggilan mana yang
melompati satu lapisan. Ketiga, jumlah fungsi pada setiap lapisan.

Cara menjalankan: python periksa_lapisan.py aplikasi_tertutup.py
"""

import ast
import sys

# Urutan lapisan dari atas ke bawah. Indeks dipakai untuk menghitung jarak
# lompatan antar lapisan.
URUTAN_LAPISAN = ["presentasi", "bisnis", "persistensi", "basis_data"]


def baca_modul(nama_berkas):
  """Mengurai satu berkas Python menjadi pohon sintaks.

  Berkas dibaca sebagai teks, bukan diimpor, sehingga pemeriksaan tidak
  menjalankan kode apa pun.
  """
  with open(nama_berkas, encoding="utf-8") as berkas:
    return ast.parse(berkas.read(), filename=nama_berkas)


def baca_peta_lapisan(pohon):
  """Mengambil nilai konstanta LAPISAN dari pohon sintaks.

  Peta ini ditulis eksplisit di dalam berkas aplikasi, sehingga pemeriksaan
  tidak perlu menebak lapisan sebuah fungsi dari namanya.
  """
  for simpul in pohon.body:
    if not isinstance(simpul, ast.Assign):
      continue
    for sasaran in simpul.targets:
      if isinstance(sasaran, ast.Name) and sasaran.id == "LAPISAN":
        return ast.literal_eval(simpul.value)
  raise ValueError("Berkas tidak memuat konstanta LAPISAN")


def kumpulkan_fungsi(pohon):
  """Mengumpulkan seluruh fungsi tingkat modul beserta simpulnya."""
  return {s.name: s for s in pohon.body if isinstance(s, ast.FunctionDef)}


def nama_fungsi_dipanggil(simpul):
  """Mengambil nama fungsi yang dipanggil di dalam sebuah simpul.

  Panggilan ke modul lain, misalnya basis_data.buka_koneksi, diabaikan karena
  bukan bagian dari susunan lapisan yang sedang diperiksa.
  """
  nama = []
  for anak in ast.walk(simpul):
    if isinstance(anak, ast.Call) and isinstance(anak.func, ast.Name):
      nama.append(anak.func.id)
  return nama


def apakah_penerus(simpul_fungsi):
  """Menentukan apakah sebuah fungsi hanya meneruskan panggilan.

  Fungsi disebut penerus bila tubuhnya, setelah docstring dilewati, hanya
  berisi satu pernyataan return yang isinya satu pemanggilan fungsi.
  """
  isi = [p for p in simpul_fungsi.body if not isinstance(p, ast.Expr)]
  if len(isi) != 1 or not isinstance(isi[0], ast.Return):
    return False
  return isinstance(isi[0].value, ast.Call)


def cari_lompatan(peta, fungsi):
  """Mencari panggilan yang melompati satu lapisan atau lebih.

  Lompatan dihitung dari selisih indeks lapisan pemanggil dan lapisan yang
  dipanggil. Selisih satu berarti wajar, selisih dua atau lebih berarti ada
  lapisan yang dilewati.
  """
  temuan = []
  for nama_pemanggil, simpul in fungsi.items():
    lapis_asal = peta.get(nama_pemanggil)
    if lapis_asal is None:
      continue
    for nama_tujuan in nama_fungsi_dipanggil(simpul):
      lapis_tujuan = peta.get(nama_tujuan)
      if lapis_tujuan is None:
        continue
      jarak = URUTAN_LAPISAN.index(lapis_tujuan) - URUTAN_LAPISAN.index(lapis_asal)
      if jarak >= 2:
        temuan.append((nama_pemanggil, lapis_asal, nama_tujuan, lapis_tujuan))
  return temuan


def laporkan(nama_berkas):
  """Mencetak ketiga hasil pemeriksaan untuk satu berkas aplikasi."""
  pohon = baca_modul(nama_berkas)
  peta = baca_peta_lapisan(pohon)
  fungsi = kumpulkan_fungsi(pohon)

  penerus = [n for n, s in fungsi.items() if n in peta and apakah_penerus(s)]
  bekerja = [n for n in peta if n not in penerus]

  print(f"Berkas: {nama_berkas}")
  print(f"  Jumlah fungsi berlapis : {len(peta)}")
  print(f"  Fungsi penerus         : {len(penerus)} {sorted(penerus)}")
  print(f"  Bagian penerus         : {100 * len(penerus) / len(peta):.1f} persen")
  print(f"  Fungsi bekerja         : {len(bekerja)}")

  lompatan = cari_lompatan(peta, fungsi)
  print(f"  Pelanggaran arah       : {len(lompatan)}")
  for pemanggil, asal, tujuan, tujuan_lapis in lompatan:
    print(f"    {pemanggil} ({asal}) memanggil {tujuan} ({tujuan_lapis})")


if __name__ == "__main__":
  laporkan(sys.argv[1])
  # Keluarannya: Fungsi penerus         : 1 ['susun_daftar_kurs']
