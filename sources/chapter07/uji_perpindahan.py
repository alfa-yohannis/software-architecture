"""Menghitung berapa kunci berpindah pemilik ketika satu node bergabung.

Letak kunci dapat dihitung dengan dua cara. Cara pertama memakai sisa bagi
jumlah node, yaitu pemiliknya adalah pengenal kunci modulo jumlah node. Cara
kedua memakai identifier ring, yaitu pemiliknya adalah penerus titik kunci itu.
Keduanya sama-sama menghitung, dan keduanya sama-sama tidak membutuhkan indeks
terpusat.

Bedanya baru terlihat ketika jumlah node berubah. Pada cara sisa bagi, pembagi
ikut berubah, sehingga hampir seluruh kunci berpindah pemilik. Pada ring, yang
berpindah hanya kunci di dalam busur milik node baru. Angka itulah yang dicetak
skrip ini, dan itulah alasan ring dipakai Chord.

Cara menjalankan:
  python uji_perpindahan.py
  python uji_perpindahan.py 16 17
"""

import sys

import cincin
import domain

JUMLAH_NODE_AWAL = 8
JUMLAH_NODE_AKHIR = 9
PERSEN_PENUH = 100.0


def pemilik_sisa_bagi(kunci: str, jumlah_node: int) -> int:
  """Menentukan pemilik kunci lewat sisa bagi jumlah node.

  Cara ini paling mudah ditulis, dan dipakai banyak sistem sebelum consistent
  hashing dikenal. Mengembalikan int berisi nomor node pemiliknya.
  """
  titik_kunci = cincin.pengenal_dari(kunci)
  return titik_kunci % jumlah_node


def titik_seluruh_node(jumlah_node: int) -> list[tuple[int, int]]:
  """Menghitung titik ring setiap node lalu mengurutkannya.

  Urutan dipakai agar pencarian penerus cukup berjalan satu arah. Mengembalikan
  list berisi pasangan titik ring dan nomor node, terurut menaik.
  """
  daftar = []
  for nomor in range(jumlah_node):
    nama = cincin.nama_simpul(nomor)
    titik = cincin.pengenal_dari(nama)
    daftar.append((titik, nomor))
  daftar.sort()
  return daftar


def pemilik_ring(kunci: str, daftar_titik: list[tuple[int, int]]) -> int:
  """Menentukan pemilik kunci lewat penerusnya pada identifier ring.

  Penerus adalah node pertama yang titiknya tidak mendahului titik kunci.
  Kunci yang titiknya melewati node terakhir kembali ke node pertama, sebab
  ring-nya melingkar. Mengembalikan int berisi nomor node pemiliknya.
  """
  titik_kunci = cincin.pengenal_dari(kunci)
  for titik, nomor in daftar_titik:
    if titik >= titik_kunci:
      return nomor
  titik_pertama, nomor_pertama = daftar_titik[0]
  return nomor_pertama


def hitung_perpindahan(jumlah_awal: int, jumlah_akhir: int) -> dict:
  """Mencacah kunci yang berpindah pemilik pada kedua cara perhitungan.

  Mengembalikan dict berisi jumlah kunci, jumlah yang berpindah pada cara sisa
  bagi, dan jumlah yang berpindah pada cara ring.
  """
  daftar_kunci = domain.daftar_kunci()
  titik_awal = titik_seluruh_node(jumlah_awal)
  titik_akhir = titik_seluruh_node(jumlah_akhir)
  pindah_sisa_bagi = 0
  pindah_ring = 0
  for kunci in daftar_kunci:
    lama_sisa_bagi = pemilik_sisa_bagi(kunci, jumlah_awal)
    baru_sisa_bagi = pemilik_sisa_bagi(kunci, jumlah_akhir)
    if lama_sisa_bagi != baru_sisa_bagi:
      pindah_sisa_bagi += 1
    lama_ring = pemilik_ring(kunci, titik_awal)
    baru_ring = pemilik_ring(kunci, titik_akhir)
    if lama_ring != baru_ring:
      pindah_ring += 1
  return {
    "jumlah_kunci": len(daftar_kunci),
    "pindah_sisa_bagi": pindah_sisa_bagi,
    "pindah_ring": pindah_ring,
  }


def laporkan(jumlah_awal: int, jumlah_akhir: int) -> None:
  """Mencetak hasil cacahan beserta persentasenya.

  Tidak mengembalikan apa pun, sebab keluarannya memang dibaca langsung oleh
  mahasiswa pada lembar isian latihan.
  """
  hasil = hitung_perpindahan(jumlah_awal, jumlah_akhir)
  jumlah_kunci = hasil["jumlah_kunci"]
  persen_sisa_bagi = hasil["pindah_sisa_bagi"] / jumlah_kunci * PERSEN_PENUH
  persen_ring = hasil["pindah_ring"] / jumlah_kunci * PERSEN_PENUH

  print(f"Jumlah node                : {jumlah_awal} lalu {jumlah_akhir}")
  print(f"Jumlah kunci               : {jumlah_kunci}")
  print(f"Pindah pemilik, sisa bagi  : {hasil['pindah_sisa_bagi']}"
        f" ({persen_sisa_bagi:.1f} persen)")
  # Keluarannya: Pindah pemilik, sisa bagi  : 26 (100.0 persen)
  print(f"Pindah pemilik, ring       : {hasil['pindah_ring']}"
        f" ({persen_ring:.1f} persen)")
  # Keluarannya: Pindah pemilik, ring       : 1 (3.8 persen)


def baca_jumlah_node(argumen: list[str]) -> tuple[int, int]:
  """Membaca jumlah node awal dan akhir dari argumen baris perintah.

  Tanpa argumen, dipakai delapan lalu sembilan node. Mengembalikan tuple berisi
  kedua angka tersebut.
  """
  if len(argumen) < 3:
    return JUMLAH_NODE_AWAL, JUMLAH_NODE_AKHIR
  awal = int(argumen[1])
  akhir = int(argumen[2])
  return awal, akhir


if __name__ == "__main__":
  jumlah_awal, jumlah_akhir = baca_jumlah_node(sys.argv)
  laporkan(jumlah_awal, jumlah_akhir)
