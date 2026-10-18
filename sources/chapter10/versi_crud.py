"""Versi CRUD, yaitu satu tabel keadaan sekarang untuk perintah dan kueri.

Perintah membaca saldo, memeriksanya, lalu menimpa baris yang sama. Kueri
membaca baris yang sama pula. Bentuk inilah yang paling sering ditulis, dan
bab ini memakainya sebagai pembanding bagi kedua versi lainnya.

Akibat penimpaan tersebut, nilai lama hilang begitu perintah berikutnya
dijalankan. Kehilangan itu bukan kelalaian, melainkan pilihan bentuk
penyimpanannya, dan akibatnya diukur pada Latihan 3.

Cara menjalankan: python versi_crud.py
"""

import pathlib
import sqlite3

import domain

BERKAS_BAKU = pathlib.Path(__file__).parent / "dompet_crud.db"

SKEMA = """
CREATE TABLE dompet (
  pemilik TEXT PRIMARY KEY,
  saldo INTEGER NOT NULL
)
"""

ALASAN_TANPA_RIWAYAT = (
  "tabel dompet hanya menyimpan saldo terakhir, nilai sebelumnya tertimpa"
)


class BukuBesarCrud:
  """Buku besar dompet yang menyimpan satu baris keadaan per pemilik."""

  def __init__(self, berkas: pathlib.Path = BERKAS_BAKU) -> None:
    """Membuka koneksi yang dipakai ulang oleh seluruh perintah dan kueri.

    Koneksinya sengaja dibuka sekali, sebab yang diukur bab ini adalah biaya
    model penyimpanannya, bukan biaya membuka berkas.
    """
    self.berkas = pathlib.Path(berkas)
    self.koneksi = sqlite3.connect(self.berkas)

  def siapkan(self) -> None:
    """Membentuk ulang tabel keadaan agar pengukuran mulai dari kosong.

    VACUUM dijalankan sesudahnya, sebab menghapus tabel hanya melepas halaman
    ke daftar bebas dan tidak mengecilkan berkasnya. Tanpa langkah itu, ukuran
    berkas yang dilaporkan masih membawa sisa pengukuran sebelumnya.
    """
    self.koneksi.execute("DROP TABLE IF EXISTS dompet")
    self.koneksi.execute(SKEMA)
    self.koneksi.commit()
    self.koneksi.execute("VACUUM")

  def jalankan(self, perintah: domain.Perintah) -> int:
    """Menimpa baris saldo sesudah aturan bisnisnya dipenuhi.

    Saldo lama dibaca lebih dahulu sebab aturan bisnis membutuhkannya, lalu
    nilai barunya menimpa nilai lama pada baris yang sama. Mengembalikan int
    berisi saldo baru, dan melempar domain.SaldoTidakCukup bila ditolak.
    """
    kursor = self.koneksi.execute(
      "SELECT saldo FROM dompet WHERE pemilik = ?", (perintah.pemilik,)
    )
    baris = kursor.fetchone()
    saldo_lama = baris[0] if baris else 0
    saldo_baru = domain.periksa_perintah(saldo_lama, perintah)
    self.koneksi.execute(
      "INSERT INTO dompet (pemilik, saldo) VALUES (?, ?) "
      "ON CONFLICT(pemilik) DO UPDATE SET saldo = excluded.saldo",
      (perintah.pemilik, saldo_baru),
    )
    self.koneksi.commit()
    return saldo_baru

  def baca_saldo(self, pemilik: str) -> int:
    """Membaca saldo dari tabel yang sama dengan yang ditulis perintah.

    Satu pembacaan indeks utama sudah cukup, sehingga versi inilah yang
    biasanya tercatat paling murah pada Latihan 1. Mengembalikan int berisi
    saldo sekarang, atau nol bila pemiliknya belum pernah menyetor.
    """
    kursor = self.koneksi.execute(
      "SELECT saldo FROM dompet WHERE pemilik = ?", (pemilik,)
    )
    baris = kursor.fetchone()
    return baris[0] if baris else 0

  def jawab_saldo_pada(self, pemilik: str, batas_waktu: str) -> domain.Jawaban:
    """Menolak menjawab saldo pada waktu lampau, disertai alasannya.

    Penolakan ini bukan galat program. Tabel keadaan memang tidak menyimpan
    nilai sebelumnya, sehingga pertanyaannya tidak punya bahan jawaban.
    Mengembalikan Jawaban dengan atribut bisa bernilai False.
    """
    return domain.Jawaban(False, 0, ALASAN_TANPA_RIWAYAT)

  def jawab_jumlah_perubahan(self, pemilik: str) -> domain.Jawaban:
    """Menolak menjawab berapa kali saldo berubah, disertai alasannya.

    Penimpaan tidak meninggalkan jejak berapa kali baris itu pernah ditulis.
    Mengembalikan Jawaban dengan atribut bisa bernilai False.
    """
    return domain.Jawaban(False, 0, ALASAN_TANPA_RIWAYAT)

  def ukuran_kib(self) -> float:
    """Mengembalikan float berisi ukuran berkas basis datanya dalam KiB."""
    return self.berkas.stat().st_size / 1024

  def tutup(self) -> None:
    """Menutup koneksi agar berkas basis datanya dapat dihapus atau disalin."""
    self.koneksi.close()


if __name__ == "__main__":
  buku = BukuBesarCrud()
  buku.siapkan()
  ditolak = 0
  for satu_perintah in domain.bangkitkan_perintah(100):
    try:
      buku.jalankan(satu_perintah)
    except domain.SaldoTidakCukup:
      ditolak += 1
  print(f"Saldo sekarang     : {buku.baca_saldo(domain.PEMILIK_BAKU)}")
  # Keluarannya: Saldo sekarang     : 8425000
  print(f"Perintah ditolak   : {ditolak}")
  # Keluarannya: Perintah ditolak   : 5
  print(f"Ukuran berkas      : {buku.ukuran_kib():.1f} KiB")
  # Keluarannya: Ukuran berkas      : 12.0 KiB
  jawaban = buku.jawab_jumlah_perubahan(domain.PEMILIK_BAKU)
  print(f"Jumlah perubahan   : {jawaban.alasan}")
  # Keluarannya: Jumlah perubahan   : tabel dompet hanya menyimpan saldo
  #   terakhir, nilai sebelumnya tertimpa
  buku.tutup()
