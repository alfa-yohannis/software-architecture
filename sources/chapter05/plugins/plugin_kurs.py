"""Plugin yang menampilkan seluruh kurs yang tersedia.

Plugin ini membaca tabel yang sama dengan plugin konversi, tetapi menyajikannya
sebagai daftar. Keduanya hidup berdampingan tanpa saling mengenal.

Cara menjalankan: python inti.py kurs
"""

import domain


class PluginKurs:
  """Menyediakan perintah kurs, yaitu daftar seluruh pasangan mata uang."""

  def __init__(self, inti) -> None:
    """Menyimpan rujukan inti yang diserahkan saat plugin diaktifkan."""
    self.inti = inti

  def jalankan(self, argumen: list[str]) -> str:
    """Menyusun seluruh pasangan kurs menjadi beberapa baris teks.

    Argumen sengaja diabaikan, sebab perintah ini tidak menerima parameter.
    Mengembalikan str berisi satu baris untuk setiap pasangan mata uang.
    """
    baris = [f"{asal} -> {tujuan}: {nilai:,.2f}"
             for (asal, tujuan), nilai in sorted(domain.KURS.items())]
    return "\n".join(baris)
