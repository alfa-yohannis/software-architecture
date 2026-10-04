"""Mengukur ongkos satu lookup kunci pada ketiga susunan jaringan.

Dua ratus lookup dijalankan, dan daftar pemintanya sama persis pada ketiga
susunan. Yang dilaporkan jumlah pesan yang melintas dan jumlah hop sampai
pemegang kunci, masing-masing berupa median, persentil ke-95, dan nilai
terbesar.

Peminta tidak pernah diambil dari node nol, sebab pada susunan client-server
node itulah indeksnya, dan indeks tidak bertanya kepada dirinya sendiri.
Aturan yang sama diberlakukan pada ketiga susunan agar bahannya sama.

Cara menjalankan:
  python ukur_pencarian.py
  python ukur_pencarian.py 32
"""

import random
import sys

import domain
import sebaran
import susunan

JUMLAH_PENCARIAN = 200
BENIH_PENCARIAN = 7


def susun_bahan(jumlah_simpul: int, jumlah_pencarian: int = JUMLAH_PENCARIAN):
  """Menyusun daftar pasangan peminta dan kunci yang akan dicari.

  Mengembalikan list berisi tupel (nomor_peminta, kunci). Daftarnya dibuat
  sekali lalu dipakai ulang oleh ketiga susunan, sehingga selisih angkanya
  benar-benar berasal dari susunannya, bukan dari bahan yang berbeda.
  """
  acak = random.Random(BENIH_PENCARIAN)
  kunci_tersedia = domain.daftar_kunci()
  bahan = []
  for _ in range(jumlah_pencarian):
    nomor_peminta = acak.randrange(1, jumlah_simpul)
    bahan.append((nomor_peminta, acak.choice(kunci_tersedia)))
  return bahan


def jalankan_pencarian(jaringan_ini, bahan: list) -> list:
  """Menjalankan seluruh lookup pada satu jaringan.

  Mengembalikan list berisi objek LookupResult, satu untuk setiap lookup.
  """
  return [jaringan_ini.cari(nomor, kunci) for nomor, kunci in bahan]


def laporkan(jaringan_ini, daftar_hasil: list) -> None:
  """Mencetak sebaran pesan dan hop satu susunan beserta catatannya."""
  pesan = [hasil.pesan for hasil in daftar_hasil]
  lompatan = [hasil.lompatan for hasil in daftar_hasil]
  terjawab = sum(1 for hasil in daftar_hasil if hasil.terjawab)
  sendiri = sum(1 for hasil in daftar_hasil if hasil.pesan == 0)
  print(f"Susunan {jaringan_ini.nama}")
  sebaran.cetak_sebaran("Pesan", pesan)
  sebaran.cetak_sebaran("Hop", lompatan)
  sebaran.cetak_baris("Lookup terjawab",
                      f"{terjawab} dari {len(daftar_hasil)}")
  sebaran.cetak_baris("Dijawab node sendiri",
                      f"{sendiri} dari {len(daftar_hasil)}")
  sebaran.cetak_baris("Sisi jaringan", f"{jaringan_ini.jumlah_sisi()}")
  print()


def ukur(jumlah_simpul: int = susunan.JUMLAH_SIMPUL_BAKU) -> None:
  """Mengukur ketiga susunan berturut-turut lalu mencetak laporannya."""
  bahan = susun_bahan(jumlah_simpul)
  print(f"Lookup per susunan         : {len(bahan)}")
  print(f"Node per jaringan          : {jumlah_simpul}")
  print(f"Kunci kurs terdaftar       : {len(domain.KURS)}\n")
  for jaringan_ini in susunan.bangun_semua(jumlah_simpul).values():
    laporkan(jaringan_ini, jalankan_pencarian(jaringan_ini, bahan))


def baca_jumlah_simpul(argumen: list[str]) -> int:
  """Membaca jumlah node dari baris perintah.

  Mengembalikan jumlah node baku bila tidak ada argumen yang diberikan,
  sehingga skrip ini tetap dapat dijalankan tanpa argumen apa pun.
  """
  if argumen:
    return int(argumen[0])
  return susunan.JUMLAH_SIMPUL_BAKU


if __name__ == "__main__":
  ukur(baca_jumlah_simpul(sys.argv[1:]))
  # Keluarannya pada susunan unstructured: Pesan median : 19.0
