"""Bidang pemesanan, yaitu pemilik tabel pesanan.

Bidang ini menyimpan siapa yang memesan, dalam mata uang apa, sebesar berapa,
dan sedang berstatus apa. Statusnya dipakai bidang penagihan sebagai dasar
penolakan, sehingga kolom status menjadi salah satu titik temu kedua bidang
di dalam basis data bersama.

Berkas ini tidak dijalankan sendiri, melainkan diimpor monolit.py atau
layanan_pemesanan.py.
"""

import basis_data
import kesalahan

AMBIL_SATU_PESANAN = """
SELECT nomor, pelanggan, mata_uang, nominal, status
FROM pesanan
WHERE nomor = ?
"""

AMBIL_SEMUA_PESANAN = """
SELECT nomor, pelanggan, mata_uang, nominal, status
FROM pesanan
ORDER BY nomor
"""


def ambil_pesanan(nomor: int) -> dict:
  """Membaca satu pesanan beserta mata uang dan statusnya.

  Melempar kesalahan.TidakDitemukan bila nomornya tidak ada, sebab pemanggil
  perlu membedakan pesanan yang kosong dari pesanan yang bernilai nol.
  Mengembalikan dict berisi kunci nomor, pelanggan, mata_uang, nominal, dan
  status.
  """
  koneksi = basis_data.buka_koneksi()
  try:
    baris = koneksi.execute(AMBIL_SATU_PESANAN, (nomor,)).fetchone()
  finally:
    koneksi.close()
  if baris is None:
    raise kesalahan.TidakDitemukan(f"pesanan {nomor} tidak terdaftar")
  return {
    "nomor": baris["nomor"],
    "pelanggan": baris["pelanggan"],
    "mata_uang": baris["mata_uang"],
    "nominal": baris["nominal"],
    "status": baris["status"],
  }


def daftar_pesanan() -> list[dict]:
  """Menyusun seluruh pesanan menjadi satu daftar yang siap ditampilkan.

  Dipakai skrip penjalan untuk memperlihatkan isi basis data sebelum latihan
  dimulai. Mengembalikan list berisi dict dengan kunci yang sama seperti
  ambil_pesanan, terurut menurut nomor pesanannya.
  """
  koneksi = basis_data.buka_koneksi()
  try:
    baris = koneksi.execute(AMBIL_SEMUA_PESANAN).fetchall()
  finally:
    koneksi.close()
  return [
    {
      "nomor": satu["nomor"],
      "pelanggan": satu["pelanggan"],
      "mata_uang": satu["mata_uang"],
      "nominal": satu["nominal"],
      "status": satu["status"],
    }
    for satu in baris
  ]
