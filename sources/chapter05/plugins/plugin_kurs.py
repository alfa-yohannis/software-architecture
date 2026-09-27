"""Plugin yang menampilkan seluruh kurs yang tersedia.

Plugin ini membaca tabel yang sama dengan plugin konversi, tetapi menyajikannya
sebagai daftar. Keduanya hidup berdampingan tanpa saling mengenal.

Cara menjalankan: python inti.py kurs
"""

import domain


class RatePlugin:
  """Menyediakan perintah kurs, yaitu daftar seluruh pasangan mata uang."""

  def __init__(self, inti) -> None:
    """Menyimpan rujukan core yang diserahkan saat plugin diaktifkan."""
    self.inti = inti

  def jalankan(self, argumen: list[str]) -> str:
    """Menyusun seluruh pasangan kurs menjadi beberapa baris teks.

    Argumen sengaja diabaikan, sebab perintah ini tidak menerima parameter.
    Mengembalikan str berisi satu baris untuk setiap pasangan mata uang.
    """
    pasangan_terurut = sorted(domain.KURS.items())
    baris = []
    for (asal, tujuan), nilai in pasangan_terurut:
      baris.append(f"{asal} -> {tujuan}: {nilai:,.2f}")
    return "\n".join(baris)
