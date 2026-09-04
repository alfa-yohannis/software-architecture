"""Varian lapisan terbuka dari aplikasi yang sama.

Perbedaannya dengan aplikasi_tertutup.py hanya satu. Permintaan yang tidak
punya aturan bisnis, yaitu menampilkan daftar kurs, dilayani langsung oleh
lapisan presentasi ke lapisan persistensi. Lapisan bisnis dilewati, sehingga
fungsi penerus susun_daftar_kurs tidak diperlukan lagi.

Cara menjalankan: python aplikasi_terbuka.py
"""

import basis_data

BATAS_NOMINAL_WAJAR = 1_000_000_000
PESAN_KURS_HILANG = "Kurs {} ke {} tidak tersedia"

KUERI_SATU_KURS = """
SELECT nilai FROM kurs WHERE kode_asal = ? AND kode_tujuan = ?
"""

KUERI_SEMUA_KURS = """
SELECT kode_asal, kode_tujuan, nilai FROM kurs ORDER BY kode_asal
"""

# Peta lapisan dibaca oleh periksa_lapisan.py, sama seperti pada versi tertutup.
LAPISAN = {
  "ambil_baris_kurs": "basis_data",
  "ambil_semua_baris": "basis_data",
  "cari_kurs": "persistensi",
  "daftar_kurs": "persistensi",
  "hitung_konversi": "bisnis",
  "tampilkan_konversi": "presentasi",
  "tampilkan_daftar_kurs": "presentasi",
}


# --- Lapisan basis data -----------------------------------------------------

def ambil_baris_kurs(kode_asal, kode_tujuan):
  """Membaca satu baris kurs langsung dari tabel."""
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
  """Mengubah baris mentah menjadi angka, atau None bila kurs tidak ada."""
  baris = ambil_baris_kurs(kode_asal, kode_tujuan)
  if baris is None:
    return None
  return baris[0]


def daftar_kurs():
  """Mengubah baris mentah menjadi daftar tupel siap pakai."""
  return [(asal, tujuan, nilai) for asal, tujuan, nilai in ambil_semua_baris()]


# --- Lapisan bisnis ---------------------------------------------------------

def hitung_konversi(kode_asal, kode_tujuan, nominal):
  """Menghitung hasil konversi beserta pemeriksaan aturan bisnisnya."""
  if nominal <= 0:
    raise ValueError("Nominal harus lebih besar dari nol")
  if nominal > BATAS_NOMINAL_WAJAR:
    raise ValueError("Nominal melewati batas wajar")
  nilai = cari_kurs(kode_asal, kode_tujuan)
  if nilai is None:
    raise LookupError(PESAN_KURS_HILANG.format(kode_asal, kode_tujuan))
  return nominal * nilai


# --- Lapisan presentasi -----------------------------------------------------

def tampilkan_konversi(kode_asal, kode_tujuan, nominal):
  """Memformat hasil konversi menjadi satu baris teks."""
  hasil = hitung_konversi(kode_asal, kode_tujuan, nominal)
  return f"{nominal:,.2f} {kode_asal} = {hasil:,.2f} {kode_tujuan}"


def tampilkan_daftar_kurs():
  """Memformat seluruh kurs dengan memanggil lapisan persistensi langsung.

  Jalur ini memangkas satu pemanggilan fungsi. Harganya, lapisan presentasi
  kini bergantung pada lapisan persistensi.
  """
  return [f"{asal} -> {tujuan}: {nilai}" for asal, tujuan, nilai in daftar_kurs()]


if __name__ == "__main__":
  for baris_teks in tampilkan_daftar_kurs():
    print(baris_teks)
  # Keluarannya: EUR -> IDR: 17600.0
