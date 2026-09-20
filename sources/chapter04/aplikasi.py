"""Merangkai logika inti dengan salah satu adapter.

Hanya berkas inilah yang mengetahui adapter mana yang dipakai. Mengganti
penyimpanan berarti mengganti satu baris di sini, bukan menyunting domain.py.

Cara menjalankan: python aplikasi.py memori
"""

import sys

import adapter_memori
import adapter_sqlite
import domain


def pilih_sumber(nama):
  """Memilih adapter sesuai nama yang diminta pengguna.

  Mengembalikan objek pemenuh port RateSource, yaitu MemoryRateSource atau
  SqliteRateSource yang tabelnya sudah disiapkan.
  """
  if nama == "memori":
    return adapter_memori.MemoryRateSource()
  sumber_kurs = adapter_sqlite.SqliteRateSource()
  sumber_kurs.siapkan()
  return sumber_kurs


if __name__ == "__main__":
  jumlah_argumen = len(sys.argv)
  nama_sumber = sys.argv[1] if jumlah_argumen > 1 else "memori"
  sumber_kurs = pilih_sumber(nama_sumber)
  hasil = domain.hitung_konversi(sumber_kurs, "USD", "IDR", 100)
  print(f"{nama_sumber}: 100 USD = {hasil:,.2f} IDR")
  # Keluarannya: memori: 100 USD = 1,625,000.00 IDR
  #              sqlite: 100 USD = 1,631,000.00 IDR
