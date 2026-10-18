"""Versi CQRS, yaitu model tulis dan model baca yang disimpan terpisah.

Sisi perintah memakai tabel dompet_tulis, yang bentuknya mengikuti aturan
bisnis. Sisi kueri memakai tabel ringkasan_baca, yang bentuknya mengikuti
pertanyaan yang akan datang. Keduanya dijembatani proyeksi, yaitu fungsi yang
melipat perubahan ke atas baris ringkasan sesudah perintah diterima.

Proyeksi di sini dijalankan langsung sesudah perintah, agar hasil latihan dapat
diulang. Pilihan lain disediakan lewat argumen proyeksi_langsung bernilai
False, dan pilihan itulah yang memperlihatkan jeda antara kedua model.

Cara menjalankan: python versi_cqrs.py
"""

import pathlib
import sqlite3

import domain

BERKAS_BAKU = pathlib.Path(__file__).parent / "dompet_cqrs.db"

SKEMA_TULIS = """
CREATE TABLE dompet_tulis (
  pemilik TEXT PRIMARY KEY,
  saldo INTEGER NOT NULL
)
"""

SKEMA_BACA = """
CREATE TABLE ringkasan_baca (
  pemilik TEXT PRIMARY KEY,
  saldo INTEGER NOT NULL,
  jumlah_perubahan INTEGER NOT NULL,
  total_setor INTEGER NOT NULL,
  total_bayar INTEGER NOT NULL,
  waktu_terakhir TEXT NOT NULL
)
"""

SIMPAN_RINGKASAN = """
INSERT INTO ringkasan_baca
  (pemilik, saldo, jumlah_perubahan, total_setor, total_bayar, waktu_terakhir)
VALUES (?, ?, ?, ?, ?, ?)
ON CONFLICT(pemilik) DO UPDATE SET
  saldo = excluded.saldo,
  jumlah_perubahan = excluded.jumlah_perubahan,
  total_setor = excluded.total_setor,
  total_bayar = excluded.total_bayar,
  waktu_terakhir = excluded.waktu_terakhir
"""

ALASAN_TANPA_RIWAYAT = (
  "model baca hanya menyimpan keadaan terakhir, nilai antaranya tidak disimpan"
)


class BukuBesarCqrs:
  """Buku besar dompet yang memisahkan model tulis dari model baca."""

  def __init__(self, berkas: pathlib.Path = BERKAS_BAKU,
               proyeksi_langsung: bool = True) -> None:
    """Membuka koneksi lalu menyiapkan antrean proyeksi yang masih kosong.

    Antrean hanya terpakai ketika proyeksi_langsung bernilai False. Dalam
    keadaan itu model baca tertinggal sampai antreannya didorong, dan jeda
    itulah yang dikenal sebagai keterlambatan model baca.
    """
    self.berkas = pathlib.Path(berkas)
    self.koneksi = sqlite3.connect(self.berkas)
    self.proyeksi_langsung = proyeksi_langsung
    self.antrean = []

  def siapkan(self) -> None:
    """Membentuk ulang kedua tabel sekaligus mengosongkan antrean proyeksi.

    VACUUM dijalankan sesudahnya, sebab menghapus tabel hanya melepas halaman
    ke daftar bebas dan tidak mengecilkan berkasnya. Tanpa langkah itu, ukuran
    berkas yang dilaporkan masih membawa sisa pengukuran sebelumnya.
    """
    self.koneksi.execute("DROP TABLE IF EXISTS dompet_tulis")
    self.koneksi.execute("DROP TABLE IF EXISTS ringkasan_baca")
    self.koneksi.execute(SKEMA_TULIS)
    self.koneksi.execute(SKEMA_BACA)
    self.koneksi.commit()
    self.koneksi.execute("VACUUM")
    self.antrean = []

  def jalankan(self, perintah: domain.Perintah) -> int:
    """Memutakhirkan model tulis lalu menyerahkan perubahannya ke proyeksi.

    Aturan bisnis diperiksa terhadap model tulis, bukan terhadap model baca,
    sebab model baca boleh tertinggal. Mengembalikan int berisi saldo baru pada
    model tulis, dan melempar domain.SaldoTidakCukup bila ditolak.
    """
    kursor = self.koneksi.execute(
      "SELECT saldo FROM dompet_tulis WHERE pemilik = ?", (perintah.pemilik,)
    )
    baris = kursor.fetchone()
    saldo_lama = baris[0] if baris else 0
    saldo_baru = domain.periksa_perintah(saldo_lama, perintah)
    self.koneksi.execute(
      "INSERT INTO dompet_tulis (pemilik, saldo) VALUES (?, ?) "
      "ON CONFLICT(pemilik) DO UPDATE SET saldo = excluded.saldo",
      (perintah.pemilik, saldo_baru),
    )
    self.koneksi.commit()
    if self.proyeksi_langsung:
      self.proyeksikan(perintah)
    else:
      self.antrean.append(perintah)
    return saldo_baru

  def proyeksikan(self, perintah: domain.Perintah) -> domain.Ringkasan:
    """Melipat satu perubahan ke atas baris ringkasan pada model baca.

    Fungsi pelipatnya diambil dari domain.terapkan, yaitu fungsi yang sama
    dengan yang dipakai penghitungan ulang versi event sourcing. Mengembalikan
    Ringkasan yang baru saja disimpan.
    """
    lama = self.baca_ringkasan(perintah.pemilik)
    baru = domain.terapkan(lama, perintah.jenis, perintah.nominal,
                           perintah.waktu)
    self.koneksi.execute(SIMPAN_RINGKASAN, (
      perintah.pemilik, baru.saldo, baru.jumlah_perubahan, baru.total_setor,
      baru.total_bayar, baru.waktu_terakhir,
    ))
    self.koneksi.commit()
    return baru

  def dorong_proyeksi(self) -> int:
    """Menjalankan seluruh proyeksi yang masih tertahan di dalam antrean.

    Metode ini hanya berguna ketika proyeksi_langsung bernilai False.
    Mengembalikan int berisi jumlah perubahan yang baru saja disusulkan.
    """
    jumlah = len(self.antrean)
    for tertahan in self.antrean:
      self.proyeksikan(tertahan)
    self.antrean = []
    return jumlah

  def baca_ringkasan(self, pemilik: str) -> domain.Ringkasan:
    """Membaca satu baris model baca tanpa menyentuh model tulis sama sekali.

    Mengembalikan Ringkasan berisi saldo beserta angka turunannya, atau
    domain.RINGKASAN_KOSONG bila pemiliknya belum pernah diproyeksikan.
    """
    kursor = self.koneksi.execute(
      "SELECT saldo, jumlah_perubahan, total_setor, total_bayar, "
      "waktu_terakhir FROM ringkasan_baca WHERE pemilik = ?", (pemilik,)
    )
    baris = kursor.fetchone()
    if not baris:
      return domain.RINGKASAN_KOSONG
    return domain.Ringkasan(*baris)

  def baca_saldo(self, pemilik: str) -> int:
    """Membaca saldo dari model baca, bukan dari model tulis.

    Inilah pemisahan yang dimaksud CQRS, yaitu kueri tidak pernah menyentuh
    tabel yang dipakai perintah. Mengembalikan int berisi saldo menurut model
    baca, yang dapat tertinggal bila proyeksinya ditunda.
    """
    return self.baca_ringkasan(pemilik).saldo

  def jawab_saldo_pada(self, pemilik: str, batas_waktu: str) -> domain.Jawaban:
    """Menolak menjawab saldo pada waktu lampau, disertai alasannya.

    Pemisahan model tidak dengan sendirinya menyimpan riwayat. Model bacanya
    tetap satu baris per pemilik, dan baris itu ditimpa setiap kali proyeksi
    berjalan. Mengembalikan Jawaban dengan atribut bisa bernilai False.
    """
    return domain.Jawaban(False, 0, ALASAN_TANPA_RIWAYAT)

  def jawab_jumlah_perubahan(self, pemilik: str) -> domain.Jawaban:
    """Menjawab berapa kali saldo berubah dari pencacah pada model baca.

    Angka ini tersedia sebab proyeksinya sengaja dirancang menampung
    pertanyaan tersebut. Pertanyaan yang tidak diduga saat merancang proyeksi
    tetap tidak terjawab. Mengembalikan Jawaban dengan atribut bisa bernilai
    True.
    """
    ringkasan = self.baca_ringkasan(pemilik)
    return domain.Jawaban(True, ringkasan.jumlah_perubahan,
                          "dihitung proyeksi saat perintah diterima")

  def ukuran_kib(self) -> float:
    """Mengembalikan float berisi ukuran berkas basis datanya dalam KiB."""
    return self.berkas.stat().st_size / 1024

  def tutup(self) -> None:
    """Menutup koneksi agar berkas basis datanya dapat dihapus atau disalin."""
    self.koneksi.close()


if __name__ == "__main__":
  buku = BukuBesarCqrs(proyeksi_langsung=False)
  buku.siapkan()
  ditolak = 0
  for satu_perintah in domain.bangkitkan_perintah(100):
    try:
      buku.jalankan(satu_perintah)
    except domain.SaldoTidakCukup:
      ditolak += 1
  print(f"Saldo model baca sebelum proyeksi : {buku.baca_saldo(domain.PEMILIK_BAKU)}")
  # Keluarannya: Saldo model baca sebelum proyeksi : 0
  print(f"Perubahan tertahan di antrean     : {buku.dorong_proyeksi()}")
  # Keluarannya: Perubahan tertahan di antrean     : 95
  print(f"Saldo model baca sesudah proyeksi : {buku.baca_saldo(domain.PEMILIK_BAKU)}")
  # Keluarannya: Saldo model baca sesudah proyeksi : 8425000
  print(f"Perintah ditolak                  : {ditolak}")
  # Keluarannya: Perintah ditolak                  : 5
  jawaban = buku.jawab_jumlah_perubahan(domain.PEMILIK_BAKU)
  print(f"Jumlah perubahan                  : {jawaban.nilai}")
  # Keluarannya: Jumlah perubahan                  : 95
  buku.tutup()
