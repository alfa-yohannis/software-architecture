"""Versi CQRS, yaitu write model dan read model yang disimpan terpisah.

Sisi command memakai tabel dompet_tulis, yang bentuknya mengikuti aturan
bisnis. Sisi query memakai tabel ringkasan_baca, yang bentuknya mengikuti
pertanyaan yang akan datang. Keduanya dijembatani projection, yaitu fungsi yang
melipat perubahan ke atas baris ringkasan sesudah command diterima.

Projection di sini dijalankan langsung sesudah command, agar hasil latihan dapat
diulang. Pilihan lain disediakan lewat argumen projection_langsung bernilai
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
  "read model hanya menyimpan keadaan terakhir, nilai antaranya tidak disimpan"
)


class BukuBesarCqrs:
  """Buku besar dompet yang memisahkan write model dari read model."""

  def __init__(self, berkas: pathlib.Path = BERKAS_BAKU,
               projection_langsung: bool = True) -> None:
    """Membuka koneksi lalu menyiapkan antrean projection yang masih kosong.

    Antrean hanya terpakai ketika projection_langsung bernilai False. Dalam
    keadaan itu read model tertinggal sampai antreannya didorong, dan jeda
    itulah yang dikenal sebagai keterlambatan read model.
    """
    self.berkas = pathlib.Path(berkas)
    self.koneksi = sqlite3.connect(self.berkas)
    self.projection_langsung = projection_langsung
    self.antrean = []

  def siapkan(self) -> None:
    """Membentuk ulang kedua tabel sekaligus mengosongkan antrean projection.

    VACUUM dijalankan sesudahnya, sebab menghapus tabel hanya melepas halaman
    ke daftar bebas dan tidak mengecilkan file-nya. Tanpa langkah itu, ukuran
    file yang dilaporkan masih membawa sisa pengukuran sebelumnya.
    """
    self.koneksi.execute("DROP TABLE IF EXISTS dompet_tulis")
    self.koneksi.execute("DROP TABLE IF EXISTS ringkasan_baca")
    self.koneksi.execute(SKEMA_TULIS)
    self.koneksi.execute(SKEMA_BACA)
    self.koneksi.commit()
    self.koneksi.execute("VACUUM")
    self.antrean = []

  def jalankan(self, command: domain.Command) -> int:
    """Memutakhirkan write model lalu menyerahkan perubahannya ke projection.

    Aturan bisnis diperiksa terhadap write model, bukan terhadap read model,
    sebab read model boleh tertinggal. Mengembalikan int berisi saldo baru pada
    write model, dan melempar domain.SaldoTidakCukup bila ditolak.
    """
    kursor = self.koneksi.execute(
      "SELECT saldo FROM dompet_tulis WHERE pemilik = ?", (command.pemilik,)
    )
    baris = kursor.fetchone()
    saldo_lama = baris[0] if baris else 0
    saldo_baru = domain.periksa_command(saldo_lama, command)
    self.koneksi.execute(
      "INSERT INTO dompet_tulis (pemilik, saldo) VALUES (?, ?) "
      "ON CONFLICT(pemilik) DO UPDATE SET saldo = excluded.saldo",
      (command.pemilik, saldo_baru),
    )
    self.koneksi.commit()
    if self.projection_langsung:
      self.proyeksikan(command)
    else:
      self.antrean.append(command)
    return saldo_baru

  def proyeksikan(self, command: domain.Command) -> domain.Ringkasan:
    """Melipat satu perubahan ke atas baris ringkasan pada read model.

    Fungsi pelipatnya diambil dari domain.terapkan, yaitu fungsi yang sama
    dengan yang dipakai penghitungan ulang versi event sourcing. Mengembalikan
    Ringkasan yang baru saja disimpan.
    """
    lama = self.baca_ringkasan(command.pemilik)
    baru = domain.terapkan(lama, command.jenis, command.nominal,
                           command.waktu)
    self.koneksi.execute(SIMPAN_RINGKASAN, (
      command.pemilik, baru.saldo, baru.jumlah_perubahan, baru.total_setor,
      baru.total_bayar, baru.waktu_terakhir,
    ))
    self.koneksi.commit()
    return baru

  def dorong_projection(self) -> int:
    """Menjalankan seluruh projection yang masih tertahan di dalam antrean.

    Metode ini hanya berguna ketika projection_langsung bernilai False.
    Mengembalikan int berisi jumlah perubahan yang baru saja disusulkan.
    """
    jumlah = len(self.antrean)
    for tertahan in self.antrean:
      self.proyeksikan(tertahan)
    self.antrean = []
    return jumlah

  def baca_ringkasan(self, pemilik: str) -> domain.Ringkasan:
    """Membaca satu baris read model tanpa menyentuh write model sama sekali.

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
    """Membaca saldo dari read model, bukan dari write model.

    Inilah pemisahan yang dimaksud CQRS, yaitu query tidak pernah menyentuh
    tabel yang dipakai command. Mengembalikan int berisi saldo menurut model
    baca, yang dapat tertinggal bila projection-nya ditunda.
    """
    return self.baca_ringkasan(pemilik).saldo

  def jawab_saldo_pada(self, pemilik: str, batas_waktu: str) -> domain.Jawaban:
    """Menolak menjawab saldo pada waktu lampau, disertai alasannya.

    Pemisahan model tidak dengan sendirinya menyimpan riwayat. Read model-nya
    tetap satu baris per pemilik, dan baris itu ditimpa setiap kali projection
    berjalan. Mengembalikan Jawaban dengan atribut bisa bernilai False.
    """
    return domain.Jawaban(False, 0, ALASAN_TANPA_RIWAYAT)

  def jawab_jumlah_perubahan(self, pemilik: str) -> domain.Jawaban:
    """Menjawab berapa kali saldo berubah dari pencacah pada read model.

    Angka ini tersedia sebab projection-nya sengaja dirancang menampung
    pertanyaan tersebut. Pertanyaan yang tidak diduga saat merancang projection
    tetap tidak terjawab. Mengembalikan Jawaban dengan atribut bisa bernilai
    True.
    """
    ringkasan = self.baca_ringkasan(pemilik)
    return domain.Jawaban(True, ringkasan.jumlah_perubahan,
                          "dihitung projection saat command diterima")

  def ukuran_kib(self) -> float:
    """Mengembalikan float berisi ukuran file basis datanya dalam KiB."""
    return self.berkas.stat().st_size / 1024

  def tutup(self) -> None:
    """Menutup koneksi agar file basis datanya dapat dihapus atau disalin."""
    self.koneksi.close()


if __name__ == "__main__":
  buku = BukuBesarCqrs(projection_langsung=False)
  buku.siapkan()
  ditolak = 0
  for satu_command in domain.bangkitkan_command(100):
    try:
      buku.jalankan(satu_command)
    except domain.SaldoTidakCukup:
      ditolak += 1
  print(f"Saldo read model sebelum projection : {buku.baca_saldo(domain.PEMILIK_BAKU)}")
  # Keluarannya: Saldo read model sebelum projection : 0
  print(f"Perubahan tertahan di antrean      : {buku.dorong_projection()}")
  # Keluarannya: Perubahan tertahan di antrean      : 95
  print(f"Saldo read model sesudah projection : {buku.baca_saldo(domain.PEMILIK_BAKU)}")
  # Keluarannya: Saldo read model sesudah projection : 8425000
  print(f"Command ditolak                    : {ditolak}")
  # Keluarannya: Command ditolak                    : 5
  jawaban = buku.jawab_jumlah_perubahan(domain.PEMILIK_BAKU)
  print(f"Jumlah perubahan                   : {jawaban.nilai}")
  # Keluarannya: Jumlah perubahan                   : 95
  buku.tutup()
