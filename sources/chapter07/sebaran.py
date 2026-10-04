"""Ringkasan sebaran sederet angka hasil pengukuran.

Bab ini melaporkan median, persentil ke-95, dan nilai terbesar, bukan rata-rata
saja. Alasannya sama dengan Bab 2, yaitu gejala antrean dan kasus terburuk hanya
tampak pada ujung sebaran. Pada lookup kunci, ujung itulah yang menentukan
apakah sebuah susunan masih layak dipakai ketika jaringannya membesar.

Persentilnya dihitung dengan peringkat terdekat, bukan dengan penyisipan di
antara dua angka. Cara itu dipilih sebab yang diukur berupa cacah pesan dan
cacah hop, keduanya bilangan bulat, sehingga angka hasilnya tetap berupa
pengukuran yang benar-benar pernah terjadi.

Cara menjalankan: python sebaran.py
"""

import math

PERSENTIL_ATAS = 95
# Lebar kolom label, agar seluruh skrip pengukuran bab ini sejajar keluarannya.
LEBAR_LABEL = 25


def persentil(deret: list, bagian: int):
  """Mengembalikan nilai pada persentil tertentu memakai peringkat terdekat.

  Deret kosong mengembalikan nol, sebab skrip pemanggilnya tetap perlu mencetak
  satu angka walaupun tidak ada satu pun pengukuran yang masuk.
  """
  if not deret:
    return 0
  terurut = sorted(deret)
  peringkat = math.ceil(bagian / 100 * len(terurut))
  return terurut[max(peringkat - 1, 0)]


def median(deret: list) -> float:
  """Mengembalikan nilai tengah sebuah deret, atau nol bila deretnya kosong."""
  if not deret:
    return 0.0
  terurut = sorted(deret)
  tengah = len(terurut) // 2
  if len(terurut) % 2:
    return float(terurut[tengah])
  return (terurut[tengah - 1] + terurut[tengah]) / 2


def ringkas(deret: list) -> dict:
  """Mengembalikan dict berisi median, persentil ke-95, dan nilai terbesar.

  Ketiga angka itulah yang dipakai seluruh tabel pada bab ini, sehingga bentuk
  kembaliannya sengaja dibuat sama untuk semua skrip pengukuran.
  """
  return {
    "median": median(deret),
    "p95": persentil(deret, PERSENTIL_ATAS),
    "terbesar": max(deret) if deret else 0,
  }


def cetak_sebaran(judul: str, deret: list) -> None:
  """Mencetak tiga baris ringkasan sebuah deret dengan label yang seragam.

  Labelnya dipakai apa adanya pada naskah bab, sebab langkah latihan menyuruh
  mahasiswa mencatat baris keluaran ini.
  """
  angka = ringkas(deret)
  cetak_baris(f"{judul} median", f"{angka['median']:.1f}")
  cetak_baris(f"{judul} persentil ke-95", f"{angka['p95']:.1f}")
  cetak_baris(f"{judul} terbesar", f"{angka['terbesar']:.1f}")


def cetak_baris(label: str, nilai: str) -> None:
  """Mencetak satu baris laporan dengan lebar label yang seragam.

  Seluruh skrip pengukuran bab ini memakai fungsi yang sama, sehingga kolom
  titik duanya sejajar dan barisnya mudah dicatat.
  """
  print(f"  {label:<{LEBAR_LABEL}s}: {nilai}")


if __name__ == "__main__":
  contoh = [2, 2, 4, 4, 4, 6, 6, 6, 8, 12]
  print(f"Deret contoh : {contoh}")
  cetak_sebaran("Contoh", contoh)
  # Keluarannya: Contoh terbesar        : 12.0
