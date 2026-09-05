"""Layanan kurs dengan lapisan terbuka.

Lapisan presentasi memanggil lapisan persistensi secara langsung untuk kedua
permintaan. Untuk kurs referensi jalan pintas itu wajar, sebab memang tidak ada
tuntutan bisnis yang berlaku. Untuk kurs jual jalan pintas itu keliru, sebab
pemeriksaan yang dituntut lapisan bisnis ikut dilewati.

Cara menjalankan: python aplikasi_terbuka.py
"""

import basis_data

KUERI_KURS_REFERENSI = """
SELECT kode_asal, kode_tujuan, nilai FROM kurs ORDER BY kode_asal
"""

KUERI_KURS_JUAL = """
SELECT kode_asal, kode_tujuan, nilai + margin FROM kurs ORDER BY kode_asal
"""

# Peta lapisan dibaca oleh periksa_lapisan.py, sama seperti pada versi tertutup.
LAPISAN = {
  "ambil_baris_kurs_referensi": "basis_data",
  "ambil_baris_kurs_jual": "basis_data",
  "daftar_kurs_referensi": "persistensi",
  "daftar_kurs_jual": "persistensi",
  "tampilkan_kurs_referensi": "presentasi",
  "tampilkan_kurs_jual": "presentasi",
}


# --- Lapisan basis data -----------------------------------------------------

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

def daftar_kurs_referensi():
  """Mengubah baris kurs referensi menjadi daftar tupel siap pakai."""
  return [(asal, tujuan, nilai) for asal, tujuan, nilai in ambil_baris_kurs_referensi()]


def daftar_kurs_jual():
  """Mengubah baris kurs jual menjadi daftar tupel siap pakai."""
  return [(asal, tujuan, nilai) for asal, tujuan, nilai in ambil_baris_kurs_jual()]


# --- Lapisan presentasi -----------------------------------------------------

def tampilkan_kurs_referensi():
  """Memanggil lapisan persistensi langsung untuk data yang memang publik.

  Jalan pintas di sini wajar. Tidak ada tuntutan bisnis yang dilewati, sebab
  kurs referensi memang diterbitkan untuk umum.
  """
  baris = daftar_kurs_referensi()
  return [f"{asal} -> {tujuan}: {nilai}" for asal, tujuan, nilai in baris]


def tampilkan_kurs_jual():
  """Memanggil lapisan persistensi langsung untuk data komersial.

  Jalan pintas di sini keliru. Pemanggil tidak perlu menyerahkan token, dan
  margin ikut terbaca siapa pun. Pemeriksaan yang dituntut lapisan bisnis
  hilang bersama lapisan yang dilewati.
  """
  return [f"{asal} -> {tujuan}: {nilai}" for asal, tujuan, nilai in daftar_kurs_jual()]


if __name__ == "__main__":
  print("referensi:", tampilkan_kurs_referensi()[0])
  # Keluarannya: referensi: EUR -> IDR: 17600.0
  print("jual     :", tampilkan_kurs_jual()[0])
  # Keluarannya: jual     : EUR -> IDR: 17690.0
  print("Tidak ada token yang diminta, dan tidak ada pemeriksaan yang dijalankan.")
