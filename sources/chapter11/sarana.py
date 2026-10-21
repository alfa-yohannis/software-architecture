"""Sarana bersama bagi seluruh proses web Bab 11.

Kelima proses, yaitu monolit, gerbang, dan ketiga layanan domain, memetakan
jenis kesalahan yang sama menjadi kode status HTTP yang sama. Pemetaannya
dikumpulkan di sini agar bidang domain tidak pernah menyebut angka status,
sekaligus agar kedua versi aplikasi benar-benar menjawab dengan bentuk yang
sama persis.

Modul ini sengaja hanya bergantung pada kesalahan.py dan pustaka standar,
tanpa menyentuh satu pun modul domain. Tanpa pembatasan itu, setiap layanan
akan ikut memuat kode bidang lain, dan hitungan layanan yang harus dijalankan
ulang pada skrip biaya_perubahan.py menjadi tidak jujur.

Berkas ini tidak dijalankan sendiri, melainkan diimpor modul lain.
"""

import logging
import sqlite3

import kesalahan

STATUS_TIDAK_DITEMUKAN = 404
STATUS_ATURAN_DILANGGAR = 409
STATUS_TAK_TERJANGKAU = 503


def jawab_tidak_ditemukan(galat: Exception) -> tuple[dict, int]:
  """Menjawab permintaan atas data yang memang tidak ada.

  Mengembalikan tuple berisi dict pesan dan kode status 404, yaitu bentuk
  jawaban yang langsung dikenali Flask.
  """
  return {"galat": str(galat)}, STATUS_TIDAK_DITEMUKAN


def jawab_aturan_dilanggar(galat: Exception) -> tuple[dict, int]:
  """Menjawab permintaan yang ditolak aturan bisnis.

  Mengembalikan tuple berisi dict pesan dan kode status 409, sehingga
  pemanggil tahu bahwa mengulang permintaan yang sama tidak menolong.
  """
  return {"galat": str(galat)}, STATUS_ATURAN_DILANGGAR


def jawab_tak_terjangkau(galat: Exception) -> tuple[dict, int]:
  """Menjawab permintaan ketika satu layanan domain tidak menjawab.

  Mengembalikan tuple berisi dict pesan dan kode status 503. Jawaban inilah
  yang dihitung sebagai permintaan gagal pada skrip uji_kegagalan.py.
  """
  return {"galat": str(galat)}, STATUS_TAK_TERJANGKAU


def jawab_basis_data_sibuk(galat: Exception) -> tuple[dict, int]:
  """Menjawab permintaan ketika berkas basis data bersama sedang terkunci.

  Kegagalan ini menimpa kedua versi sekaligus, sebab keduanya membaca berkas
  yang sama. Mengembalikan tuple berisi dict pesan dan kode status 503.
  """
  return {"galat": f"basis data bersama sibuk: {galat}"}, STATUS_TAK_TERJANGKAU


def pasang_penangan_galat(aplikasi) -> None:
  """Mendaftarkan keempat penangan galat pada satu aplikasi Flask.

  Dipanggil sekali oleh setiap proses web sesudah aplikasinya dibuat. Tidak
  mengembalikan apa pun, sebab yang diubah adalah objek aplikasi yang
  diterimanya.
  """
  aplikasi.register_error_handler(
    kesalahan.TidakDitemukan, jawab_tidak_ditemukan)
  aplikasi.register_error_handler(
    kesalahan.AturanDilanggar, jawab_aturan_dilanggar)
  aplikasi.register_error_handler(
    kesalahan.LayananTakTerjangkau, jawab_tak_terjangkau)
  aplikasi.register_error_handler(
    sqlite3.OperationalError, jawab_basis_data_sibuk)


def redam_catatan_web() -> None:
  """Menurunkan tingkat catatan Werkzeug agar keluaran latihan tetap terbaca.

  Tanpa peredaman ini, setiap permintaan dari seratus putaran pengukuran
  ikut tercetak, dan angka hasilnya tenggelam. Tidak mengembalikan apa pun.
  """
  logging.getLogger("werkzeug").setLevel(logging.ERROR)
