"""Menyiapkan basis data contoh untuk Bab 2.

Berkas ini membuat tabel kurs dan mengisinya dengan data awal. Dijalankan
sekali sebelum lapisan_tertutup.py atau lapisan_terbuka.py dipakai.

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

# Kolom nilai adalah kurs referensi yang diterbitkan untuk umum, meniru JISDOR
# dari Bank Indonesia. Kolom margin adalah tambahan yang dipakai bank sendiri,
# dan angka itulah yang bersifat komersial.
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


def buka_koneksi():
  """Membuka koneksi baru ke berkas basis data.

  Koneksi tidak dipakai bersama antar pemanggil, sehingga setiap lapisan yang
  membutuhkannya memanggil fungsi ini sendiri.
  """
  return sqlite3.connect(NAMA_BERKAS)


def siapkan_basis_data():
  """Membuat tabel kurs bila belum ada, lalu mengisi data awal.

  Pengisian memakai INSERT OR REPLACE agar skrip aman dijalankan berulang.
  """
  koneksi = buka_koneksi()
  koneksi.execute(SKEMA)
  koneksi.executemany(
    SISIPKAN_KURS,
    DATA_AWAL,
  )
  koneksi.commit()
  koneksi.close()


if __name__ == "__main__":
  siapkan_basis_data()
  print("Basis data siap:", NAMA_BERKAS)
