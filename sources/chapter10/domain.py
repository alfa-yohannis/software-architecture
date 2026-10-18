"""Kontrak bersama ketiga versi buku besar dompet mahasiswa.

Dompet ini menyimpan saldo rupiah yang dipakai membayar uang kuliah. Saldonya
berubah karena dua perintah saja, yaitu setor dan bayar, sehingga domainnya
cukup kecil untuk dibaca sekali duduk tetapi tetap punya riwayat.

Modul ini memuat bentuk perintah, bentuk ringkasan, aturan bisnisnya, dan
pembangkit perintah yang dipakai seluruh skrip pengukuran. Ketiga versi
penyimpanan memakai berkas ini, sehingga perbedaan yang terukur berasal dari
cara penyimpanannya, bukan dari aturan bisnisnya.

Cara menjalankan: python domain.py
"""

import dataclasses
import datetime
import random
from typing import Protocol

PEMILIK_BAKU = "2201001"
JENIS_SETOR = "setor"
JENIS_BAYAR = "bayar"

# Nominal setoran diambil acak di antara kedua batas berikut, dalam rupiah.
SETOR_TERKECIL = 50_000
SETOR_TERBESAR = 500_000
# Pembayaran dibuat lebih kecil daripada setoran, agar saldo jarang habis dan
# urutan perintahnya tetap sama pada ketiga versi.
BAYAR_TERKECIL = 10_000
BAYAR_TERBESAR = 200_000
# Tiga dari setiap lima perintah berupa setoran. Perbandingan itu membuat
# saldonya naik perlahan, sehingga penolakan tetap ada tetapi tidak menguasai.
PELUANG_SETOR = 0.6

BENIH_BAKU = 2026
WAKTU_MULAI = datetime.datetime(2026, 3, 1, 8, 0)
JEDA_MENIT = 1


class SaldoTidakCukup(Exception):
  """Ditandai ketika pembayaran melebihi saldo yang tersedia.

  Aturan inilah yang membuat sisi perintah benar-benar bekerja. Tanpa aturan
  tersebut, sisi perintah hanya meneruskan angka ke penyimpanan, dan pemisahan
  yang dibahas bab ini kehilangan alasannya.
  """


@dataclasses.dataclass(frozen=True)
class Perintah:
  """Satu permintaan perubahan saldo yang belum tentu diterima.

  Waktunya ikut dibawa perintah, bukan diambil dari jam sistem saat perintah
  dijalankan, agar ketiga versi mencatat waktu yang sama persis.
  """

  jenis: str
  pemilik: str
  nominal: int
  waktu: str


@dataclasses.dataclass(frozen=True)
class Ringkasan:
  """Keadaan dompet yang siap dibaca tanpa penghitungan tambahan.

  Isinya sengaja lebih luas daripada saldo saja, sebab model baca memang
  dibentuk mengikuti pertanyaan yang akan datang, bukan mengikuti bentuk
  penyimpanan sisi perintah.
  """

  saldo: int
  jumlah_perubahan: int
  total_setor: int
  total_bayar: int
  waktu_terakhir: str


@dataclasses.dataclass(frozen=True)
class Jawaban:
  """Hasil satu pertanyaan riwayat beserta keterangan bila tidak terjawab.

  Versi yang tidak menyimpan riwayat tetap mengembalikan objek ini dengan
  atribut bisa bernilai False, sehingga ketidakmampuannya tercetak sebagai
  hasil pengukuran, bukan sebagai galat program yang menghentikan skrip.
  """

  bisa: bool
  nilai: int
  alasan: str


RINGKASAN_KOSONG = Ringkasan(0, 0, 0, 0, "")


class BukuBesar(Protocol):
  """Perilaku luar yang wajib sama pada ketiga versi penyimpanan.

  Skrip pengukuran hanya memanggil metode di bawah ini, sehingga ketiga versi
  dapat ditukar tanpa menyunting skripnya. Perbedaan di antara mereka murni
  terletak di balik metode yang sama.
  """

  def siapkan(self) -> None:
    """Mengosongkan lalu membentuk ulang seluruh tabel yang dipakainya."""

  def jalankan(self, perintah: Perintah) -> int:
    """Menjalankan satu perintah lalu mengembalikan int berisi saldo baru."""

  def baca_saldo(self, pemilik: str) -> int:
    """Mengembalikan int berisi saldo sekarang milik pemilik tersebut."""

  def jawab_saldo_pada(self, pemilik: str, batas_waktu: str) -> Jawaban:
    """Mengembalikan Jawaban berisi saldo pada waktu yang diminta."""

  def jawab_jumlah_perubahan(self, pemilik: str) -> Jawaban:
    """Mengembalikan Jawaban berisi berapa kali saldonya pernah berubah."""

  def tutup(self) -> None:
    """Menutup koneksi basis datanya agar berkasnya dapat dihapus."""


def periksa_perintah(saldo: int, perintah: Perintah) -> int:
  """Menerapkan aturan bisnis dompet atas satu perintah.

  Pembayaran yang melebihi saldo ditolak, sedangkan setoran selalu diterima.
  Fungsi ini dipanggil ketiga versi sebelum perubahan apa pun ditulis, sehingga
  ketiganya menolak perintah yang sama persis. Mengembalikan int berisi saldo
  sesudah perintah diterima, dan melempar SaldoTidakCukup bila ditolak.
  """
  if perintah.jenis == JENIS_SETOR:
    return saldo + perintah.nominal
  if perintah.nominal > saldo:
    raise SaldoTidakCukup(
      f"bayar {perintah.nominal} melebihi saldo {saldo}"
    )
  return saldo - perintah.nominal


def terapkan(ringkasan: Ringkasan, jenis: str, nominal: int,
             waktu: str) -> Ringkasan:
  """Melipat satu perubahan ke atas ringkasan yang sudah ada.

  Fungsi ini dipakai dua kali di tempat yang berbeda, yaitu oleh proyeksi versi
  CQRS sesudah perintah diterima, dan oleh penghitungan ulang versi event
  sourcing ketika event log dibaca ulang. Kesamaan itu disengaja, sebab
  model baca kedua versi memang harus berisi angka yang sama. Mengembalikan
  Ringkasan baru, sedangkan ringkasan masukannya tidak diubah.
  """
  if jenis == JENIS_SETOR:
    return Ringkasan(
      saldo=ringkasan.saldo + nominal,
      jumlah_perubahan=ringkasan.jumlah_perubahan + 1,
      total_setor=ringkasan.total_setor + nominal,
      total_bayar=ringkasan.total_bayar,
      waktu_terakhir=waktu,
    )
  return Ringkasan(
    saldo=ringkasan.saldo - nominal,
    jumlah_perubahan=ringkasan.jumlah_perubahan + 1,
    total_setor=ringkasan.total_setor,
    total_bayar=ringkasan.total_bayar + nominal,
    waktu_terakhir=waktu,
  )


def bangkitkan_perintah(jumlah: int, benih: int = BENIH_BAKU,
                        pemilik: str = PEMILIK_BAKU) -> list[Perintah]:
  """Menyusun deretan perintah yang sama setiap kali skrip dijalankan.

  Benih acaknya tetap, sehingga ketiga versi menerima urutan yang sama dan
  pengukurannya dapat diulang. Waktu setiap perintah maju satu menit dari
  perintah sebelumnya, sehingga pertanyaan saldo pada waktu tertentu punya
  jawaban yang pasti. Mengembalikan list berisi objek Perintah.
  """
  pengacak = random.Random(benih)
  daftar = []
  for nomor in range(jumlah):
    waktu = WAKTU_MULAI + datetime.timedelta(minutes=nomor * JEDA_MENIT)
    if pengacak.random() < PELUANG_SETOR:
      nominal = pengacak.randrange(SETOR_TERKECIL, SETOR_TERBESAR, 1_000)
      jenis = JENIS_SETOR
    else:
      nominal = pengacak.randrange(BAYAR_TERKECIL, BAYAR_TERBESAR, 1_000)
      jenis = JENIS_BAYAR
    daftar.append(Perintah(jenis, pemilik, nominal, waktu.isoformat(" ")))
  return daftar


def waktu_perintah_ke(nomor: int) -> str:
  """Menghitung waktu perintah nomor tertentu tanpa membangkitkan daftarnya.

  Skrip pertanyaan riwayat membutuhkan satu titik waktu di tengah deretan,
  misalnya perintah ke-30 dari seratus. Mengembalikan str berisi waktu dalam
  bentuk yang sama dengan yang tersimpan di dalam event log.
  """
  waktu = WAKTU_MULAI + datetime.timedelta(minutes=nomor * JEDA_MENIT)
  return waktu.isoformat(" ")


if __name__ == "__main__":
  contoh = bangkitkan_perintah(5)
  for satu in contoh:
    print(f"{satu.waktu}  {satu.jenis:<5} {satu.nominal:>8}")
  # Keluarannya baris pertama: 2026-03-01 08:00:00  setor   307000
  saldo_berjalan = 0
  for satu in contoh:
    try:
      saldo_berjalan = periksa_perintah(saldo_berjalan, satu)
    except SaldoTidakCukup as kesalahan:
      print(f"Ditolak: {kesalahan}")
  print(f"Saldo sesudah 5 perintah: {saldo_berjalan}")
  # Keluarannya: Saldo sesudah 5 perintah: 96000
