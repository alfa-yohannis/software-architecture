"""Berkas SQLite milik satu proses, dipakai layanan maupun monolit Bab 13.

Pola database per service menuntut setiap layanan memegang datanya sendiri.
Karena itu kelas di berkas ini tidak memuat skema maupun data milik siapa pun.
Setiap pemilik membuat objeknya sendiri dengan nama berkas dan daftar tabelnya.
Layanan nasabah membuka data/nasabah.db, layanan pesanan membuka
data/pesanan.db, layanan kurs membuka data/kurs.db, sedangkan monolit membuka
data/monolit.db yang memuat ketiga tabel sekaligus.

Perbedaan jumlah tabel itulah yang membedakan kedua versi, dan perbedaan itu
tampak langsung pada keluaran berkas ini.

Cara menjalankan: python basis_data.py
"""

import dataclasses
import pathlib
import sqlite3

DIREKTORI_DATA = pathlib.Path(__file__).parent / "data"


@dataclasses.dataclass(frozen=True)
class Tabel:
  """Satu tabel beserta skema, perintah sisip, dan isi awalnya.

  Ketiganya disatukan agar sebuah tabel dapat dipindahkan dari layanan ke
  monolit tanpa memecah definisinya. Monolit memakai objek Tabel yang sama
  persis dengan yang dipakai ketiga layanan, sehingga datanya dijamin sama dan
  yang dibandingkan benar-benar susunannya.
  """

  skema: str
  sisipkan: str
  isi_awal: list[tuple]


class BasisDataLayanan:
  """Satu berkas SQLite yang hanya boleh dibuka oleh satu proses.

  Nama berkas dan daftar tabelnya diterima dari pemiliknya. Kelas ini hanya
  tahu cara membuka dan menyiapkan berkas, sehingga tidak ada satu tabel pun
  yang dikenal dua layanan sekaligus.
  """

  def __init__(self, nama_berkas: str, tabel: list[Tabel]) -> None:
    """Menyimpan jalur berkas beserta daftar tabel milik satu proses.

    Berkas belum dibuka di sini, sebab objek ini juga dibuat oleh skrip yang
    hanya ingin tahu nama berkasnya tanpa membaca isinya. Konstruktor tidak
    mengembalikan nilai.
    """
    self.jalur = DIREKTORI_DATA / nama_berkas
    self.tabel = tabel

  def buka_koneksi(self) -> sqlite3.Connection:
    """Membuka koneksi baru ke berkas milik proses ini.

    Koneksi tidak dipakai bersama antar utas, sebab server Flask melayani
    setiap permintaan pada utasnya sendiri. Mengembalikan objek Connection yang
    wajib ditutup oleh pemanggilnya.
    """
    return sqlite3.connect(self.jalur)

  def siapkan(self) -> int:
    """Membuat seluruh tabel bila belum ada, lalu mengisi data awalnya.

    Pengisian memakai INSERT OR REPLACE agar aman diulang setiap kali proses
    dinyalakan tanpa menggandakan baris. Mengembalikan int berisi jumlah baris
    isi awal yang ditulis.
    """
    self.jalur.parent.mkdir(exist_ok=True)
    koneksi = self.buka_koneksi()
    jumlah_baris = 0
    for satu_tabel in self.tabel:
      koneksi.execute(satu_tabel.skema)
      koneksi.executemany(satu_tabel.sisipkan, satu_tabel.isi_awal)
      jumlah_baris += len(satu_tabel.isi_awal)
    koneksi.commit()
    koneksi.close()
    return jumlah_baris

  def baca(self, kueri: str, parameter: tuple) -> list[tuple]:
    """Menjalankan satu kueri baca, lalu menutup koneksinya kembali.

    Setiap pembacaan membuka koneksinya sendiri, sama seperti pada Bab 2, agar
    tidak ada koneksi yang dipakai dua utas. Mengembalikan list berisi seluruh
    baris hasil kueri.
    """
    koneksi = self.buka_koneksi()
    try:
      return koneksi.execute(kueri, parameter).fetchall()
    finally:
      koneksi.close()


def laporkan(nama_proses: str, basis: BasisDataLayanan) -> str:
  """Menyiapkan satu baris laporan tentang berkas milik sebuah proses.

  Baris inilah yang memperlihatkan pemisahan datanya, sebab jumlah tabel pada
  satu berkas menunjukkan berapa banyak pemilik yang berbagi berkas itu.
  Mengembalikan str berisi nama proses, jalur berkas, jumlah tabel, dan jumlah
  barisnya.
  """
  jumlah_baris = basis.siapkan()
  jalur = basis.jalur.relative_to(DIREKTORI_DATA.parent)
  return (f"{nama_proses:<16} {str(jalur):<17} {len(basis.tabel)} tabel, "
          f"{jumlah_baris} baris")


if __name__ == "__main__":
  import layanan_kurs
  import layanan_nasabah
  import layanan_pesanan
  import monolit

  for modul in (layanan_nasabah, layanan_pesanan, layanan_kurs, monolit):
    print(laporkan(modul.__name__, modul.BASIS_DATA))
  # Keluarannya baris pertama:
  # layanan_nasabah  data/nasabah.db   1 tabel, 3 baris
