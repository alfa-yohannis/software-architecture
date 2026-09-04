"""Adapter yang menyimpan kurs di dalam memori.

Adapter ini mengisi port SumberKurs memakai sebuah kamus biasa. Dipakai untuk
menjalankan aplikasi tanpa basis data apa pun.

Cara menjalankan: python adapter_memori.py
"""

KURS = {
  ("USD", "IDR"): 16250.0,
  ("EUR", "IDR"): 17600.0,
}


class SumberMemori:
  """Menyediakan kurs dari kamus di dalam memori."""

  def nilai(self, kode_asal, kode_tujuan):
    """Mengembalikan nilai kurs dari kamus, atau None bila tidak ada."""
    return KURS.get((kode_asal, kode_tujuan))


if __name__ == "__main__":
  print(SumberMemori().nilai("USD", "IDR"))
  # Keluarannya: 16250.0
