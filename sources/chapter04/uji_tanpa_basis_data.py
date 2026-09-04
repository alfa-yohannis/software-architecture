"""Menguji logika inti tanpa basis data dan tanpa jaringan.

Adapter tiruan cukup berupa satu kelas dengan satu metode. Karena logika inti
hanya mengenal port, adapter tiruan tersebut dapat dipasang begitu saja.

Cara menjalankan: python uji_tanpa_basis_data.py
"""

import domain

KURS_UJI = 16250.0


class SumberTiruan:
  """Adapter tiruan yang selalu mengembalikan satu nilai tetap."""

  def nilai(self, kode_asal, kode_tujuan):
    """Mengembalikan kurs tetap agar hasil pengujian selalu sama."""
    return KURS_UJI if kode_asal == "USD" else None


def uji_hasil_benar():
  """Memastikan perhitungan memakai nilai dari adapter yang dipasang."""
  return domain.hitung_konversi(SumberTiruan(), "USD", "IDR", 100) == 1_625_000.0


def uji_nominal_nol_ditolak():
  """Memastikan aturan nominal positif tetap berlaku."""
  try:
    domain.hitung_konversi(SumberTiruan(), "USD", "IDR", 0)
    return False
  except ValueError:
    return True


def uji_kurs_hilang_ditolak():
  """Memastikan kurs yang tidak tersedia menimbulkan galat."""
  try:
    domain.hitung_konversi(SumberTiruan(), "SGD", "IDR", 100)
    return False
  except LookupError:
    return True


if __name__ == "__main__":
  for nama, fungsi in [("hasil benar", uji_hasil_benar),
                       ("nominal nol ditolak", uji_nominal_nol_ditolak),
                       ("kurs hilang ditolak", uji_kurs_hilang_ditolak)]:
    print(f"{nama:<22} lulus={fungsi()}")
  print("Basis data yang disentuh: 0")
  # Keluarannya: hasil benar            lulus=True
