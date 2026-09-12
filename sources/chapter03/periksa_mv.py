"""Mengukur dependency antar komponen pada kelima varian Model-View-*.

Skrip ini membaca kode tanpa menjalankannya. Dependency diambil dari
parameter konstruktor setiap kelas, sebab di situlah setiap komponen menyatakan
apa yang dibutuhkannya. Yang paling menentukan adalah dependency View,
karena View yang tidak bergantung pada apa pun dapat diganti tiruan saat diuji.

Cara menjalankan: python periksa_mv.py
"""

import ast

BERKAS_VARIAN = ["mvc_klasik.py", "mvc.py", "mvp.py", "mvvm.py", "mvi.py"]
NAMA_VIEW = "View"

# Parameter jendela induk berasal dari Tkinter, bukan dari pola Model-View-*.
# Parameter ini dikecualikan agar yang terhitung hanya ketergantungan antar
# komponen pola, bukan artefak pustaka antarmuka.
PARAMETER_DIKECUALIKAN = {"induk"}


def baca_pohon(nama_berkas):
  """Mengurai satu berkas Python menjadi pohon sintaks tanpa menjalankannya."""
  with open(nama_berkas, encoding="utf-8") as berkas:
    return ast.parse(berkas.read(), filename=nama_berkas)


def kumpulkan_kelas(pohon):
  """Mengumpulkan seluruh kelas tingkat modul beserta simpulnya."""
  return {s.name: s for s in pohon.body if isinstance(s, ast.ClassDef)}


def parameter_konstruktor(simpul_kelas):
  """Mengambil nama parameter __init__ sebuah kelas, tanpa self.

  Parameter konstruktor dipakai sebagai ukuran dependency, sebab di situlah
  sebuah komponen menyatakan komponen lain yang dibutuhkannya.
  """
  for anggota in simpul_kelas.body:
    if isinstance(anggota, ast.FunctionDef) and anggota.name == "__init__":
      return [a.arg for a in anggota.args.args
              if a.arg != "self" and a.arg not in PARAMETER_DIKECUALIKAN]
  return []


def fungsi_bebas(pohon):
  """Mengumpulkan nama fungsi tingkat modul di luar kelas mana pun."""
  return [s.name for s in pohon.body if isinstance(s, ast.FunctionDef)]


def laporkan(nama_berkas):
  """Mencetak dependency setiap kelas pada satu varian."""
  pohon = baca_pohon(nama_berkas)
  kelas = kumpulkan_kelas(pohon)
  dependency = {n: parameter_konstruktor(s) for n, s in kelas.items()}
  total = sum(len(v) for v in dependency.values())

  print(f"{nama_berkas}")
  for nama_kelas in sorted(dependency):
    butuh = dependency[nama_kelas] or ["tidak ada"]
    print(f"  {nama_kelas:<14} butuh: {', '.join(butuh)}")
  print(f"  Fungsi di luar kelas : {fungsi_bebas(pohon) or 'tidak ada'}")
  print(f"  Total dependency      : {total}")
  print(f"  Dependency View       : {len(dependency.get(NAMA_VIEW, []))}")


if __name__ == "__main__":
  for berkas in BERKAS_VARIAN:
    laporkan(berkas)
    print()
  # Keluarannya: Dependency View       : 1
