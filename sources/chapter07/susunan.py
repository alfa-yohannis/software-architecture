"""Pemilih susunan jaringan beserta peragaan satu kali lookup kunci.

Ketiga susunan dibangun dari kerangka yang sama pada jaringan.py, memakai tabel
kurs yang sama pada domain.py, lalu dipanggil lewat satu metode yang sama, yaitu
cari. Karena ketiganya hanya berbeda pada cara menitipkan dan menemukan kunci,
angka yang keluar dapat dibandingkan langsung.

Cara menjalankan:
  python susunan.py daftar
  python susunan.py cari cincin USD/IDR
  python susunan.py cari tetangga EUR/IDR 16
"""

import sys

import cincin
import domain
import indeks
import tetangga

SUSUNAN = {
  "indeks": indeks.IndexNetwork,
  "tetangga": tetangga.FloodingNetwork,
  "cincin": cincin.RingNetwork,
}

JUMLAH_SIMPUL_BAKU = 8
# Node nol berperan sebagai indeks pada susunan client-server, sehingga tidak
# pernah dipakai sebagai peminta. Aturan yang sama diberlakukan pada ketiga
# susunan agar daftar pemintanya persis sama.
NOMOR_PEMINTA_CONTOH = 3
# Kunci peraga dipilih yang tidak dipegang sendiri oleh node peminta pada
# susunan mana pun, agar ketiga angkanya benar-benar dapat dibandingkan.
KUNCI_CONTOH = "EUR/IDR"


def bangun(nama: str, jumlah_simpul: int = JUMLAH_SIMPUL_BAKU):
  """Membangun satu jaringan sesuai nama susunannya.

  Mengembalikan objek turunan Jaringan yang sudah tersusun lengkap, yaitu
  node-nya tersambung dan kuncinya sudah dititipkan.
  """
  if nama not in SUSUNAN:
    raise KeyError(f"Susunan {nama} tidak dikenal, pilih {sorted(SUSUNAN)}")
  return SUSUNAN[nama](jumlah_simpul)


def bangun_semua(jumlah_simpul: int = JUMLAH_SIMPUL_BAKU) -> dict:
  """Membangun ketiga susunan sekaligus dengan jumlah node yang sama.

  Mengembalikan dict bernama susunan berisi objek jaringannya, dipakai seluruh
  skrip pengukuran agar ketiganya menghadapi keadaan yang sama.
  """
  return {nama: bangun(nama, jumlah_simpul) for nama in SUSUNAN}


def cetak_daftar(jumlah_simpul: int = JUMLAH_SIMPUL_BAKU) -> None:
  """Mencetak ringkasan ketiga susunan beserta satu contoh lookup."""
  print(f"Kunci kurs terdaftar : {len(domain.KURS)}"
        f" ({domain.TANGGAL_KURS})")
  print(f"Node per jaringan    : {jumlah_simpul}\n")
  daftar_jaringan = bangun_semua(jumlah_simpul)
  for nama, jaringan_ini in daftar_jaringan.items():
    hasil = jaringan_ini.cari(NOMOR_PEMINTA_CONTOH, KUNCI_CONTOH)
    print(f"{jaringan_ini.ringkas()}"
          f"  pesan {hasil.pesan:3d}  hop {hasil.lompatan}"
          f"  (susunan {nama})")


def cetak_satu_pencarian(nama: str, kunci: str, jumlah_simpul: int) -> None:
  """Mencetak hasil satu lookup kunci beserta letak pemegangnya."""
  jaringan_ini = bangun(nama, jumlah_simpul)
  hasil = jaringan_ini.cari(NOMOR_PEMINTA_CONTOH, kunci)
  print(f"Susunan         : {jaringan_ini.nama}")
  print(f"Peminta         : node {NOMOR_PEMINTA_CONTOH}")
  print(f"Kunci           : {kunci}")
  print(f"Pemegang kunci  : node {jaringan_ini.pemegang(kunci)}")
  print(f"Nilai ditemukan : {hasil.nilai}")
  print(f"Jumlah pesan    : {hasil.pesan}")
  print(f"Jumlah hop      : {hasil.lompatan}")


def baca_perintah(argumen: list[str]) -> int:
  """Menjalankan perintah baris perintah lalu mengembalikan kode keluarnya.

  Mengembalikan nol bila perintahnya dikenali, dan satu bila tidak.
  """
  if not argumen or argumen[0] == "daftar":
    jumlah = int(argumen[1]) if len(argumen) > 1 else JUMLAH_SIMPUL_BAKU
    cetak_daftar(jumlah)
    return 0
  if argumen[0] == "cari" and len(argumen) >= 3:
    jumlah = int(argumen[3]) if len(argumen) > 3 else JUMLAH_SIMPUL_BAKU
    cetak_satu_pencarian(argumen[1], argumen[2], jumlah)
    return 0
  print("Pemakaian: python susunan.py daftar [jumlah_simpul]")
  print("           python susunan.py cari <susunan> <kunci> [jumlah_simpul]")
  print(f"Susunan yang tersedia: {sorted(SUSUNAN)}")
  return 1


if __name__ == "__main__":
  sys.exit(baca_perintah(sys.argv[1:]))
  # Keluarannya baris pertama: Kunci kurs terdaftar : 26 (18 September 2026)
