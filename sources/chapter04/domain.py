"""Logika inti konversi mata uang beserta port yang dibutuhkannya.

Berkas ini tidak menyebut satu pun teknologi penyimpanan. Kebutuhannya
dinyatakan sebagai port, yaitu antarmuka SumberKurs. Adapter yang mengisi port
tersebut berada di berkas lain.

Cara menjalankan: python domain.py
"""

from typing import Protocol

BATAS_NOMINAL_WAJAR = 1_000_000_000


class SumberKurs(Protocol):
  """Port keluaran yang dibutuhkan logika inti.

  Siapa pun yang menyediakan metode ini dapat dipasang, baik penyimpanan dalam
  memori, basis data, maupun tiruan untuk pengujian.
  """

  def nilai(self, kode_asal, kode_tujuan):
    """Mengembalikan nilai kurs, atau None bila pasangannya tidak ada."""


def hitung_konversi(sumber, kode_asal, kode_tujuan, nominal):
  """Menghitung hasil konversi setelah memeriksa dua aturan bisnis.

  Sumber kurs diterima sebagai argumen, bukan dibuat di dalam fungsi. Karena itu
  fungsi ini tidak pernah mengetahui teknologi penyimpanan yang dipakai.
  """
  if nominal <= 0:
    raise ValueError("Nominal harus lebih besar dari nol")
  if nominal > BATAS_NOMINAL_WAJAR:
    raise ValueError("Nominal melewati batas wajar")
  kurs = sumber.nilai(kode_asal, kode_tujuan)
  if kurs is None:
    raise LookupError(f"Kurs {kode_asal} ke {kode_tujuan} tidak tersedia")
  return nominal * kurs


if __name__ == "__main__":
  print("Modul ini tidak dapat berjalan sendiri, sebab membutuhkan sebuah adapter.")
