"""Memeriksa apakah logika inti benar-benar bebas dari adapter.

Klaim utama ports and adapters dapat dibuktikan salah oleh satu angka, yaitu
jumlah adapter yang disebut oleh domain.py. Menurut pola tersebut, jumlahnya
harus nol.

Cara menjalankan: python periksa_port.py
"""

import ast

BERKAS_DOMAIN = "domain.py"
BERKAS_ADAPTER = ["adapter_memori", "adapter_sqlite", "sqlite3"]


def modul_diimpor(nama_berkas):
  """Mengumpulkan seluruh nama modul yang diimpor sebuah berkas."""
  with open(nama_berkas, encoding="utf-8") as berkas:
    pohon = ast.parse(berkas.read(), filename=nama_berkas)
  nama = []
  for simpul in ast.walk(pohon):
    if isinstance(simpul, ast.Import):
      nama.extend(a.name for a in simpul.names)
    elif isinstance(simpul, ast.ImportFrom) and simpul.module:
      nama.append(simpul.module)
  return nama


if __name__ == "__main__":
  impor = modul_diimpor(BERKAS_DOMAIN)
  pelanggaran = [m for m in impor if m in BERKAS_ADAPTER]
  print(f"Berkas diperiksa   : {BERKAS_DOMAIN}")
  print(f"Modul yang diimpor : {impor}")
  print(f"Adapter disebut    : {len(pelanggaran)} {pelanggaran}")
  print("Klaim terpenuhi" if not pelanggaran else "Klaim gagal")
  # Keluarannya: Adapter disebut    : 0 []
