"""Plugin yang menampilkan seluruh kurs yang tersedia.

Plugin ini membaca tabel yang sama dengan plugin konversi, tetapi menyajikannya
sebagai daftar. Keduanya hidup berdampingan tanpa saling mengenal.

Cara menjalankan: python inti.py kurs
"""

import domain


def jalankan(argumen):
  """Menyusun seluruh pasangan kurs menjadi beberapa baris teks."""
  baris = [f"{asal} -> {tujuan}: {nilai:,.2f}"
           for (asal, tujuan), nilai in sorted(domain.KURS.items())]
  return "\n".join(baris)
