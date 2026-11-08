"""Ringkasan sebaran angka, dipakai bersama oleh seluruh skrip pengukuran Bab 15.

Rata-rata menyembunyikan antrean, sedangkan median, persentil ke-95, dan nilai
terbesar memperlihatkannya. Ketiganya dikumpulkan di satu file agar setiap
skrip melaporkan bentuk yang sama.

Cara menjalankan: file ini diimpor, bukan dijalankan langsung.
"""

import statistics

PERSENTIL = 95


def persentil(daftar: list, peringkat: int = PERSENTIL) -> float:
  """Menghitung persentil satu daftar angka tanpa pustaka luar.

  Daftar diurutkan lebih dahulu, lalu nilainya diambil pada peringkat yang
  diminta. Mengembalikan float berisi nilai persentilnya, atau nol bila
  daftarnya kosong.
  """
  if not daftar:
    return 0.0
  terurut = sorted(daftar)
  nomor = int(round((peringkat / 100.0) * (len(terurut) - 1)))
  return terurut[nomor]


def ringkas(daftar: list) -> dict:
  """Meringkas satu daftar angka menjadi median, persentil ke-95, dan terbesar.

  Mengembalikan dict berisi key median, p95, terbesar, dan jumlah.
  """
  if not daftar:
    return {"median": 0.0, "p95": 0.0, "terbesar": 0.0, "jumlah": 0}
  return {
    "median": statistics.median(daftar),
    "p95": persentil(daftar),
    "terbesar": max(daftar),
    "jumlah": len(daftar),
  }


def baris_ringkas(nama: str, ringkasan: dict, satuan: str = "ms") -> str:
  """Menyusun satu baris laporan yang bentuknya sama di seluruh skrip.

  Mengembalikan str berisi baris yang siap dicetak.
  """
  return (f"{nama:<30}: median {ringkasan['median']:8.4f} {satuan}"
          f"  p95 {ringkasan['p95']:8.4f}"
          f"  terbesar {ringkasan['terbesar']:9.4f}")
