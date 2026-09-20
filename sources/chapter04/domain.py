"""Logika inti konversi mata uang beserta port yang dibutuhkannya.

Berkas ini tidak menyebut satu pun teknologi penyimpanan. Kebutuhannya
dinyatakan sebagai port, yaitu antarmuka RateSource. Adapter yang memenuhi port
tersebut berada di berkas lain.

Cara menjalankan: python domain.py
"""

from typing import Protocol

# Nominal satu transaksi penukaran dibatasi agar salah ketik tidak lolos.
# Satu miliar dipilih sebab penukaran ritel tidak pernah sebesar itu.
BATAS_KEWAJARAN_NOMINAL = 1_000_000_000


class RateSource(Protocol):
  """Outbound port yang dibutuhkan core logic.

  Kelas apa pun yang punya metode nilai dapat dipasang sebagai adapter,
  misalnya kamus di dalam memori, tabel SQLite, atau stub untuk pengujian.
  """

  def nilai(self, kode_asal, kode_tujuan):
    """Mengembalikan nilai kurs, atau None bila pasangannya tidak ada."""


def hitung_konversi(sumber_kurs, kode_asal, kode_tujuan, nominal):
  """Menghitung hasil konversi setelah memeriksa dua aturan bisnis.

  Sumber kurs diterima sebagai argumen, bukan dibuat di dalam fungsi. Karena itu
  fungsi ini tidak pernah mengetahui teknologi storage yang dipakai.
  """
  if nominal <= 0:
    raise ValueError("Nominal harus lebih besar dari nol")
  if nominal > BATAS_KEWAJARAN_NOMINAL:
    raise ValueError(
      f"Nominal melewati batas kewajaran, yaitu {BATAS_KEWAJARAN_NOMINAL:,}")
  kurs = sumber_kurs.nilai(kode_asal, kode_tujuan)
  if kurs is None:
    raise LookupError(f"Kurs {kode_asal} ke {kode_tujuan} tidak tersedia")
  return nominal * kurs


if __name__ == "__main__":
  print("Modul ini tidak dapat berjalan sendiri, sebab membutuhkan sebuah adapter.")
