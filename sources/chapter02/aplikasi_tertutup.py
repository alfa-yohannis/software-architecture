"""Layanan kurs dengan empat closed layer.

Setiap lapisan diwakili satu kelas, dan setiap kelas hanya memegang rujukan ke
kelas lapisan tepat di bawahnya. Rujukan tersebut diserahkan lewat konstruktor,
sehingga arah ketergantungannya terbaca dari tanda tangan konstruktor itu
sendiri. Aplikasi melayani dua permintaan yang membaca tabel yang sama, tetapi
tuntutan bisnisnya berbeda. Kurs dasar terbuka untuk umum, sedangkan kurs
jual memuat margin keuntungan bank sehingga hanya boleh dibaca staf. Berkas ini
menjadi pembanding bagi aplikasi_terbuka.py.

Cara menjalankan, salah satu dari tiga perintah berikut:
  python aplikasi_tertutup.py dasar
  python aplikasi_tertutup.py jual token-andi
  python aplikasi_tertutup.py konversi USD IDR 100
"""

import sys

from autentikasi import PenjagaAkses
from basis_data import BasisDataKurs

BATAS_NOMINAL_WAJAR = 1_000_000_000
# Token bawaan bila perintah jual dijalankan tanpa menyebutkan token.
TOKEN_BAWAAN = "token-andi"

PEMAKAIAN = """Perintah yang dikenali:
  python aplikasi_tertutup.py dasar
  python aplikasi_tertutup.py jual token-andi
  python aplikasi_tertutup.py konversi USD IDR 100"""
PESAN_KURS_HILANG = "Kurs {} ke {} tidak tersedia"

KUERI_SATU_KURS = """
SELECT nilai FROM kurs WHERE kode_asal = ? AND kode_tujuan = ?
"""

KUERI_KURS_DASAR = """
SELECT kode_asal, kode_tujuan, nilai FROM kurs ORDER BY kode_asal
"""

KUERI_KURS_JUAL = """
SELECT kode_asal, kode_tujuan, nilai + margin FROM kurs ORDER BY kode_asal
"""

# Peta lapisan dibaca oleh periksa_lapisan.py. Peta ini ditulis eksplisit agar
# pemeriksaan tidak perlu menebak lapisan sebuah kelas dari namanya.
LAPISAN = {
  "AksesTabelKurs": "basis_data",
  "RepositoriKurs": "persistensi",
  "LayananKurs": "bisnis",
  "AntarmukaKurs": "presentasi",
}


class AksesTabelKurs:
  """Lapisan basis data, satu-satunya tempat perintah SQL ditulis.

  Kelas ini menerjemahkan permintaan menjadi kueri, lalu mengembalikan baris
  mentah apa adanya. Bentuk baris sengaja tidak diubah di sini, sebab
  pengubahannya menjadi tugas lapisan persistensi.
  """

  def __init__(self, basis: BasisDataKurs):
    """Menerima basis data yang akan dibaca, bukan membuatnya sendiri."""
    self.basis = basis

  def ambil_baris_kurs(self, kode_asal, kode_tujuan):
    """Membaca satu baris kurs dasar untuk sepasang mata uang."""
    koneksi = self.basis.buka_koneksi()
    kursor = koneksi.execute(KUERI_SATU_KURS, (kode_asal, kode_tujuan))
    baris = kursor.fetchone()
    koneksi.close()
    return baris

  def ambil_baris_kurs_dasar(self):
    """Membaca seluruh kurs dasar, yaitu nilai tanpa margin."""
    koneksi = self.basis.buka_koneksi()
    kursor = koneksi.execute(KUERI_KURS_DASAR)
    baris = kursor.fetchall()
    koneksi.close()
    return baris

  def ambil_baris_kurs_jual(self):
    """Membaca seluruh kurs jual, yaitu nilai ditambah margin keuntungan."""
    koneksi = self.basis.buka_koneksi()
    kursor = koneksi.execute(KUERI_KURS_JUAL)
    baris = kursor.fetchall()
    koneksi.close()
    return baris


class RepositoriKurs:
  """Lapisan persistensi, tempat baris mentah menjadi bentuk siap pakai.

  Lapisan di atasnya tidak pernah melihat kursor maupun tupel basis data,
  sehingga penggantian penyimpanan cukup mengubah kelas ini beserta kelas di
  bawahnya.
  """

  def __init__(self, akses: AksesTabelKurs):
    """Menerima akses tabel yang dipakai membaca seluruh kurs."""
    self.akses = akses

  def cari_kurs(self, kode_asal, kode_tujuan):
    """Mengubah baris mentah menjadi angka, atau None bila kurs tidak ada."""
    baris = self.akses.ambil_baris_kurs(kode_asal, kode_tujuan)
    if baris is None:
      return None
    return baris[0]

  def daftar_kurs_dasar(self):
    """Mengubah baris kurs dasar menjadi daftar tupel siap pakai."""
    baris = self.akses.ambil_baris_kurs_dasar()
    return [(asal, tujuan, nilai) for asal, tujuan, nilai in baris]

  def daftar_kurs_jual(self):
    """Mengubah baris kurs jual menjadi daftar tupel siap pakai."""
    baris = self.akses.ambil_baris_kurs_jual()
    return [(asal, tujuan, nilai) for asal, tujuan, nilai in baris]


class LayananKurs:
  """Lapisan bisnis, tempat seluruh aturan dan pemeriksaan ditegakkan.

  Kelas ini memegang dua kolaborator, yaitu repositori sebagai lapisan tepat di
  bawahnya dan penjaga akses sebagai penegak aturan siapa yang boleh membaca
  apa. Kedua kolaborator itulah yang ikut hilang bila lapisan ini dilewati.
  """

  def __init__(self, repositori: RepositoriKurs, penjaga: PenjagaAkses):
    """Menerima repositori dan penjaga akses yang dipakai seluruh metodenya."""
    self.repositori = repositori
    self.penjaga = penjaga

  def hitung_konversi(self, kode_asal, kode_tujuan, nominal):
    """Menghitung hasil konversi beserta pemeriksaan aturan bisnisnya.

    Aturan yang diperiksa ada dua, yaitu nominal harus positif dan tidak boleh
    melewati batas wajar. Keduanya diperiksa di sini, bukan di lapisan
    antarmuka.
    """
    if nominal <= 0:
      raise ValueError("Nominal harus lebih besar dari nol")
    if nominal > BATAS_NOMINAL_WAJAR:
      raise ValueError("Nominal melewati batas wajar")
    nilai = self.repositori.cari_kurs(kode_asal, kode_tujuan)
    if nilai is None:
      raise LookupError(PESAN_KURS_HILANG.format(kode_asal, kode_tujuan))
    return nominal * nilai

  def susun_kurs_dasar(self):
    """Meneruskan panggilan tanpa menambahkan apa pun.

    Kurs dasar memang diterbitkan untuk umum, meniru JISDOR yang diumumkan
    Bank Indonesia setiap hari kerja. Tidak ada tuntutan bisnis yang berlaku,
    sehingga metode ini murni pass-through.
    """
    return self.repositori.daftar_kurs_dasar()

  def susun_kurs_jual(self, token):
    """Memeriksa autentikasi dan otorisasi sebelum kurs jual diberikan.

    Kurs jual adalah kurs dasar ditambah margin keuntungan bank. Besar
    keuntungan itu informasi komersial, sehingga tuntutan bisnisnya menyatakan
    hanya staf yang boleh membacanya. Tuntutan itulah yang ikut hilang bila
    lapisan bisnis dilewati.
    """
    pengguna = self.penjaga.periksa_token(token)
    if pengguna is None:
      raise PermissionError("Token tidak dikenali")
    if not self.penjaga.boleh_membaca(pengguna):
      raise PermissionError(f"Peran {pengguna['peran']} tidak berhak membaca")
    return self.repositori.daftar_kurs_jual()


class AntarmukaKurs:
  """Lapisan presentasi, tempat hasil diubah menjadi teks.

  Kelas ini hanya mengenal lapisan bisnis. Tidak ada satu pun kueri maupun
  aturan bisnis yang ditulis di sini, sehingga bentuk tampilannya dapat
  berganti tanpa menyentuh lapisan di bawahnya.
  """

  def __init__(self, layanan: LayananKurs):
    """Menerima layanan yang menjadi satu-satunya jalan turun ke data."""
    self.layanan = layanan

  def tampilkan_konversi(self, kode_asal, kode_tujuan, nominal):
    """Memformat hasil konversi menjadi satu baris teks."""
    hasil = self.layanan.hitung_konversi(kode_asal, kode_tujuan, nominal)
    return f"{nominal:,.2f} {kode_asal} = {hasil:,.2f} {kode_tujuan}"

  def tampilkan_kurs_dasar(self):
    """Memformat kurs dasar menjadi daftar baris teks."""
    baris = self.layanan.susun_kurs_dasar()
    return [f"{asal} -> {tujuan}: {nilai}" for asal, tujuan, nilai in baris]

  def tampilkan_kurs_jual(self, token):
    """Memformat kurs jual menjadi daftar baris teks."""
    baris = self.layanan.susun_kurs_jual(token)
    return [f"{asal} -> {tujuan}: {nilai}" for asal, tujuan, nilai in baris]


def rakit_antarmuka():
  """Merangkai keempat lapisan menjadi satu objek presentasi siap pakai.

  Perangkaian dikumpulkan di satu tempat agar setiap kelas tetap menerima
  kolaboratornya dari luar. Skrip pengukuran memakai fungsi yang sama, sehingga
  susunan lapisan yang diukur persis sama dengan yang dijalankan.
  """
  akses = AksesTabelKurs(BasisDataKurs())
  repositori = RepositoriKurs(akses)
  layanan = LayananKurs(repositori, PenjagaAkses())
  return AntarmukaKurs(layanan)


if __name__ == "__main__":
  perintah = sys.argv[1] if len(sys.argv) > 1 else "dasar"
  antarmuka = rakit_antarmuka()
  if perintah == "dasar":
    print("\n".join(antarmuka.tampilkan_kurs_dasar()))
    # Keluarannya baris pertama: EUR -> IDR: 17600.0
  elif perintah == "jual":
    token = sys.argv[2] if len(sys.argv) > 2 else TOKEN_BAWAAN
    try:
      print("\n".join(antarmuka.tampilkan_kurs_jual(token)))
      # Keluarannya baris pertama: EUR -> IDR: 17690.0
    except PermissionError as ditolak:
      print("ditolak:", ditolak)
      # Keluarannya dengan token-palsu: ditolak: Token tidak dikenali
  elif perintah == "konversi":
    print(antarmuka.tampilkan_konversi(sys.argv[2], sys.argv[3],
                                       float(sys.argv[4])))
    # Keluarannya: 100.00 USD = 1,625,000.00 IDR
  else:
    print(PEMAKAIAN)
