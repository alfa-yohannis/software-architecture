"""Basis data bersama yang dipakai ketiga bidang domain Bab 11.

Satu berkas SQLite memuat tiga tabel, yaitu kurs, pesanan, dan tagihan.
Ketiga bidang domain menulis dan membaca berkas yang sama, baik ketika
seluruhnya berada di dalam satu proses maupun ketika sudah dipecah menjadi
tiga layanan. Basis data bersama itulah ciri utama service-based architecture,
sekaligus yang membedakannya dari mikroservis yang basis datanya terpisah.

Mode jurnal sengaja dibiarkan pada bawaannya, bukan WAL, sebab skrip
uji_kegagalan.py perlu mengunci berkas ini secara penuh agar pembacaan ikut
tertahan. Batas tunggu kunci dipendekkan agar kegagalannya segera ketahuan.

Cara menjalankan: python basis_data.py
"""

import pathlib
import sqlite3

BERKAS = pathlib.Path(__file__).resolve().parent / "layanan.db"
BATAS_TUNGGU_KUNCI = 1.0

SKEMA_KURS = """
CREATE TABLE kurs (
  kode   TEXT PRIMARY KEY,
  nilai  REAL NOT NULL
)
"""

SKEMA_PESANAN = """
CREATE TABLE pesanan (
  nomor      INTEGER PRIMARY KEY,
  pelanggan  TEXT NOT NULL,
  mata_uang  TEXT NOT NULL,
  nominal    REAL NOT NULL,
  status     TEXT NOT NULL
)
"""

SKEMA_TAGIHAN = """
CREATE TABLE tagihan (
  nomor_pesanan   INTEGER PRIMARY KEY,
  nominal_rupiah  REAL NOT NULL,
  pajak           REAL NOT NULL,
  total           REAL NOT NULL,
  waktu_terbit    TEXT NOT NULL
)
"""

SISIPKAN_KURS = "INSERT INTO kurs (kode, nilai) VALUES (?, ?)"

SISIPKAN_PESANAN = """
INSERT INTO pesanan (nomor, pelanggan, mata_uang, nominal, status)
VALUES (?, ?, ?, ?, ?)
"""

SISIPKAN_TAGIHAN = """
INSERT INTO tagihan
  (nomor_pesanan, nominal_rupiah, pajak, total, waktu_terbit)
VALUES (?, ?, ?, ?, ?)
"""

# Kosakata status pesanan ikut menjadi bagian skema bersama, bukan milik satu
# bidang saja, sebab bidang penagihan membaca kolom status dari tabel yang
# sama dengan bidang pemesanan.
STATUS_BARU = "baru"
STATUS_BATAL = "batal"

# Kurs dasar yang diterbitkan untuk umum, meniru JISDOR dari Bank Indonesia.
# Angkanya sama dengan yang dipakai Bab 2, agar contoh sepanjang modul ini
# tetap dapat dibandingkan.
DATA_KURS = [
  ("USD", 16250.0),
  ("EUR", 17600.0),
  ("SGD", 12100.0),
]

# Pesanan bernomor 3 sengaja berstatus batal, sebab aturan bisnis penagihan
# menolak menerbitkan tagihan atas pesanan yang sudah dibatalkan.
DATA_PESANAN = [
  (1, "Universitas Pradita", "USD", 120.0, STATUS_BARU),
  (2, "Koperasi Mahasiswa", "SGD", 450.0, STATUS_BARU),
  (3, "Panitia Wisuda", "EUR", 80.0, STATUS_BATAL),
]

# Satu tagihan disiapkan sejak awal agar permintaan baca tagihan dapat dicoba
# tanpa menerbitkannya lebih dahulu. Angkanya mengikuti aturan yang sama,
# yaitu 120 dikali 16.250 ditambah pajak sebelas persen.
DATA_TAGIHAN = [
  (1, 1950000.0, 214500.0, 2164500.0, "2026-09-20T08:00:00"),
]


def buka_koneksi() -> sqlite3.Connection:
  """Membuka koneksi baru ke berkas basis data bersama.

  Setiap pemanggil membuka koneksinya sendiri lalu menutupnya, sebab objek
  koneksi SQLite tidak aman dipakai lintas utas. Baris hasil dibungkus
  sqlite3.Row agar kolomnya dibaca memakai nama, bukan nomor urut.
  Mengembalikan objek sqlite3.Connection yang siap dipakai.
  """
  koneksi = sqlite3.connect(BERKAS, timeout=BATAS_TUNGGU_KUNCI)
  koneksi.row_factory = sqlite3.Row
  return koneksi


def siapkan() -> dict:
  """Membuat ulang ketiga tabel beserta data awalnya dari nol.

  Tabel lama dibuang lebih dahulu, sehingga latihan selalu dimulai dari
  keadaan yang sama walaupun skrip pengukuran sudah menulis banyak tagihan.
  Mengembalikan dict berisi jumlah baris awal tiap tabel.
  """
  koneksi = buka_koneksi()
  try:
    for nama_tabel in ("tagihan", "pesanan", "kurs"):
      koneksi.execute(f"DROP TABLE IF EXISTS {nama_tabel}")
    koneksi.execute(SKEMA_KURS)
    koneksi.execute(SKEMA_PESANAN)
    koneksi.execute(SKEMA_TAGIHAN)
    koneksi.executemany(SISIPKAN_KURS, DATA_KURS)
    koneksi.executemany(SISIPKAN_PESANAN, DATA_PESANAN)
    koneksi.executemany(SISIPKAN_TAGIHAN, DATA_TAGIHAN)
    koneksi.commit()
  finally:
    koneksi.close()
  return {
    "kurs": len(DATA_KURS),
    "pesanan": len(DATA_PESANAN),
    "tagihan": len(DATA_TAGIHAN),
  }


if __name__ == "__main__":
  jumlah_baris = siapkan()
  print(f"Basis data bersama : {BERKAS.name}")
  # Keluarannya: Basis data bersama : layanan.db
  for nama, jumlah in jumlah_baris.items():
    print(f"  tabel {nama:<9} {jumlah} baris")
  # Keluarannya:   tabel kurs      3 baris
