"""Basis data SQLite yang menjadi system of record pada contoh bab ini.

Berkas ini dipakai dua versi aplikasi dengan cara yang berbeda. Pada versi basis
data, setiap processing unit membukanya sendiri lalu membaca kurs dan menyimpan
hasil di jalur setiap tugas. Pada versi ruang, unit sama sekali tidak
membukanya, dan hanya penulis data yang menyentuhnya, itu pun sesudah hasilnya
menumpuk menjadi satu kelompok.

Perbedaan itulah yang diukur ukur_hasil.py, sedangkan akibat buruknya diukur
uji_kehilangan.py.

Cara menjalankan: python basis_data.py
"""

import sqlite3

import domain

NAMA_BERKAS = "kurs.db"
# Lama menunggu kunci berkas, dalam detik. Beberapa unit dapat menulis bersamaan
# pada jalur tulis langsung, sehingga batas bawaan lima detik terlalu pendek.
BATAS_TUNGGU_KUNCI = 30.0

SKEMA_KURS = """
CREATE TABLE IF NOT EXISTS kurs (
  kode_asal    TEXT NOT NULL,
  kode_tujuan  TEXT NOT NULL,
  nilai        REAL NOT NULL,
  PRIMARY KEY (kode_asal, kode_tujuan)
)
"""

SKEMA_HASIL = """
CREATE TABLE IF NOT EXISTS hasil (
  nomor         INTEGER PRIMARY KEY,
  unit          TEXT NOT NULL,
  nilai_rupiah  REAL NOT NULL
)
"""

SISIPKAN_KURS = """
INSERT OR REPLACE INTO kurs (kode_asal, kode_tujuan, nilai) VALUES (?, ?, ?)
"""
KUERI_KURS = "SELECT nilai FROM kurs WHERE kode_asal = ? AND kode_tujuan = ?"
KUERI_SEMUA_KURS = """
SELECT kode_asal, kode_tujuan, nilai FROM kurs ORDER BY kode_asal
"""
SISIPKAN_HASIL = "INSERT INTO hasil (nomor, unit, nilai_rupiah) VALUES (?, ?, ?)"
KUERI_NOMOR_HASIL = "SELECT nomor FROM hasil"
HAPUS_HASIL = "DELETE FROM hasil"


class BasisData:
  """Berkas SQLite beserta skema tabel kurs dan tabel hasil.

  Kelas ini hanya mengurus penyimpanan. Tidak ada aturan konversi di sini, dan
  tidak ada pengetahuan tentang tuple space. Nama berkas disimpan sebagai
  atribut agar skrip pengukuran dapat menunjuk berkas di sistem berkas lain.
  """

  def __init__(self, nama_berkas: str = NAMA_BERKAS) -> None:
    """Menyimpan nama berkas yang dipakai seluruh koneksi berikutnya.

    Koneksi tidak dibuka di sini, sebab koneksi SQLite tidak boleh dibawa
    menyeberang ke proses lain. Setiap proses membuka koneksinya sendiri.
    """
    self.nama_berkas = nama_berkas

  def buka_koneksi(self) -> sqlite3.Connection:
    """Membuka koneksi baru dengan batas tunggu kunci yang longgar.

    Mengembalikan objek sqlite3.Connection yang wajib ditutup pemanggilnya.
    """
    return sqlite3.connect(self.nama_berkas, timeout=BATAS_TUNGGU_KUNCI)

  def siapkan(self) -> int:
    """Membuat kedua tabel bila belum ada, lalu mengisi tabel kurs.

    Pengisian memakai INSERT OR REPLACE agar skrip aman dijalankan berulang.
    Tabel hasil dikosongkan, sehingga setiap latihan mulai dari keadaan yang sama.
    Mengembalikan int berisi jumlah baris kurs yang tersedia.
    """
    koneksi = self.buka_koneksi()
    koneksi.execute(SKEMA_KURS)
    koneksi.execute(SKEMA_HASIL)
    koneksi.executemany(SISIPKAN_KURS, [(asal, tujuan, nilai) for (asal, tujuan),
                                        nilai in domain.KURS.items()])
    koneksi.execute(HAPUS_HASIL)
    koneksi.commit()
    koneksi.close()
    return len(domain.KURS)

  def kosongkan_hasil(self) -> None:
    """Menghapus seluruh baris hasil sebelum satu percobaan dimulai.

    Tanpa langkah ini, baris dari percobaan sebelumnya ikut terhitung sebagai
    tersimpan. Tidak mengembalikan apa pun.
    """
    koneksi = self.buka_koneksi()
    koneksi.execute(HAPUS_HASIL)
    koneksi.commit()
    koneksi.close()

  def daftar_kurs(self) -> list[tuple[str, str, float]]:
    """Membaca seluruh kurs, dipakai pembaca data saat mengisi ruang.

    Mengembalikan list berisi tuple kode asal, kode tujuan, dan nilai kurs.
    """
    koneksi = self.buka_koneksi()
    baris = koneksi.execute(KUERI_SEMUA_KURS).fetchall()
    koneksi.close()
    return baris

  def baca_kurs(self, koneksi: sqlite3.Connection, kode_asal: str,
                kode_tujuan: str) -> float | None:
    """Membaca satu kurs lewat koneksi yang sudah terbuka.

    Koneksi diterima dari pemanggil agar pengukuran tidak ikut menghitung biaya
    membuka berkas. Perlakuan itu menguntungkan basis data, sehingga selisih yang
    terukur adalah batas bawahnya. Mengembalikan float berisi kurs, atau None
    bila pasangan mata uang tidak ditemukan.
    """
    baris = koneksi.execute(KUERI_KURS, (kode_asal, kode_tujuan)).fetchone()
    return None if baris is None else baris[0]

  def simpan_hasil(self, koneksi: sqlite3.Connection,
                   daftar_baris: list[tuple[int, str, float]]) -> int:
    """Menyisipkan beberapa baris hasil dalam satu transaksi.

    Satu commit untuk banyak baris jauh lebih murah daripada satu commit per
    baris, dan itulah yang dimanfaatkan penulis data. Mengembalikan int berisi
    jumlah baris yang disisipkan.
    """
    koneksi.executemany(SISIPKAN_HASIL, daftar_baris)
    koneksi.commit()
    return len(daftar_baris)

  def nomor_tersimpan(self) -> set[int]:
    """Membaca nomor seluruh tugas yang hasilnya sudah tersimpan.

    Mengembalikan set berisi nomor tugas, dipakai untuk menghitung tugas yang
    sudah dijawab tetapi tidak pernah sampai ke basis data.
    """
    koneksi = self.buka_koneksi()
    nomor = {baris[0] for baris in koneksi.execute(KUERI_NOMOR_HASIL)}
    koneksi.close()
    return nomor


if __name__ == "__main__":
  basis = BasisData()
  jumlah_kurs = basis.siapkan()
  print(f"Tabel kurs  : {jumlah_kurs} baris")
  # Keluarannya: Tabel kurs  : 3 baris
  print(f"Tabel hasil : {len(basis.nomor_tersimpan())} baris")
  # Keluarannya: Tabel hasil : 0 baris
