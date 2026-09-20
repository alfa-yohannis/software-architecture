"""Adapter yang menyimpan kurs di dalam memori.

Adapter ini memenuhi port RateSource memakai sebuah in-memory map. Dipakai
untuk menjalankan aplikasi tanpa basis data apa pun.

Angkanya sengaja dibedakan dari adapter_sqlite.py, yaitu kurs penutupan hari
sebelumnya. Perbedaan itu membuat keluaran aplikasi menunjukkan adapter mana
yang sedang terpasang.

Cara menjalankan: python adapter_memori.py
"""

KURS = {
  ("USD", "IDR"): 16250.0,
  ("EUR", "IDR"): 17600.0,
}


class MemoryRateSource:
  """Menyediakan kurs dari in-memory map, tanpa menyentuh basis data."""

  def nilai(self, kode_asal, kode_tujuan):
    """Mengembalikan nilai kurs dari kamus, atau None bila tidak ada."""
    return KURS.get((kode_asal, kode_tujuan))


if __name__ == "__main__":
  sumber_kurs = MemoryRateSource()
  kurs = sumber_kurs.nilai("USD", "IDR")
  print(kurs)
  # Keluarannya: 16250.0
