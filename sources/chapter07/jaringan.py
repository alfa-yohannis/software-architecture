"""Kerangka bersama ketiga susunan jaringan pencari kurs.

Node-nya berupa objek di dalam satu proses, bukan proses terpisah yang
berbicara lewat soket. Pilihan itu diambil sebab yang diukur bab ini adalah
jumlah pesan dan jumlah hop, bukan waktu. Soket hanya akan menambahkan
ragam penjadwalan sistem operasi ke dalam angka tersebut, tanpa mengubah satu
pun kesimpulannya, sedangkan objek di dalam satu proses memberi angka yang sama
persis pada setiap penjalanan. Sebagai gantinya, setiap perpindahan pesan
dihitung satu per satu, sehingga jalurnya tetap terbaca seperti jaringan
sungguhan.

File ini menyiapkan node, menitipkan kunci, lalu menyerahkan cara
menemukannya kepada turunan kelas Network.

Cara menjalankan: python jaringan.py
"""

import random

# Benih tetap agar susunan neighbor dan sebaran kunci sama pada setiap
# penjalanan, sehingga angka yang dilaporkan dapat diulang.
BENIH_BAKU = 2026


class LookupResult:
  """Catatan satu kali lookup kunci di dalam sebuah jaringan."""

  def __init__(self, kunci: str, nilai, pesan: int, lompatan: int) -> None:
    """Menyimpan nilai temuan beserta ongkos yang dibayar untuk menemukannya.

    Nilai None berarti lookup tidak terjawab, baik sebab pemegang kuncinya
    mati maupun sebab batas hop tercapai lebih dahulu.
    """
    self.kunci = kunci
    self.nilai = nilai
    self.pesan = pesan
    self.lompatan = lompatan

  @property
  def terjawab(self) -> bool:
    """Mengembalikan True bila lookup ini berhasil menemukan nilainya."""
    return self.nilai is not None

  def __repr__(self) -> str:
    """Mengembalikan ringkasan satu baris, dipakai saat menelusuri kesalahan."""
    return (f"LookupResult({self.kunci}, nilai={self.nilai}, "
            f"pesan={self.pesan}, hop={self.lompatan})")


class Node:
  """Satu node jaringan beserta titipan kunci dan daftar neighbor-nya."""

  def __init__(self, nomor: int) -> None:
    """Membuat node kosong yang belum mengenal satu pun neighbor.

    Titipan dan daftar neighbor sengaja dibiarkan kosong. Isinya ditentukan
    oleh susunan yang memakainya, bukan oleh node-nya sendiri, sebab justru
    perbedaan cara mengisi itulah yang dibandingkan bab ini.
    """
    self.nomor = nomor
    self.simpanan = {}
    self.tetangga = []
    self.hidup = True

  def simpan(self, kunci: str, nilai) -> None:
    """Menitipkan satu pasangan kunci dan nilai kurs kepada node ini."""
    self.simpanan[kunci] = nilai

  def ambil(self, kunci: str):
    """Mengembalikan nilai kurs yang dititipkan, atau None bila tidak ada.

    Node yang sudah dimatikan selalu mengembalikan None, sebab permintaan
    kepadanya tidak pernah sampai. Kunci yang dititipkan kepadanya ikut hilang,
    dan hilangnya kunci itulah yang diukur pada latihan ketahanan.
    """
    if not self.hidup:
      return None
    return self.simpanan.get(kunci)

  def derajat(self) -> int:
    """Mengembalikan jumlah neighbor langsung node ini."""
    return len(self.tetangga)


class Network:
  """Kerangka bersama yang dipakai ketiga susunan pada bab ini.

  Kelas ini menyiapkan node, menyediakan pengacak dengan seed tetap, lalu
  menyerahkan dua keputusan kepada turunannya. Keputusan pertama adalah cara
  menitipkan kunci, dan keputusan kedua adalah cara menemukannya kembali.
  """

  nama = "network"

  def __init__(self, jumlah_simpul: int, benih: int = BENIH_BAKU) -> None:
    """Membuat node sebanyak yang diminta lalu menyusun jaringannya.

    Benihnya tetap, sehingga sebaran kunci dan sambungan antar node sama
    persis pada setiap penjalanan.
    """
    self.jumlah_simpul = jumlah_simpul
    self.acak = random.Random(benih)
    self.simpul = [self.buat_simpul(nomor) for nomor in range(jumlah_simpul)]
    self.susun()

  def buat_simpul(self, nomor: int) -> Node:
    """Mengembalikan satu node kosong bernomor tertentu.

    Susunan yang membutuhkan node dengan bekal tambahan, misalnya finger table
    pada susunan cincin, menimpa metode ini.
    """
    return Node(nomor)

  def susun(self) -> None:
    """Menitipkan kunci lalu menyambung node sesuai susunannya."""
    raise NotImplementedError("Susunan wajib menentukan cara menitipkan kunci")

  def cari(self, nomor_peminta: int, kunci: str) -> LookupResult:
    """Mencari satu kunci mulai dari node peminta.

    Mengembalikan LookupResult berisi nilai temuan, jumlah pesan yang melintas, dan
    jumlah hop sampai pemegang kuncinya.
    """
    raise NotImplementedError("Susunan wajib menentukan cara mencari kunci")

  def matikan(self, nomor: int) -> None:
    """Mematikan satu node, meniru node yang keluar dari jaringan."""
    self.simpul[nomor].hidup = False

  def hidupkan_semua(self) -> None:
    """Menghidupkan kembali seluruh node sebelum percobaan berikutnya."""
    for simpul in self.simpul:
      simpul.hidup = True

  def pemegang(self, kunci: str) -> int:
    """Mengembalikan nomor node yang dititipi sebuah kunci, atau -1.

    Angka ini tidak pernah dipakai saat mencari, sebab tidak ada satu node
    pun yang mengetahuinya. Gunanya hanya untuk memeriksa hasil pengukuran.
    """
    for simpul in self.simpul:
      if kunci in simpul.simpanan:
        return simpul.nomor
    return -1

  def jumlah_sisi(self) -> int:
    """Mengembalikan jumlah sambungan dua arah di antara seluruh node."""
    return sum(simpul.derajat() for simpul in self.simpul) // 2

  def sambungkan(self, nomor_a: int, nomor_b: int) -> bool:
    """Menyambung dua node sebagai neighbor dua arah.

    Mengembalikan True bila sambungan itu benar-benar baru, dan False bila
    keduanya sudah bertetangga atau nomornya sama.
    """
    if nomor_a == nomor_b:
      return False
    if nomor_b in self.simpul[nomor_a].tetangga:
      return False
    self.simpul[nomor_a].tetangga.append(nomor_b)
    self.simpul[nomor_b].tetangga.append(nomor_a)
    return True

  def ringkas(self) -> str:
    """Mengembalikan satu baris ringkasan susunan, dipakai saat mencetak."""
    return (f"{self.nama:16s} node {self.jumlah_simpul:2d}"
            f"  sisi {self.jumlah_sisi():3d}"
            f"  kunci {sum(len(s.simpanan) for s in self.simpul):3d}")


if __name__ == "__main__":
  print("Modul ini hanya kerangka bersama, sehingga tidak berjalan sendiri.")
  print("Jalankan python susunan.py daftar untuk melihat ketiga susunannya.")
