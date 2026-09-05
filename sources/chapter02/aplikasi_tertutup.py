"""Layanan kurs dengan empat lapisan tertutup.

Setiap lapisan hanya memanggil lapisan tepat di bawahnya. Aplikasi melayani dua
permintaan yang membaca tabel yang sama, tetapi tuntutan bisnisnya berbeda.
Kurs referensi terbuka untuk umum, sedangkan kurs jual memuat margin sehingga
hanya boleh dibaca staf. Berkas ini menjadi pembanding bagi aplikasi_terbuka.py.

Cara menjalankan: python aplikasi_tertutup.py USD IDR 100
"""

import sys

import autentikasi
import basis_data

BATAS_NOMINAL_WAJAR = 1_000_000_000
PESAN_KURS_HILANG = "Kurs {} ke {} tidak tersedia"

KUERI_SATU_KURS = """
SELECT nilai FROM kurs WHERE kode_asal = ? AND kode_tujuan = ?
"""

KUERI_KURS_REFERENSI = """
SELECT kode_asal, kode_tujuan, nilai FROM kurs ORDER BY kode_asal
"""

KUERI_KURS_JUAL = """
SELECT kode_asal, kode_tujuan, nilai + margin FROM kurs ORDER BY kode_asal
"""

# Peta lapisan dibaca oleh periksa_lapisan.py. Peta ini ditulis eksplisit agar
# pemeriksaan tidak perlu menebak lapisan dari nama fungsinya.
LAPISAN = {
  "ambil_baris_kurs": "basis_data",
  "ambil_baris_kurs_referensi": "basis_data",
  "ambil_baris_kurs_jual": "basis_data",
  "cari_kurs": "persistensi",
  "daftar_kurs_referensi": "persistensi",
  "daftar_kurs_jual": "persistensi",
  "hitung_konversi": "bisnis",
  "susun_kurs_referensi": "bisnis",
  "susun_kurs_jual": "bisnis",
  "tampilkan_konversi": "presentasi",
  "tampilkan_kurs_referensi": "presentasi",
  "tampilkan_kurs_jual": "presentasi",
}


# --- Lapisan basis data -----------------------------------------------------

def ambil_baris_kurs(kode_asal, kode_tujuan):
  """Membaca satu baris kurs referensi langsung dari tabel."""
  koneksi = basis_data.buka_koneksi()
  kursor = koneksi.execute(KUERI_SATU_KURS, (kode_asal, kode_tujuan))
  baris = kursor.fetchone()
  koneksi.close()
  return baris


def ambil_baris_kurs_referensi():
  """Membaca seluruh kurs referensi, yaitu nilai tanpa margin."""
  koneksi = basis_data.buka_koneksi()
  kursor = koneksi.execute(KUERI_KURS_REFERENSI)
  baris = kursor.fetchall()
  koneksi.close()
  return baris


def ambil_baris_kurs_jual():
  """Membaca seluruh kurs jual, yaitu nilai yang sudah ditambah margin."""
  koneksi = basis_data.buka_koneksi()
  kursor = koneksi.execute(KUERI_KURS_JUAL)
  baris = kursor.fetchall()
  koneksi.close()
  return baris


# --- Lapisan persistensi ----------------------------------------------------

def cari_kurs(kode_asal, kode_tujuan):
  """Mengubah baris mentah menjadi angka, atau None bila kurs tidak ada."""
  baris = ambil_baris_kurs(kode_asal, kode_tujuan)
  if baris is None:
    return None
  return baris[0]


def daftar_kurs_referensi():
  """Mengubah baris kurs referensi menjadi daftar tupel siap pakai."""
  baris = ambil_baris_kurs_referensi()
  return [(asal, tujuan, nilai) for asal, tujuan, nilai in baris]


def daftar_kurs_jual():
  """Mengubah baris kurs jual menjadi daftar tupel siap pakai."""
  return [(asal, tujuan, nilai) for asal, tujuan, nilai in ambil_baris_kurs_jual()]


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


def susun_kurs_referensi():
  """Meneruskan panggilan tanpa menambahkan apa pun.

  Kurs referensi memang diterbitkan untuk umum, meniru JISDOR yang diumumkan
  Bank Indonesia setiap hari kerja. Tidak ada tuntutan bisnis yang berlaku,
  sehingga fungsi ini murni penerus.
  """
  return daftar_kurs_referensi()


def susun_kurs_jual(token):
  """Memeriksa autentikasi dan otorisasi sebelum kurs jual diberikan.

  Kurs jual memuat margin, dan margin adalah informasi komersial. Tuntutan
  bisnisnya menyatakan hanya staf yang boleh membacanya. Tuntutan itulah yang
  ikut hilang bila lapisan bisnis dilewati.
  """
  pengguna = autentikasi.periksa_token(token)
  if pengguna is None:
    raise PermissionError("Token tidak dikenali")
  if not autentikasi.boleh_membaca(pengguna):
    raise PermissionError(f"Peran {pengguna['peran']} tidak berhak membaca kurs jual")
  return daftar_kurs_jual()


# --- Lapisan presentasi -----------------------------------------------------

def tampilkan_konversi(kode_asal, kode_tujuan, nominal):
  """Memformat hasil konversi menjadi satu baris teks."""
  hasil = hitung_konversi(kode_asal, kode_tujuan, nominal)
  return f"{nominal:,.2f} {kode_asal} = {hasil:,.2f} {kode_tujuan}"


def tampilkan_kurs_referensi():
  """Memformat kurs referensi menjadi daftar baris teks."""
  baris = susun_kurs_referensi()
  return [f"{asal} -> {tujuan}: {nilai}" for asal, tujuan, nilai in baris]


def tampilkan_kurs_jual(token):
  """Memformat kurs jual menjadi daftar baris teks."""
  baris = susun_kurs_jual(token)
  return [f"{asal} -> {tujuan}: {nilai}" for asal, tujuan, nilai in baris]


if __name__ == "__main__":
  asal, tujuan, jumlah = sys.argv[1], sys.argv[2], float(sys.argv[3])
  print(tampilkan_konversi(asal, tujuan, jumlah))
  # Keluarannya: 100.00 USD = 1,625,000.00 IDR
  print("referensi:", tampilkan_kurs_referensi()[0])
  # Keluarannya: referensi: EUR -> IDR: 17600.0
  print("jual     :", tampilkan_kurs_jual("token-andi")[0])
  # Keluarannya: jual     : EUR -> IDR: 17690.0
  try:
    tampilkan_kurs_jual("token-palsu")
  except PermissionError as ditolak:
    print("ditolak  :", ditolak)
    # Keluarannya: ditolak  : Token tidak dikenali
