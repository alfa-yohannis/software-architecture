"""Konversi mata uang dengan empat lapisan tertutup.

Setiap lapisan hanya memanggil lapisan tepat di bawahnya. Lapisan presentasi
tidak menyentuh basis data, dan lapisan bisnis tidak menyentuh antarmuka.
Berkas ini menjadi pembanding bagi aplikasi_terbuka.py.

Cara menjalankan: python aplikasi_tertutup.py USD IDR 100
"""

import sys

import basis_data

BATAS_NOMINAL_WAJAR = 1_000_000_000
PESAN_KURS_HILANG = "Kurs {} ke {} tidak tersedia"

KUERI_SATU_KURS = """
SELECT nilai FROM kurs WHERE kode_asal = ? AND kode_tujuan = ?
"""

KUERI_SEMUA_KURS = """
SELECT kode_asal, kode_tujuan, nilai FROM kurs ORDER BY kode_asal
"""

# Peta lapisan dibaca oleh periksa_lapisan.py. Peta ini ditulis eksplisit agar
# pemeriksaan tidak perlu menebak lapisan dari nama fungsinya.
LAPISAN = {
  "ambil_baris_kurs": "basis_data",
  "ambil_semua_baris": "basis_data",
  "cari_kurs": "persistensi",
  "daftar_kurs": "persistensi",
  "hitung_konversi": "bisnis",
  "susun_daftar_kurs": "bisnis",
  "tampilkan_konversi": "presentasi",
  "tampilkan_daftar_kurs": "presentasi",
}


# --- Lapisan basis data -----------------------------------------------------

def ambil_baris_kurs(kode_asal, kode_tujuan):
  """Membaca satu baris kurs langsung dari tabel.

  Fungsi ini salah satu dari dua tempat kueri SQL ditulis. Lapisan di atasnya
  tidak mengetahui nama tabel maupun bentuk kuerinya.
  """
  koneksi = basis_data.buka_koneksi()
  kursor = koneksi.execute(KUERI_SATU_KURS, (kode_asal, kode_tujuan))
  baris = kursor.fetchone()
  koneksi.close()
  return baris


def ambil_semua_baris():
  """Membaca seluruh baris kurs dari tabel, diurutkan menurut kode asal."""
  koneksi = basis_data.buka_koneksi()
  kursor = koneksi.execute(KUERI_SEMUA_KURS)
  baris = kursor.fetchall()
  koneksi.close()
  return baris


# --- Lapisan persistensi ----------------------------------------------------

def cari_kurs(kode_asal, kode_tujuan):
  """Mengubah baris mentah menjadi angka, atau None bila kurs tidak ada.

  Lapisan ini memisahkan bentuk penyimpanan dari bentuk yang dipakai logika
  bisnis, sehingga pergantian basis data tidak merambat ke atas.
  """
  baris = ambil_baris_kurs(kode_asal, kode_tujuan)
  if baris is None:
    return None
  return baris[0]


def daftar_kurs():
  """Mengubah baris mentah menjadi daftar tupel siap pakai."""
  return [(asal, tujuan, nilai) for asal, tujuan, nilai in ambil_semua_baris()]


# --- Lapisan bisnis ---------------------------------------------------------

def hitung_konversi(kode_asal, kode_tujuan, nominal):
  """Menghitung hasil konversi beserta pemeriksaan aturan bisnisnya.

  Aturan yang diperiksa ada dua, yaitu nominal harus positif dan tidak boleh
  melewati batas wajar. Keduanya diperiksa di sini, bukan di lapisan antarmuka.
  """
  if nominal <= 0:
    raise ValueError("Nominal harus lebih besar dari nol")
  if nominal > BATAS_NOMINAL_WAJAR:
    raise ValueError("Nominal melewati batas wajar")
  nilai = cari_kurs(kode_asal, kode_tujuan)
  if nilai is None:
    raise LookupError(PESAN_KURS_HILANG.format(kode_asal, kode_tujuan))
  return nominal * nilai


def susun_daftar_kurs():
  """Meneruskan panggilan tanpa menambahkan apa pun.

  Fungsi seperti inilah yang disebut fungsi penerus. Fungsi ini ada hanya untuk
  mematuhi aturan lapisan tertutup, bukan karena ada aturan bisnis.
  """
  return daftar_kurs()


# --- Lapisan presentasi -----------------------------------------------------

def tampilkan_konversi(kode_asal, kode_tujuan, nominal):
  """Memformat hasil konversi menjadi satu baris teks.

  Lapisan ini hanya mengatur tampilan. Seluruh perhitungan dan pemeriksaan
  aturan dikerjakan oleh lapisan bisnis.
  """
  hasil = hitung_konversi(kode_asal, kode_tujuan, nominal)
  return f"{nominal:,.2f} {kode_asal} = {hasil:,.2f} {kode_tujuan}"


def tampilkan_daftar_kurs():
  """Memformat seluruh kurs menjadi daftar baris teks."""
  return [f"{asal} -> {tujuan}: {nilai}" for asal, tujuan, nilai in susun_daftar_kurs()]


if __name__ == "__main__":
  asal, tujuan, jumlah = sys.argv[1], sys.argv[2], float(sys.argv[3])
  print(tampilkan_konversi(asal, tujuan, jumlah))
  # Keluarannya: 100.00 USD = 1,625,000.00 IDR
