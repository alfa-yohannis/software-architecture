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
  """Mengembalikan adapter sesuai nama yang diminta."""
  if nama == "memori":
    return adapter_memori.SumberMemori()
  sumber = adapter_sqlite.SumberSqlite()
  sumber.siapkan()
  return sumber


if __name__ == "__main__":
  nama_sumber = sys.argv[1] if len(sys.argv) > 1 else "memori"
  hasil = domain.hitung_konversi(pilih_sumber(nama_sumber), "USD", "IDR", 100)
  print(f"{nama_sumber}: 100 USD = {hasil:,.2f} IDR")
  # Keluarannya: memori: 100 USD = 1,625,000.00 IDR
