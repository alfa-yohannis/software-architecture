"""Menaikkan jumlah node dari delapan ke enam belas, lalu menimbang pesannya.

Pertanyaan yang dijawab skrip ini hanya satu, yaitu ongkos lookup tumbuh
mengikuti jumlah node atau mengikuti logaritmanya. Jumlah node digandakan,
sehingga pertumbuhan yang sebanding dengan jumlah node bernilai dua kali,
sedangkan pertumbuhan yang sebanding dengan logaritmanya bernilai empat per
tiga kali.

Dua ratus lookup dijalankan pada setiap ukuran jaringan, dengan kunci dan
peminta yang diambil dari seed yang sama.

Cara menjalankan: python ukur_penskalaan.py
"""

import math

import sebaran
import susunan
import ukur_pencarian

UKURAN_JARINGAN = (8, 16)


def ukur_satu_ukuran(jumlah_simpul: int) -> dict:
  """Mengukur ketiga susunan pada satu ukuran jaringan.

  Mengembalikan dict bernama susunan berisi median pesan, median hop, dan
  cacah lookup yang terjawab.
  """
  bahan = ukur_pencarian.susun_bahan(jumlah_simpul)
  catatan = {}
  for nama, jaringan_ini in susunan.bangun_semua(jumlah_simpul).items():
    daftar_hasil = ukur_pencarian.jalankan_pencarian(jaringan_ini, bahan)
    catatan[nama] = {
      "nama_susunan": jaringan_ini.nama,
      "pesan": sebaran.median([hasil.pesan for hasil in daftar_hasil]),
      "hop": sebaran.median([hasil.lompatan for hasil in daftar_hasil]),
      "terjawab": sum(1 for hasil in daftar_hasil if hasil.terjawab),
      "sisi": jaringan_ini.jumlah_sisi(),
      "jumlah": len(daftar_hasil),
    }
  return catatan


def laporkan(nama: str, kecil: dict, besar: dict) -> None:
  """Mencetak perbandingan satu susunan antara jaringan kecil dan besar."""
  pertumbuhan = besar["pesan"] / kecil["pesan"] if kecil["pesan"] else 0.0
  print(f"Susunan {kecil['nama_susunan']}")
  sebaran.cetak_baris(f"Pesan median {UKURAN_JARINGAN[0]} node",
                      f"{kecil['pesan']:.1f}")
  sebaran.cetak_baris(f"Pesan median {UKURAN_JARINGAN[1]} node",
                      f"{besar['pesan']:.1f}")
  sebaran.cetak_baris("Pertumbuhan pesan", f"{pertumbuhan:.2f} kali")
  sebaran.cetak_baris(f"Hop median {UKURAN_JARINGAN[0]} node",
                      f"{kecil['hop']:.1f}")
  sebaran.cetak_baris(f"Hop median {UKURAN_JARINGAN[1]} node",
                      f"{besar['hop']:.1f}")
  sebaran.cetak_baris("Sisi jaringan",
                      f"{kecil['sisi']} lalu {besar['sisi']}")
  sebaran.cetak_baris("Lookup terjawab",
                      f"{kecil['terjawab']} lalu {besar['terjawab']}"
                      f" dari {kecil['jumlah']}")
  print()


def ukur() -> None:
  """Mengukur kedua ukuran jaringan lalu mencetak pembandingnya."""
  kecil, besar = UKURAN_JARINGAN
  bandingan_simpul = besar / kecil
  bandingan_log = math.log2(besar) / math.log2(kecil)
  print(f"Lookup per ukuran          : {ukur_pencarian.JUMLAH_PENCARIAN}")
  print(f"Ukuran jaringan diuji      : {kecil} lalu {besar} node")
  print(f"Pertumbuhan jumlah node    : {bandingan_simpul:.2f} kali")
  print(f"Pertumbuhan logaritmanya   : {bandingan_log:.2f} kali\n")
  catatan_kecil = ukur_satu_ukuran(kecil)
  catatan_besar = ukur_satu_ukuran(besar)
  for nama in catatan_kecil:
    laporkan(nama, catatan_kecil[nama], catatan_besar[nama])


if __name__ == "__main__":
  ukur()
  # Keluarannya: Pertumbuhan logaritmanya   : 1.33 kali
