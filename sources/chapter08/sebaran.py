"""Ringkasan sebaran angka, dipakai bersama oleh seluruh skrip pengukuran Bab 8.

Rata-rata menyembunyikan antrean, sedangkan median, persentil ke-95, dan nilai
terbesar memperlihatkannya. Ketiganya dikumpulkan di satu file agar setiap
skrip melaporkan bentuk yang sama.

Cara menjalankan: file ini diimpor, bukan dijalankan langsung.
"""

import statistics

PERSENTIL = 95
PERSEN = 100.0


def persentil(daftar: list, peringkat: int = PERSENTIL) -> float:
  """Menghitung persentil satu daftar angka tanpa pustaka luar.

  Daftar diurutkan lebih dahulu, lalu nilainya diambil pada peringkat yang
  diminta, tanpa menyisipkan nilai di antara dua angka. Mengembalikan float
  berisi nilai persentilnya, atau nol bila daftarnya kosong.
  """
  if not daftar:
    return 0.0
  terurut = sorted(daftar)
  indeks_terakhir = len(terurut) - 1
  letak = round(peringkat / PERSEN * indeks_terakhir)
  return terurut[letak]


def ringkas(daftar: list) -> dict:
  """Meringkas satu daftar angka menjadi median, persentil ke-95, dan terbesar.

  Daftar kosong diringkas menjadi nol, sehingga skrip pemanggil tidak perlu
  memeriksanya sendiri. Mengembalikan dict dengan key median, p95, terbesar,
  dan jumlah.
  """
  if not daftar:
    return {"median": 0.0, "p95": 0.0, "terbesar": 0.0, "jumlah": 0}
  return {
    "median": statistics.median(daftar),
    "p95": persentil(daftar),
    "terbesar": max(daftar),
    "jumlah": len(daftar),
  }
