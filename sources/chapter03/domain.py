"""Logika konversi mata uang yang dipakai bersama oleh keempat varian.

Berkas ini tidak mengenal antarmuka mana pun. Keempat varian Model-View-*
memakai fungsi yang sama dari sini, sehingga perbandingannya adil.

Cara menjalankan: python domain.py
"""

BATAS_NOMINAL_WAJAR = 1_000_000_000

KURS = {
  ("USD", "IDR"): 16250.0,
  ("EUR", "IDR"): 17600.0,
  ("SGD", "IDR"): 12100.0,
}


def cari_kurs(kode_asal, kode_tujuan):
  """Mengembalikan nilai kurs, atau None bila pasangan mata uang tidak ada."""
  return KURS.get((kode_asal, kode_tujuan))


def hitung_konversi(kode_asal, kode_tujuan, nominal):
  """Menghitung hasil konversi setelah memeriksa dua aturan bisnis.

  Aturan yang diperiksa adalah nominal harus positif dan tidak melewati batas
  wajar. Pemeriksaan diletakkan di sini agar keempat varian memakai aturan yang
  sama persis.
  """
  if nominal <= 0:
    raise ValueError("Nominal harus lebih besar dari nol")
  if nominal > BATAS_NOMINAL_WAJAR:
    raise ValueError("Nominal melewati batas wajar")
  nilai = cari_kurs(kode_asal, kode_tujuan)
  if nilai is None:
    raise LookupError(f"Kurs {kode_asal} ke {kode_tujuan} tidak tersedia")
  return nominal * nilai


if __name__ == "__main__":
  print(hitung_konversi("USD", "IDR", 100))
  # Keluarannya: 1625000.0
