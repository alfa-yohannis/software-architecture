"""Layanan kurs dengan open layer.

Kelas presentasi memegang rujukan ke kelas persistensi, sehingga lapisan bisnis
tidak pernah dilewati sama sekali. Untuk kurs dasar jalan pintas itu wajar,
sebab memang tidak ada tuntutan bisnis yang berlaku. Untuk kurs jual jalan
pintas itu keliru, sebab kurs tersebut memuat margin keuntungan bank, dan
pemeriksaan yang dituntut lapisan bisnis ikut dilewati. Nama kelas dan nama
metodenya sengaja disamakan dengan aplikasi_tertutup.py agar perbandingannya
hanya menyangkut susunan lapisan.

Cara menjalankan: python aplikasi_terbuka.py
"""

from basis_data import BasisDataKurs

KUERI_KURS_DASAR = """
SELECT kode_asal, kode_tujuan, nilai FROM kurs ORDER BY kode_asal
"""

KUERI_KURS_JUAL = """
SELECT kode_asal, kode_tujuan, nilai + margin FROM kurs ORDER BY kode_asal
"""

# Peta lapisan dibaca oleh periksa_lapisan.py, sama seperti pada versi closed.
# Lapisan bisnis tidak muncul di sini, dan ketiadaannya itulah yang diperiksa.
LAPISAN = {
  "AksesTabelKurs": "basis_data",
  "RepositoriKurs": "persistensi",
  "AntarmukaKurs": "presentasi",
}


class AksesTabelKurs:
  """Lapisan basis data, isinya sama persis dengan versi closed."""

  def __init__(self, basis: BasisDataKurs):
    """Menerima basis data yang akan dibaca, bukan membuatnya sendiri."""
    self.basis = basis

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
  """Lapisan persistensi, isinya sama persis dengan versi closed."""

  def __init__(self, akses: AksesTabelKurs):
    """Menerima akses tabel yang dipakai membaca seluruh kurs."""
    self.akses = akses

  def daftar_kurs_dasar(self):
    """Mengubah baris kurs dasar menjadi daftar tupel siap pakai."""
    baris = self.akses.ambil_baris_kurs_dasar()
    return [(asal, tujuan, nilai) for asal, tujuan, nilai in baris]

  def daftar_kurs_jual(self):
    """Mengubah baris kurs jual menjadi daftar tupel siap pakai."""
    baris = self.akses.ambil_baris_kurs_jual()
    return [(asal, tujuan, nilai) for asal, tujuan, nilai in baris]


class AntarmukaKurs:
  """Lapisan presentasi yang memegang repositori, bukan layanan.

  Rujukan pada konstruktorlah yang membuat lapisan bisnis tidak pernah
  terpanggil. Satu baris itu menentukan dua request sekaligus, dan hanya
  salah satunya yang dapat dibenarkan.
  """

  def __init__(self, repositori: RepositoriKurs):
    """Menerima repositori secara langsung, tanpa melewati lapisan bisnis."""
    self.repositori = repositori

  def tampilkan_kurs_dasar(self):
    """Memanggil lapisan persistensi langsung untuk data yang memang publik.

    Jalan pintas di sini wajar. Tidak ada tuntutan bisnis yang dilewati, sebab
    kurs dasar memang diterbitkan untuk umum.
    """
    baris = self.repositori.daftar_kurs_dasar()
    return [f"{asal} -> {tujuan}: {nilai}" for asal, tujuan, nilai in baris]

  def tampilkan_kurs_jual(self):
    """Memanggil lapisan persistensi langsung untuk data komersial.

    Jalan pintas di sini keliru. Pemanggil tidak perlu menyerahkan token, dan
    margin keuntungan ikut terbaca siapa pun. Pemeriksaan yang dituntut lapisan
    bisnis hilang bersama lapisan yang dilewati.
    """
    baris = self.repositori.daftar_kurs_jual()
    return [f"{asal} -> {tujuan}: {nilai}" for asal, tujuan, nilai in baris]


def rakit_antarmuka():
  """Merangkai ketiga lapisan, tanpa lapisan bisnis dan tanpa penjaga akses.

  Bandingkan dengan fungsi bernama sama pada aplikasi_tertutup.py. Perbedaannya
  hanya satu simpul yang hilang, dan simpul itulah yang memegang pemeriksaan.
  """
  akses = AksesTabelKurs(BasisDataKurs())
  return AntarmukaKurs(RepositoriKurs(akses))


if __name__ == "__main__":
  antarmuka = rakit_antarmuka()
  print("dasar:", antarmuka.tampilkan_kurs_dasar()[0])
  # Keluarannya: dasar: EUR -> IDR: 17600.0
  print("jual :", antarmuka.tampilkan_kurs_jual()[0])
  # Keluarannya: jual : EUR -> IDR: 17690.0
  print("Tidak ada token yang diminta, dan tidak ada pemeriksaan yang dijalankan.")
