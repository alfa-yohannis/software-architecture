"""Basis data kuota kelas, yaitu system of record pada kedua versi.

Pada versi basis data, setiap request membuka transaksi di sini, membaca
sisanya, lalu menulis balik. Pada versi space, basis data ini tidak pernah
disentuh processing unit, melainkan hanya oleh data writer yang menerima
kiriman data pump.

Berkasnya SQLite agar seluruh percobaan berjalan di satu laptop. Yang ditiru
bukan kecanggihan mesinnya, melainkan satu sifat yang dimiliki seluruh basis
data, yaitu penulisan ke satu tempat yang sama harus bergiliran.

Cara menjalankan: python basis_data.py
"""

import os
import sqlite3

import domain

NAMA_BERKAS = "krs.db"

# Lama menunggu kunci sebelum SQLite menyerah. Dinaikkan dari bawaannya, sebab
# puluhan penulis yang berebut giliran memang membuat antreannya panjang.
BATAS_TUNGGU_KUNCI = 30.0

SKEMA_KELAS = """
CREATE TABLE IF NOT EXISTS kelas (
  kode TEXT PRIMARY KEY,
  sisa INTEGER NOT NULL,
  versi INTEGER NOT NULL
)
"""

SKEMA_PENGAMBILAN = """
CREATE TABLE IF NOT EXISTS pengambilan (
  nomor INTEGER PRIMARY KEY,
  nim TEXT NOT NULL,
  kode_kelas TEXT NOT NULL,
  unit TEXT NOT NULL
)
"""

SISIPKAN_KELAS = """
INSERT INTO kelas (kode, sisa, versi) VALUES (?, ?, ?)
ON CONFLICT(kode) DO UPDATE SET sisa = excluded.sisa, versi = excluded.versi
"""

KUERI_SISA = "SELECT sisa FROM kelas WHERE kode = ?"
KUERI_SEMUA = "SELECT kode, sisa, versi FROM kelas"
UBAH_SISA = "UPDATE kelas SET sisa = ?, versi = versi + 1 WHERE kode = ?"
SISIPKAN_PENGAMBILAN = """
INSERT OR IGNORE INTO pengambilan (nomor, nim, kode_kelas, unit)
VALUES (?, ?, ?, ?)
"""
KUERI_JUMLAH_PENGAMBILAN = "SELECT COUNT(*) FROM pengambilan"
HAPUS_PENGAMBILAN = "DELETE FROM pengambilan"


class BasisData:
  """Pembungkus SQLite yang menyimpan kuota kelas beserta pengambilannya.

  Satu objek memegang satu koneksi, sehingga setiap proses atau thread wajib
  membuat objeknya sendiri. Pembagian itu meniru sambungan basis data
  sungguhan, yang juga tidak boleh dipakai bersama antar proses.
  """

  def __init__(self, jalur: str = NAMA_BERKAS) -> None:
    """Membuka koneksi beserta batas tunggu kuncinya.

    Batas tunggu dinaikkan agar penulis yang sedang mengantre tidak langsung
    gagal ketika penulis lain memegang kuncinya.
    """
    self.jalur = jalur
    self.koneksi = sqlite3.connect(jalur, timeout=BATAS_TUNGGU_KUNCI)
    self.koneksi.execute("PRAGMA journal_mode=WAL")

  def siapkan(self, per_kelas: int = None) -> None:
    """Membentuk kedua tabel lalu mengisi kuota awalnya.

    Dipanggil sekali sebelum percobaan, sehingga setiap putaran berangkat dari
    keadaan yang sama. Argumen per_kelas menaikkan kuota seluruh kelas, dipakai
    skrip pengukuran hasil. Tidak mengembalikan apa pun.
    """
    self.koneksi.execute(SKEMA_KELAS)
    self.koneksi.execute(SKEMA_PENGAMBILAN)
    self.koneksi.execute(HAPUS_PENGAMBILAN)
    for kode, kuota in domain.kuota_awal(per_kelas).items():
      self.koneksi.execute(SISIPKAN_KELAS, (kode, kuota, domain.VERSI_AWAL))
    self.koneksi.commit()

  def baca_sisa(self, kode_kelas: str) -> int:
    """Membaca sisa kuota satu kelas langsung dari cakram.

    Mengembalikan int berisi sisa kuota yang tercatat pada basis data.
    """
    baris = self.koneksi.execute(KUERI_SISA, (kode_kelas,)).fetchone()
    return baris[0]

  def baca_semua(self) -> dict:
    """Membaca seluruh baris kelas beserta versinya.

    Dipakai data reader ketika grid harus diisi ulang dari nol. Mengembalikan
    dict berisi kode kelas dan pasangan sisa beserta versinya.
    """
    hasil = {}
    for kode, sisa, versi in self.koneksi.execute(KUERI_SEMUA):
      hasil[kode] = (sisa, versi)
    return hasil

  def layani(self, request: domain.Request, unit: str) -> domain.Jawaban:
    """Menjalankan satu request pada basis data, membaca atau mengambil.

    Request yang hanya membaca cukup satu SELECT, sehingga tidak menyentuh
    kunci tulis sama sekali. Mengembalikan Jawaban berisi hasil beserta sisa
    kuotanya.
    """
    if request.jenis == domain.JENIS_BACA:
      sisa = self.baca_sisa(request.kode_kelas)
      return domain.Jawaban(request.nomor, True, sisa, "sisa dibaca")
    return self.ambil_kuota(request, unit)

  def ambil_kuota(self, request: domain.Request, unit: str) -> domain.Jawaban:
    """Menjalankan satu request sebagai satu transaksi basis data.

    Inilah jalur versi basis data. Pembacaan, pemeriksaan aturan, dan penulisan
    terjadi di dalam satu transaksi, sehingga dua unit tidak mungkin menjual
    kuota yang sama. Harganya setiap request menunggu giliran menulis.
    Mengembalikan Jawaban berisi hasil beserta sisa kuotanya.
    """
    try:
      self.koneksi.execute("BEGIN IMMEDIATE")
      sisa = self.baca_sisa(request.kode_kelas)
      sisa_baru = domain.kurangi_kuota(sisa, request)
      self.koneksi.execute(UBAH_SISA, (sisa_baru, request.kode_kelas))
      self.koneksi.execute(SISIPKAN_PENGAMBILAN,
                           (request.nomor, request.nim, request.kode_kelas,
                            unit))
      self.koneksi.commit()
      return domain.Jawaban(request.nomor, True, sisa_baru, "diterima")
    except domain.KuotaHabis as galat:
      self.koneksi.rollback()
      return domain.Jawaban(request.nomor, False, 0, str(galat))

  def catat_pengambilan(self, nomor: int, nim: str, kode_kelas: str,
                        unit: str) -> None:
    """Menyimpan satu pengambilan yang dikirim data writer.

    Dipakai jalur asinkron versi space, yaitu sesudah unit menjawab
    mahasiswanya. Tidak mengembalikan apa pun.
    """
    self.koneksi.execute(SISIPKAN_PENGAMBILAN, (nomor, nim, kode_kelas, unit))

  def tulis_sisa(self, kode_kelas: str, sisa: int) -> None:
    """Menimpa sisa kuota satu kelas tanpa memeriksa aturan bisnisnya.

    Dipakai data writer, sebab aturan bisnisnya sudah diperiksa unit ketika
    request dilayani. Tidak mengembalikan apa pun.
    """
    self.koneksi.execute(UBAH_SISA, (sisa, kode_kelas))

  def simpan(self) -> None:
    """Menutup satu kelompok tulisan dengan satu commit.

    Pengelompokan inilah yang membuat data writer jauh lebih murah daripada
    menulis satu per satu. Tidak mengembalikan apa pun.
    """
    self.koneksi.commit()

  def jumlah_pengambilan(self) -> int:
    """Menghitung baris pengambilan yang benar-benar tersimpan di cakram.

    Angka inilah yang dibandingkan dengan jumlah request yang dijawab, dan
    selisihnya adalah data yang lenyap. Mengembalikan int berisi jumlah baris.
    """
    return self.koneksi.execute(KUERI_JUMLAH_PENGAMBILAN).fetchone()[0]

  def tutup(self) -> None:
    """Menutup koneksi agar berkas tidak tertahan pada proses yang selesai."""
    self.koneksi.close()


def siapkan_berkas_baru(jalur: str = NAMA_BERKAS,
                        per_kelas: int = None) -> None:
  """Menghapus berkas lama lalu membentuk basis data yang masih bersih.

  Dipakai setiap skrip pengukuran sebelum putarannya dimulai, sehingga keadaan
  awalnya sama persis. Tidak mengembalikan apa pun.
  """
  for akhiran in ("", "-wal", "-shm"):
    berkas = jalur + akhiran
    if os.path.exists(berkas):
      os.remove(berkas)
  basis = BasisData(jalur)
  basis.siapkan(per_kelas)
  basis.tutup()


if __name__ == "__main__":
  siapkan_berkas_baru()
  basis_contoh = BasisData()
  print(f"Kelas mata kuliah terdaftar : {len(basis_contoh.baca_semua())}")
  daftar_request = domain.bangkitkan_request(3)
  for request_contoh in daftar_request:
    jawaban = basis_contoh.ambil_kuota(request_contoh, "unit-1")
    print(f"  request {jawaban.nomor:3d}  {request_contoh.kode_kelas}  "
          f"diterima={jawaban.diterima}  sisa={jawaban.sisa}")
  print(f"Pengambilan      : {basis_contoh.jumlah_pengambilan()}")
  basis_contoh.tutup()
