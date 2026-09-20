"""Automated check, memeriksa apakah core logic benar-benar bebas dari adapter.

Klaim utama ports and adapters dapat dibuktikan salah oleh satu angka, yaitu
jumlah adapter yang disebut oleh domain.py. Menurut pola tersebut, jumlahnya
harus nol.

Kodenya dibaca sebagai pohon sintaks, bukan dijalankan, sehingga pemeriksaan
ini aman dipakai pada berkas yang sengaja dirusak saat latihan.

Cara menjalankan: python periksa_port.py
"""

import ast

BERKAS_DOMAIN = "domain.py"
BERKAS_ADAPTER = ["adapter_memori", "adapter_sqlite", "sqlite3"]


def modul_diimpor(nama_berkas):
  """Mengumpulkan seluruh nama modul yang diimpor sebuah berkas.

  Mengembalikan list berisi nama modul, misalnya ['typing'].
  """
  with open(nama_berkas, encoding="utf-8") as berkas:
    isi = berkas.read()
  pohon = ast.parse(isi, filename=nama_berkas)
  nama = []
  for simpul in ast.walk(pohon):
    if isinstance(simpul, ast.Import):
      for alias in simpul.names:
        nama.append(alias.name)
    elif isinstance(simpul, ast.ImportFrom) and simpul.module:
      nama.append(simpul.module)
  return nama


if __name__ == "__main__":
  impor = modul_diimpor(BERKAS_DOMAIN)
  pelanggaran = [modul for modul in impor if modul in BERKAS_ADAPTER]
  jumlah_pelanggaran = len(pelanggaran)
  kesimpulan = "Klaim gagal" if pelanggaran else "Klaim terpenuhi"
  print(f"Berkas diperiksa   : {BERKAS_DOMAIN}")
  print(f"Modul yang diimpor : {impor}")
  print(f"Adapter disebut    : {jumlah_pelanggaran} {pelanggaran}")
  print(kesimpulan)
  # Keluarannya: Berkas diperiksa   : domain.py
  #              Modul yang diimpor : ['typing']
  #              Adapter disebut    : 0 []
  #              Klaim terpenuhi
