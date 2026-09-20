"""Adapter yang menyimpan kurs di dalam basis data SQLite.

Adapter ini mengisi port RateSource yang sama dengan adapter_memori.py, tetapi
membaca dari berkas basis data. Logika inti tidak berubah sama sekali.

Cara menjalankan: python adapter_sqlite.py
"""

import sqlite3

NAMA_BERKAS = "kurs.db"

DATA_AWAL = [("USD", "IDR", 16250.0), ("EUR", "IDR", 17600.0)]


class SqliteRateSource:
  """Menyediakan kurs dari tabel pada berkas SQLite."""

  def __init__(self, nama_berkas=NAMA_BERKAS):
    self.nama_berkas = nama_berkas

  def siapkan(self):
    """Membuat tabel kurs lalu mengisinya dengan data awal."""
    koneksi = sqlite3.connect(self.nama_berkas)
    koneksi.execute(
      "CREATE TABLE IF NOT EXISTS kurs (asal TEXT, tujuan TEXT, nilai REAL)"
    )
    koneksi.execute("DELETE FROM kurs")
    koneksi.executemany("INSERT INTO kurs VALUES (?, ?, ?)", DATA_AWAL)
    koneksi.commit()
    koneksi.close()

  def nilai(self, kode_asal, kode_tujuan):
    """Mengembalikan nilai kurs dari tabel, atau None bila tidak ada."""
    koneksi = sqlite3.connect(self.nama_berkas)
    kursor = koneksi.execute(
      "SELECT nilai FROM kurs WHERE asal = ? AND tujuan = ?", (kode_asal, kode_tujuan)
    )
    baris = kursor.fetchone()
    koneksi.close()
    return baris[0] if baris else None


if __name__ == "__main__":
  sumber_kurs = SqliteRateSource()
  sumber_kurs.siapkan()
  print(sumber_kurs.nilai("USD", "IDR"))
  # Keluarannya: 16250.0
