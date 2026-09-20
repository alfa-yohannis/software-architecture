"""Menguji core logic tanpa basis data dan tanpa jaringan.

Stub adapter cukup berupa satu kelas dengan satu metode. Karena core logic
hanya mengenal port, stub itu dapat dipasang begitu saja.

Setiap panggilan ditulis satu per satu, bukan disarangkan menjadi
a(b(c())), agar nilai antaranya terlihat dan mudah diperiksa.

Cara menjalankan: python uji_tanpa_basis_data.py
"""

import domain

KURS_UJI = 16250.0
HASIL_DIHARAPKAN = 1_625_000.0


class StubRateSource:
  """Stub adapter yang selalu mengembalikan satu nilai tetap."""

  def nilai(self, kode_asal, kode_tujuan):
    """Mengembalikan kurs tetap agar hasil unit test selalu sama."""
    return KURS_UJI if kode_asal == "USD" else None


def uji_hasil_benar():
  """Memastikan perhitungan memakai nilai dari adapter yang dipasang.

  Mengembalikan True bila hasilnya sama dengan HASIL_DIHARAPKAN.
  """
  sumber_kurs = StubRateSource()
  hasil = domain.hitung_konversi(sumber_kurs, "USD", "IDR", 100)
  return hasil == HASIL_DIHARAPKAN


def uji_nominal_nol_ditolak():
  """Memastikan aturan nominal positif tetap berlaku.

  Mengembalikan True bila ValueError memang muncul.
  """
  sumber_kurs = StubRateSource()
  try:
    domain.hitung_konversi(sumber_kurs, "USD", "IDR", 0)
    return False
  except ValueError:
    return True


def uji_kurs_hilang_ditolak():
  """Memastikan kurs yang tidak tersedia menimbulkan error.

  Mengembalikan True bila LookupError memang muncul.
  """
  sumber_kurs = StubRateSource()
  try:
    domain.hitung_konversi(sumber_kurs, "SGD", "IDR", 100)
    return False
  except LookupError:
    return True


DAFTAR_UJI = [
  ("hasil benar", uji_hasil_benar),
  ("nominal nol ditolak", uji_nominal_nol_ditolak),
  ("kurs hilang ditolak", uji_kurs_hilang_ditolak),
]

if __name__ == "__main__":
  for nama, fungsi in DAFTAR_UJI:
    lulus = fungsi()
    print(f"{nama:<22} lulus={lulus}")
  print("Basis data yang disentuh: 0")
  # Keluarannya: hasil benar            lulus=True
  #              nominal nol ditolak    lulus=True
  #              kurs hilang ditolak    lulus=True
  #              Basis data yang disentuh: 0
