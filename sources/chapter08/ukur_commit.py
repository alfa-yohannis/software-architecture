"""Mengukur harga satu commit SQLite pada dua pengaturan synchronous.

Pada pengaturan bawaan, yaitu FULL, setiap commit dalam mode WAL ditutup dengan
satu sinkronisasi file ke cakram. Lamanya ditentukan cakram laptop itu, bukan
oleh susunan arsitekturnya. Pada pengaturan NORMAL, sinkronisasi hanya terjadi
saat checkpoint, sedangkan transaksi yang sudah di-commit tetap selamat bila
aplikasinya mati.

Skrip ini menjelaskan mengapa basis_data.py memakai NORMAL. Dengan FULL,
pengukuran hasil pada bab ini akan lebih banyak mengukur cakram daripada
mengukur jalur request kedua versi.

Cara menjalankan: python ukur_commit.py
"""

import os
import sqlite3
import time

import sebaran

MILIDETIK = 1000.0
# Banyaknya commit yang diukur pada tiap pengaturan.
JUMLAH_COMMIT = 200
# Pengaturan synchronous yang dibandingkan, dimulai dari bawaan SQLite.
PENGATURAN_DICOBA = ("FULL", "NORMAL")
# File basis data sementara, dihapus lagi sesudah setiap pengaturan.
NAMA_BERKAS_UJI = "uji_commit.db"
# Kode kelas yang diubah berulang kali.
KODE_UJI = "IF231303-A"
# Kuota awal yang cukup besar agar tidak habis selama pengukuran.
KUOTA_UJI = 1000000

SKEMA_UJI = "CREATE TABLE kelas (kode TEXT PRIMARY KEY, sisa INTEGER NOT NULL)"
SISIPKAN_UJI = "INSERT INTO kelas (kode, sisa) VALUES (?, ?)"
KURANGI_UJI = "UPDATE kelas SET sisa = sisa - 1 WHERE kode = ?"


def hapus_berkas_uji() -> None:
  """Menghapus file uji beserta file WAL dan file indeksnya.

  Dipanggil sebelum dan sesudah setiap pengaturan, sehingga keduanya berangkat
  dari file yang sama-sama kosong. Tidak mengembalikan apa pun.
  """
  for akhiran in ("", "-wal", "-shm"):
    berkas = NAMA_BERKAS_UJI + akhiran
    if os.path.exists(berkas):
      os.remove(berkas)


def ukur_satu_pengaturan(pengaturan: str) -> dict:
  """Menjalankan sejumlah transaksi kecil lalu mencatat lama tiap commit.

  Setiap transaksi sama dengan satu request versi basis data, yaitu meminta
  kunci tulis, mengurangi satu kuota, lalu commit. Mengembalikan dict berisi
  median, persentil ke-95, dan nilai terbesar lama satu transaksi.
  """
  hapus_berkas_uji()
  koneksi = sqlite3.connect(NAMA_BERKAS_UJI)
  koneksi.execute("PRAGMA journal_mode=WAL")
  koneksi.execute(f"PRAGMA synchronous={pengaturan}")
  koneksi.execute(SKEMA_UJI)
  koneksi.execute(SISIPKAN_UJI, (KODE_UJI, KUOTA_UJI))
  koneksi.commit()
  daftar_lama = []
  for _ in range(JUMLAH_COMMIT):
    mulai = time.perf_counter()
    koneksi.execute("BEGIN IMMEDIATE")
    koneksi.execute(KURANGI_UJI, (KODE_UJI,))
    koneksi.commit()
    selesai = time.perf_counter()
    daftar_lama.append((selesai - mulai) * MILIDETIK)
  koneksi.close()
  hapus_berkas_uji()
  return sebaran.ringkas(daftar_lama)


if __name__ == "__main__":
  print(f"Transaksi tiap pengaturan : {JUMLAH_COMMIT}, mode WAL")
  print(f"{'Synchronous':<12}{'Median ms':>12}{'p95 ms':>12}"
        f"{'Terbesar ms':>14}")
  for nama_pengaturan in PENGATURAN_DICOBA:
    ringkasan = ukur_satu_pengaturan(nama_pengaturan)
    print(f"{nama_pengaturan:<12}{ringkasan['median']:>12.4f}"
          f"{ringkasan['p95']:>12.4f}{ringkasan['terbesar']:>14.4f}")
  # Keluarannya baris terakhir:
  # NORMAL            0.0091      0.0241        0.0581
