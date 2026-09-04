"""Klien yang meminta konversi kepada server.

Klien tidak menyimpan tabel kurs dan tidak menghitung apa pun. Seluruh
pekerjaan dikerjakan server, dan klien hanya menampilkan jawabannya.

Cara menjalankan: python klien.py USD IDR 100
"""

import json
import sys
import urllib.request

ALAMAT_SERVER = "http://127.0.0.1:8000"


def minta_konversi(kode_asal, kode_tujuan, nominal):
  """Mengirim satu permintaan ke server lalu mengembalikan jawabannya."""
  alamat = f"{ALAMAT_SERVER}/?asal={kode_asal}&tujuan={kode_tujuan}&nominal={nominal}"
  with urllib.request.urlopen(alamat) as balasan:
    return json.loads(balasan.read())


if __name__ == "__main__":
  asal, tujuan, jumlah = sys.argv[1], sys.argv[2], sys.argv[3]
  jawaban = minta_konversi(asal, tujuan, jumlah)
  print(f"{jumlah} {asal} = {jawaban['hasil']:,.2f} {tujuan}")
  # Keluarannya: 100 USD = 1,625,000.00 IDR
