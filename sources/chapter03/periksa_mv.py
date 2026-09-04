"""Mengukur ketergantungan antar komponen pada keempat varian Model-View-*.

Skrip ini membaca kode tanpa menjalankannya. Ketergantungan diambil dari
parameter konstruktor setiap kelas, sebab di situlah setiap komponen menyatakan
apa yang dibutuhkannya. Yang paling menentukan adalah ketergantungan View,
karena View yang tidak bergantung pada apa pun dapat diganti tiruan saat diuji.

Cara menjalankan: python periksa_mv.py
"""

import ast

BERKAS_VARIAN = ["mvc.py", "mvp.py", "mvvm.py", "mvi.py"]
NAMA_VIEW = "View"


def baca_pohon(nama_berkas):
  """Mengurai satu berkas Python menjadi pohon sintaks tanpa menjalankannya."""
  with open(nama_berkas, encoding="utf-8") as berkas:
    return ast.parse(berkas.read(), filename=nama_berkas)


def kumpulkan_kelas(pohon):
  """Mengumpulkan seluruh kelas tingkat modul beserta simpulnya."""
  return {s.name: s for s in pohon.body if isinstance(s, ast.ClassDef)}


def parameter_konstruktor(simpul_kelas):
  """Mengambil nama parameter __init__ sebuah kelas, tanpa self.

  Parameter konstruktor dipakai sebagai ukuran ketergantungan, sebab di situlah
  sebuah komponen menyatakan komponen lain yang dibutuhkannya.
  """
  for anggota in simpul_kelas.body:
    if isinstance(anggota, ast.FunctionDef) and anggota.name == "__init__":
      return [a.arg for a in anggota.args.args if a.arg != "self"]
  return []


def fungsi_bebas(pohon):
  """Mengumpulkan nama fungsi tingkat modul di luar kelas mana pun."""
  return [s.name for s in pohon.body if isinstance(s, ast.FunctionDef)]


def laporkan(nama_berkas):
  """Mencetak ketergantungan setiap kelas pada satu varian."""
  pohon = baca_pohon(nama_berkas)
  kelas = kumpulkan_kelas(pohon)
  ketergantungan = {n: parameter_konstruktor(s) for n, s in kelas.items()}
  total = sum(len(v) for v in ketergantungan.values())

  print(f"{nama_berkas}")
  for nama_kelas in sorted(ketergantungan):
    butuh = ketergantungan[nama_kelas] or ["tidak ada"]
    print(f"  {nama_kelas:<14} butuh: {', '.join(butuh)}")
  print(f"  Fungsi di luar kelas : {fungsi_bebas(pohon) or 'tidak ada'}")
  print(f"  Total ketergantungan : {total}")
  print(f"  Ketergantungan View  : {len(ketergantungan.get(NAMA_VIEW, []))}")


if __name__ == "__main__":
  for berkas in BERKAS_VARIAN:
    laporkan(berkas)
    print()
  # Keluarannya: Ketergantungan View  : 1
