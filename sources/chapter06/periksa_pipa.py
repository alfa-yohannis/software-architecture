"""Memeriksa apakah setiap filter benar-benar tidak mengenal tetangganya.

Skrip ini membaca kode tanpa menjalankannya. Klaim yang diuji adalah klaim
pipeline yang paling sering diucapkan, yaitu stage dapat ditambah, dibuang, atau
ditukar tanpa menyunting isi stage lain. Klaim itu jatuh bila satu filter
menyebut nama filter lain, sebab penyebutan seperti itu mengunci urutannya.

Setiap panggilan ditulis satu per satu, bukan disarangkan menjadi a(b(c())),
agar nilai antaranya terlihat saat latihan.

Cara menjalankan: python periksa_pipa.py
"""

import ast
import pathlib

BERKAS_FILTER = "penyaring.py"
BERKAS_PIPE = "pipa.py"
DIREKTORI = pathlib.Path(__file__).parent


def kumpulkan_filter(pohon: ast.Module) -> list[str]:
  """Mengumpulkan nama seluruh filter tingkat modul.

  Fungsi dihitung sebagai filter bila memuat yield, sedangkan kelas dihitung
  bila punya metode __call__. Keduanya dipakai pipe dengan cara yang sama.
  Mengembalikan list berisi namanya, berurutan seperti di dalam file-nya.
  """
  nama = []
  for simpul in pohon.body:
    if isinstance(simpul, ast.FunctionDef):
      if any(isinstance(anak, (ast.Yield, ast.YieldFrom))
             for anak in ast.walk(simpul)):
        nama.append(simpul.name)
    elif isinstance(simpul, ast.ClassDef):
      if any(isinstance(anggota, ast.FunctionDef) and anggota.name == "__call__"
             for anggota in simpul.body):
        nama.append(simpul.name)
  return nama


def penyebutan_tetangga(pohon: ast.Module, nama_filter: list[str]) -> dict:
  """Mencari filter yang menyebut nama filter lain di dalam tubuhnya.

  Penyebutan seperti itu berarti kedua filter terikat, sehingga urutannya tidak
  lagi bebas. Mengembalikan dict berisi nama filter beserta daftar tetangga yang
  disebutnya, dan kosong bila seluruhnya mandiri.
  """
  hasil = {}
  for simpul in pohon.body:
    if not isinstance(simpul, (ast.FunctionDef, ast.ClassDef)):
      continue
    disebut = {n.id for n in ast.walk(simpul) if isinstance(n, ast.Name)}
    tetangga = sorted(disebut & set(nama_filter) - {simpul.name})
    if tetangga:
      hasil[simpul.name] = tetangga
  return hasil


def hitung_baris(jalur: pathlib.Path) -> int:
  """Menghitung baris berisi pada sebuah file, tanpa baris kosong.

  Baris kosong diabaikan agar angkanya mewakili kode, bukan tata letak.
  Mengembalikan int berisi jumlah barisnya.
  """
  teks = jalur.read_text(encoding="utf-8")
  isi = teks.splitlines()
  return sum(1 for baris in isi if baris.strip())


def laporkan() -> None:
  """Mencetak hasil pemeriksaan beserta angka yang menjadi dasarnya.

  Tidak mengembalikan apa pun, sebab keluarannya memang dibaca langsung oleh
  mahasiswa pada lembar isian Latihan 1.
  """
  jalur_filter = DIREKTORI / BERKAS_FILTER
  jalur_pipe = DIREKTORI / BERKAS_PIPE
  teks = jalur_filter.read_text(encoding="utf-8")
  pohon = ast.parse(teks)
  nama_filter = kumpulkan_filter(pohon)
  terikat = penyebutan_tetangga(pohon, nama_filter)
  baris_filter = hitung_baris(jalur_filter)
  baris_pipe = hitung_baris(jalur_pipe)

  print(f"Filter ditemukan      : {len(nama_filter)}")
  # Keluarannya: Filter ditemukan      : 5
  for nama in nama_filter:
    print(f"  {nama}")
  print(f"Filter menyebut filter: {len(terikat)} {terikat}")
  # Keluarannya: Filter menyebut filter: 0 {}
  print(f"Baris filter          : {baris_filter}")
  print(f"Baris pipe            : {baris_pipe}")


if __name__ == "__main__":
  laporkan()
