"""Mematikan satu layanan, lalu mencatat permintaan mana yang masih dilayani.

Percobaan yang sama dikerjakan pada kedua versi. Pada versi mikroservis, yang
dimatikan adalah layanan kurs saja, sedangkan layanan nasabah dan layanan
pesanan dibiarkan hidup. Pada versi monolit tidak ada bagian yang dapat
dimatikan sendiri, sehingga yang dimatikan adalah seluruh prosesnya. Perbedaan
itu bukan kecurangan, melainkan justru inti persoalannya.

Setiap jawaban digolongkan menjadi tiga. Penuh berarti dilayani dengan isi
lengkap, sebagian berarti dilayani tetapi ada bagian yang kosong, dan gagal
berarti tidak dilayani sama sekali.

Cara menjalankan: python uji_kegagalan.py
"""

import requests

import alamat
import penjalan

TENGGANG_DETIK = 5.0

PERMINTAAN_UJI = (
  ("nasabah", "/nasabah/N-001"),
  ("kurs", "/kurs/USD"),
  ("laporan", "/laporan/N-001"),
)

STATUS_PENUH = "penuh"
STATUS_SEBAGIAN = "sebagian"
STATUS_GAGAL = "gagal"
STATUS_TERLAYANI = (STATUS_PENUH, STATUS_SEBAGIAN)


def golongkan(induk: str, jalur: str) -> str:
  """Mengirim satu permintaan lalu menggolongkan hasilnya menjadi tiga.

  Laporan yang keluar tanpa nilai rupiah digolongkan sebagai sebagian, sebab
  pengguna tetap menerima daftar pesanannya walau angka rupiahnya kosong.
  Mengembalikan str berisi salah satu dari penuh, sebagian, atau gagal.
  """
  try:
    jawaban = requests.get(induk + jalur, timeout=TENGGANG_DETIK)
  except requests.RequestException:
    return STATUS_GAGAL
  if jawaban.status_code != 200:
    return STATUS_GAGAL
  if jawaban.json().get("lengkap") is False:
    return STATUS_SEBAGIAN
  return STATUS_PENUH


def periksa_semua(induk: str) -> dict:
  """Menjalankan ketiga permintaan uji lalu mencatat golongan hasilnya.

  Ketiganya sengaja menyentuh sumber data yang berbeda, sehingga akibat
  matinya satu layanan dapat dipisahkan. Mengembalikan dict yang memetakan nama
  permintaan ke golongan hasilnya.
  """
  return {nama: golongkan(induk, jalur) for nama, jalur in PERMINTAAN_UJI}


def uji_satu_versi(nama_versi: str, daftar_proses: tuple, induk: str,
                   yang_dimatikan: str) -> tuple[dict, dict]:
  """Memeriksa ketiga permintaan sebelum dan sesudah satu proses dimatikan.

  Proses yang dimatikan tidak dinyalakan kembali, sebab yang diukur memang
  keadaan ketika layanan itu sedang mati. Mengembalikan tuple berisi dua dict
  hasil pemeriksaan, yaitu sebelum dan sesudah.
  """
  print(f"Menyalakan versi {nama_versi}.", flush=True)
  berjalan = penjalan.nyalakan(daftar_proses)
  try:
    sebelum = periksa_semua(induk)
    print(f"  mematikan proses {yang_dimatikan}.", flush=True)
    penjalan.matikan_satu(berjalan.pop(yang_dimatikan))
    sesudah = periksa_semua(induk)
  finally:
    penjalan.matikan(berjalan)
  return sebelum, sesudah


def hitung_terlayani(hasil: dict) -> int:
  """Menghitung permintaan yang masih dilayani, penuh maupun sebagian.

  Sebagian tetap dihitung sebagai terlayani, sebab penggunanya menerima
  jawaban dan bukan halaman galat. Mengembalikan int berisi jumlah permintaan
  yang dilayani.
  """
  return sum(1 for status in hasil.values() if status in STATUS_TERLAYANI)


if __name__ == "__main__":
  sebelum_monolit, sesudah_monolit = uji_satu_versi(
    "monolit", penjalan.NAMA_MONOLIT, alamat.MONOLIT, "monolit")
  sebelum_mikro, sesudah_mikro = uji_satu_versi(
    "mikroservis", penjalan.NAMA_MIKROSERVIS, alamat.GERBANG, "kurs")

  print(f"\n{'Permintaan':<11} {'Monolit sebelum':<16} {'Monolit sesudah':<16}"
        f" {'Mikro sebelum':<14} {'Mikro sesudah':<14}")
  for nama_permintaan, _ in PERMINTAAN_UJI:
    print(f"{nama_permintaan:<11} {sebelum_monolit[nama_permintaan]:<16}"
          f" {sesudah_monolit[nama_permintaan]:<16}"
          f" {sebelum_mikro[nama_permintaan]:<14}"
          f" {sesudah_mikro[nama_permintaan]:<14}")

  jumlah_uji = len(PERMINTAAN_UJI)
  print(f"\nTerlayani sesudah kurs mati, monolit     : "
        f"{hitung_terlayani(sesudah_monolit)} dari {jumlah_uji}")
  print(f"Terlayani sesudah kurs mati, mikroservis : "
        f"{hitung_terlayani(sesudah_mikro)} dari {jumlah_uji}")
  # Keluarannya: Terlayani sesudah kurs mati, mikroservis : 2 dari 3
