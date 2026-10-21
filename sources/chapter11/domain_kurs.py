"""Bidang kurs, yaitu penyedia nilai tukar bagi kedua bidang lainnya.

Bidang ini hanya membaca tabel kurs. Isinya sengaja kecil, sebab yang ingin
diperlihatkan bab ini adalah butir layanannya, bukan kerumitan aturannya.
Modul yang sama dipakai versi monolit dan versi service-based, sehingga
perbedaan waktu tanggapnya benar-benar berasal dari letak prosesnya.

Berkas ini tidak dijalankan sendiri, melainkan diimpor monolit.py atau
layanan_kurs.py.
"""

import basis_data
import kesalahan

AMBIL_SATU_KURS = "SELECT kode, nilai FROM kurs WHERE kode = ?"
AMBIL_SEMUA_KURS = "SELECT kode, nilai FROM kurs ORDER BY kode"


def ambil_kurs(kode: str) -> dict:
  """Mencari nilai tukar satu mata uang terhadap rupiah.

  Kode diseragamkan menjadi huruf besar lebih dahulu, sehingga permintaan
  usd dan USD menghasilkan baris yang sama. Melempar kesalahan.TidakDitemukan
  bila kodenya tidak terdaftar. Mengembalikan dict berisi kunci kode dan
  nilai.
  """
  koneksi = basis_data.buka_koneksi()
  try:
    baris = koneksi.execute(AMBIL_SATU_KURS, (kode.upper(),)).fetchone()
  finally:
    koneksi.close()
  if baris is None:
    raise kesalahan.TidakDitemukan(f"kurs {kode.upper()} tidak terdaftar")
  return {"kode": baris["kode"], "nilai": baris["nilai"]}


def daftar_kurs() -> list[dict]:
  """Menyusun seluruh nilai tukar yang tersimpan menjadi satu daftar.

  Dipakai halaman ringkasan dan skrip pemeriksaan, agar keduanya tidak perlu
  membuka basis data sendiri. Mengembalikan list berisi dict dengan kunci
  kode dan nilai, terurut menurut kode mata uangnya.
  """
  koneksi = basis_data.buka_koneksi()
  try:
    baris = koneksi.execute(AMBIL_SEMUA_KURS).fetchall()
  finally:
    koneksi.close()
  return [{"kode": satu["kode"], "nilai": satu["nilai"]} for satu in baris]
