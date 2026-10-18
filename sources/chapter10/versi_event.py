"""Versi event sourcing, yaitu hanya event yang disimpan.

Tidak ada satu pun kolom saldo yang ditimpa. Setiap perintah yang diterima
menambah satu baris pada tabel event, dan saldo sekarang dihitung ulang
dengan melipat baris tersebut satu per satu.

Penghitungan ulang dari awal menjadi mahal ketika logya panjang, sehingga
tabel snapshot disediakan. Snapshot menyimpan hasil lipatan sampai satu nomor
urut tertentu, sehingga penghitungan berikutnya cukup melanjutkan dari sana.

Cara menjalankan: python versi_event.py
"""

import pathlib
import sqlite3

import domain

BERKAS_BAKU = pathlib.Path(__file__).parent / "dompet_event.db"

SKEMA_EVENT = """
CREATE TABLE event (
  urutan INTEGER PRIMARY KEY AUTOINCREMENT,
  pemilik TEXT NOT NULL,
  jenis TEXT NOT NULL,
  nominal INTEGER NOT NULL,
  waktu TEXT NOT NULL
)
"""

SKEMA_SNAPSHOT = """
CREATE TABLE snapshot (
  pemilik TEXT PRIMARY KEY,
  urutan INTEGER NOT NULL,
  saldo INTEGER NOT NULL,
  jumlah_perubahan INTEGER NOT NULL,
  total_setor INTEGER NOT NULL,
  total_bayar INTEGER NOT NULL,
  waktu_terakhir TEXT NOT NULL
)
"""

INDEKS_EVENT = (
  "CREATE INDEX indeks_pemilik ON event (pemilik, urutan)"
)

BACA_EVENT = (
  "SELECT urutan, jenis, nominal, waktu FROM event "
  "WHERE pemilik = ? AND urutan > ? ORDER BY urutan"
)

BACA_SAMPAI_WAKTU = (
  "SELECT jenis, nominal, waktu FROM event "
  "WHERE pemilik = ? AND waktu <= ? ORDER BY urutan"
)

SIMPAN_SNAPSHOT = """
INSERT INTO snapshot
  (pemilik, urutan, saldo, jumlah_perubahan, total_setor, total_bayar,
   waktu_terakhir)
VALUES (?, ?, ?, ?, ?, ?, ?)
ON CONFLICT(pemilik) DO UPDATE SET
  urutan = excluded.urutan,
  saldo = excluded.saldo,
  jumlah_perubahan = excluded.jumlah_perubahan,
  total_setor = excluded.total_setor,
  total_bayar = excluded.total_bayar,
  waktu_terakhir = excluded.waktu_terakhir
"""


class BukuBesarEvent:
  """Buku besar dompet yang hanya menyimpan event beserta snapshotnya."""

  def __init__(self, berkas: pathlib.Path = BERKAS_BAKU,
               pakai_snapshot: bool = True) -> None:
    """Membuka koneksi lalu mencatat apakah snapshot boleh dibaca.

    Argumen pakai_snapshot dipakai skrip pengukuran untuk mematikan snapshot
    tanpa menghapus isinya, sehingga kedua jalur menghadapi log yang sama
    persis.
    """
    self.berkas = pathlib.Path(berkas)
    self.koneksi = sqlite3.connect(self.berkas)
    self.pakai_snapshot = pakai_snapshot

  def siapkan(self) -> None:
    """Membentuk ulang tabel event, tabel snapshot, dan indeksnya.

    VACUUM dijalankan sesudahnya, sebab menghapus tabel hanya melepas halaman
    ke daftar bebas dan tidak mengecilkan berkasnya. Tanpa langkah itu, ukuran
    berkas yang dilaporkan masih membawa sisa pengukuran sebelumnya.
    """
    self.koneksi.execute("DROP TABLE IF EXISTS event")
    self.koneksi.execute("DROP TABLE IF EXISTS snapshot")
    self.koneksi.execute(SKEMA_EVENT)
    self.koneksi.execute(SKEMA_SNAPSHOT)
    self.koneksi.execute(INDEKS_EVENT)
    self.koneksi.commit()
    self.koneksi.execute("VACUUM")

  def titik_mulai(self, pemilik: str) -> tuple[int, domain.Ringkasan]:
    """Menentukan dari mana penghitungan ulang layak dimulai.

    Bila snapshot dimatikan atau belum ada, penghitungan mulai dari nomor urut
    nol, yaitu dari event pertama. Mengembalikan tuple berisi nomor urut
    terakhir yang sudah terlipat beserta Ringkasan pada nomor urut itu.
    """
    if not self.pakai_snapshot:
      return 0, domain.RINGKASAN_KOSONG
    kursor = self.koneksi.execute(
      "SELECT urutan, saldo, jumlah_perubahan, total_setor, total_bayar, "
      "waktu_terakhir FROM snapshot WHERE pemilik = ?", (pemilik,)
    )
    baris = kursor.fetchone()
    if not baris:
      return 0, domain.RINGKASAN_KOSONG
    return baris[0], domain.Ringkasan(*baris[1:])

  def susun_ringkasan(self, pemilik: str) -> tuple[int, domain.Ringkasan]:
    """Menghitung ulang model baca dengan melipat event satu per satu.

    Lipatannya memakai domain.terapkan, fungsi yang sama dengan yang dipakai
    proyeksi versi CQRS. Mengembalikan tuple berisi nomor urut event
    terakhir yang terbaca beserta Ringkasan hasil lipatannya.
    """
    urutan, ringkasan = self.titik_mulai(pemilik)
    for nomor, jenis, nominal, waktu in self.koneksi.execute(
        BACA_EVENT, (pemilik, urutan)):
      ringkasan = domain.terapkan(ringkasan, jenis, nominal, waktu)
      urutan = nomor
    return urutan, ringkasan

  def jalankan(self, perintah: domain.Perintah) -> int:
    """Menambah satu baris event sesudah aturan bisnisnya dipenuhi.

    Saldo untuk pemeriksaan aturan bisnis disusun ulang lebih dahulu, sebab
    tidak ada kolom saldo yang dapat dibaca langsung. Mengembalikan int berisi
    saldo baru, dan melempar domain.SaldoTidakCukup bila ditolak.
    """
    _, ringkasan = self.susun_ringkasan(perintah.pemilik)
    saldo_baru = domain.periksa_perintah(ringkasan.saldo, perintah)
    self.koneksi.execute(
      "INSERT INTO event (pemilik, jenis, nominal, waktu) "
      "VALUES (?, ?, ?, ?)",
      (perintah.pemilik, perintah.jenis, perintah.nominal, perintah.waktu),
    )
    self.koneksi.commit()
    return saldo_baru

  def catat_event(self, perintah: domain.Perintah) -> None:
    """Menambah event tanpa memeriksa aturan bisnisnya lebih dahulu.

    Metode ini hanya dipakai skrip pengukuran untuk menyusun log panjang
    dengan cepat, misalnya seratus ribu event. Perintah dari pengguna tetap
    melewati jalankan, sehingga aturan bisnisnya tidak dapat dilangkahi.
    """
    self.koneksi.execute(
      "INSERT INTO event (pemilik, jenis, nominal, waktu) "
      "VALUES (?, ?, ?, ?)",
      (perintah.pemilik, perintah.jenis, perintah.nominal, perintah.waktu),
    )

  def simpan_snapshot(self, pemilik: str) -> int:
    """Menyimpan hasil lipatan sampai event terakhir yang ada saat ini.

    Snapshot bukan sumber kebenaran, melainkan singkatan yang boleh dibuang
    dan dibentuk ulang kapan saja dari event log. Mengembalikan int berisi
    nomor urut event terakhir yang tercakup snapshot tersebut.
    """
    urutan, ringkasan = self.susun_ringkasan(pemilik)
    self.koneksi.execute(SIMPAN_SNAPSHOT, (
      pemilik, urutan, ringkasan.saldo, ringkasan.jumlah_perubahan,
      ringkasan.total_setor, ringkasan.total_bayar, ringkasan.waktu_terakhir,
    ))
    self.koneksi.commit()
    return urutan

  def baca_saldo(self, pemilik: str) -> int:
    """Menghitung saldo sekarang dari event log, bukan dari kolom saldo.

    Inilah biaya tetap versi ini, yaitu setiap kueri menuntut penghitungan
    ulang. Mengembalikan int berisi saldo sesudah seluruh event terlipat.
    """
    return self.susun_ringkasan(pemilik)[1].saldo

  def jawab_saldo_pada(self, pemilik: str, batas_waktu: str) -> domain.Jawaban:
    """Menjawab saldo pada waktu lampau dengan melipat event sampai sana.

    Snapshot sengaja dilewati di sini, sebab snapshot mewakili keadaan
    sekarang, sedangkan pertanyaannya menyangkut keadaan lampau. Mengembalikan
    Jawaban dengan atribut bisa bernilai True.
    """
    ringkasan = domain.RINGKASAN_KOSONG
    for jenis, nominal, waktu in self.koneksi.execute(
        BACA_SAMPAI_WAKTU, (pemilik, batas_waktu)):
      ringkasan = domain.terapkan(ringkasan, jenis, nominal, waktu)
    return domain.Jawaban(True, ringkasan.saldo,
                          f"melipat event sampai {batas_waktu}")

  def jawab_jumlah_perubahan(self, pemilik: str) -> domain.Jawaban:
    """Menjawab berapa kali saldo berubah dengan mencacah baris event.

    Pertanyaan ini tidak perlu diduga saat merancang penyimpanan, sebab
    bahannya memang tersimpan seluruhnya. Mengembalikan Jawaban dengan atribut
    bisa bernilai True.
    """
    kursor = self.koneksi.execute(
      "SELECT COUNT(*) FROM event WHERE pemilik = ?", (pemilik,)
    )
    return domain.Jawaban(True, kursor.fetchone()[0],
                          "mencacah baris pada event log")

  def jumlah_event(self) -> int:
    """Mengembalikan int berisi banyaknya baris pada seluruh event log."""
    return self.koneksi.execute("SELECT COUNT(*) FROM event").fetchone()[0]

  def ukuran_kib(self) -> float:
    """Mengembalikan float berisi ukuran berkas basis datanya dalam KiB."""
    return self.berkas.stat().st_size / 1024

  def tutup(self) -> None:
    """Menutup koneksi agar berkas basis datanya dapat dihapus atau disalin."""
    self.koneksi.close()


if __name__ == "__main__":
  buku = BukuBesarEvent()
  buku.siapkan()
  ditolak = 0
  for satu_perintah in domain.bangkitkan_perintah(100):
    try:
      buku.jalankan(satu_perintah)
    except domain.SaldoTidakCukup:
      ditolak += 1
  print(f"Saldo sekarang     : {buku.baca_saldo(domain.PEMILIK_BAKU)}")
  # Keluarannya: Saldo sekarang     : 8425000
  print(f"Event tersimpan    : {buku.jumlah_event()}")
  # Keluarannya: Event tersimpan: 95
  print(f"Perintah ditolak   : {ditolak}")
  # Keluarannya: Perintah ditolak   : 5
  print(f"Snapshot sampai    : {buku.simpan_snapshot(domain.PEMILIK_BAKU)}")
  # Keluarannya: Snapshot sampai    : 95
  jawaban = buku.jawab_saldo_pada(domain.PEMILIK_BAKU,
                                  domain.waktu_perintah_ke(30))
  print(f"Saldo pada menit 30: {jawaban.nilai}")
  # Keluarannya: Saldo pada menit 30: 2132000
  buku.tutup()
