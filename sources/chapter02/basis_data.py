"""Menyiapkan basis data contoh untuk Bab 2.

Kelas BasisDataKurs mewakili berkas SQLite beserta skema dan data awalnya.
Kelas ini menjadi kolaborator paling bawah bagi keempat lapisan aplikasi,
sehingga lapisan di atasnya tidak perlu tahu nama berkas maupun cara
membukanya. Berkas ini dijalankan sekali sebelum aplikasi_tertutup.py atau
aplikasi_terbuka.py dipakai.

Cara menjalankan: python basis_data.py
"""

import sqlite3

NAMA_BERKAS = "kurs.db"

SKEMA = """
CREATE TABLE IF NOT EXISTS kurs (
  kode_asal    TEXT NOT NULL,
  kode_tujuan  TEXT NOT NULL,
  nilai        REAL NOT NULL,
  margin       REAL NOT NULL,
  PRIMARY KEY (kode_asal, kode_tujuan)
)
"""

# Kolom nilai adalah kurs dasar yang diterbitkan untuk umum, meniru JISDOR
# dari Bank Indonesia. Kolom margin adalah margin keuntungan bank, yaitu
# tambahan yang dikenakan ketika valuta asing dijual kepada nasabah. Besar
# keuntungan itulah yang bersifat komersial.
SISIPKAN_KURS = """
INSERT OR REPLACE INTO kurs (kode_asal, kode_tujuan, nilai, margin)
VALUES (?, ?, ?, ?)
"""

DATA_AWAL = [
  ("USD", "IDR", 16250.0, 75.0),
  ("EUR", "IDR", 17600.0, 90.0),
  ("SGD", "IDR", 12100.0, 60.0),
  ("IDR", "USD", 0.0000615, 0.0000004),
]


class BasisDataKurs:
  """Berkas SQLite tempat tabel kurs disimpan.

  Kelas ini hanya mengurus penyimpanan, yaitu membuka koneksi dan menyiapkan
  skema beserta data awalnya. Tidak ada aturan bisnis yang diletakkan di sini,
  sebab lapisan di atasnyalah yang menuntut aturan tersebut. Nama berkas
  disimpan sebagai atribut agar pengujian dapat menunjuk berkas lain tanpa
  menyentuh kode lapisan mana pun.
  """

  def __init__(self, nama_berkas=NAMA_BERKAS):
    """Menyimpan nama berkas yang akan dipakai seluruh koneksi berikutnya."""
    self.nama_berkas = nama_berkas

  def buka_koneksi(self):
    """Membuka koneksi baru ke berkas basis data.

    Koneksi tidak dipakai bersama antar pemanggil, sehingga setiap pembacaan
    membuka dan menutup koneksinya sendiri.
    """
    return sqlite3.connect(self.nama_berkas)

  def siapkan(self):
    """Membuat tabel kurs bila belum ada, lalu mengisi data awal.

    Pengisian memakai INSERT OR REPLACE agar berkas ini aman dijalankan
    berulang tanpa menggandakan baris.
    """
    koneksi = self.buka_koneksi()
    koneksi.execute(SKEMA)
    koneksi.executemany(SISIPKAN_KURS, DATA_AWAL)
    koneksi.commit()
    koneksi.close()


if __name__ == "__main__":
  basis = BasisDataKurs()
  basis.siapkan()
  print("Basis data siap:", basis.nama_berkas)
  # Keluarannya: Basis data siap: kurs.db
