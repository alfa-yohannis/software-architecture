"""Menghitung biaya menambah satu pelanggan baru pada ketiga susunan.

Pelanggan barunya adalah PencatatAudit pada audit.py. Direktori varian_audit/
memuat ketiga file susunan sesudah pelanggan itu disisipkan, sehingga
biayanya dapat dihitung sebagai selisih baris, bukan diperkirakan.

Perbandingannya hanya menghitung baris kode. Docstring modul, baris kosong, dan
baris komentar dilewati, sebab ketiganya tidak menentukan perilaku program.
Selain selisih baris, skrip ini juga menjalankan kedua bentuk setiap susunan
agar terlihat berapa message tambahan yang dibayar pelanggan baru itu.

Cara menjalankan: python ukur_perubahan.py
"""

import ast
import difflib
import importlib.util
import pathlib

import domain

DIREKTORI = pathlib.Path(__file__).parent
DIREKTORI_VARIAN = DIREKTORI / "varian_audit"
BERKAS_BARU = "audit.py"
NAMA_SUSUNAN = ("sinkron", "broker", "mediator")
JUMLAH_PERMINTAAN = 50
BATAS_TUNGGU = 5.0


def baris_kode(jalur: pathlib.Path) -> list:
  """Membaca satu file Python lalu menyisakan baris kodenya saja.

  Docstring modul dilewati memakai pohon sintaks, sedangkan baris kosong dan
  baris komentar disaring biasa. Mengembalikan list berisi baris kode yang siap
  dibandingkan.
  """
  isi = jalur.read_text(encoding="utf-8")
  pohon = ast.parse(isi)
  batas = 0
  if pohon.body and isinstance(pohon.body[0], ast.Expr):
    nilai = pohon.body[0].value
    if isinstance(nilai, ast.Constant) and isinstance(nilai.value, str):
      batas = pohon.body[0].end_lineno
  baris = isi.splitlines()[batas:]
  return [b for b in baris if b.strip() and not b.strip().startswith("#")]


def hitung_selisih(dasar: list, varian: list) -> tuple:
  """Membandingkan dua daftar baris kode memakai difflib.

  Mengembalikan tuple berisi jumlah baris yang ditambahkan dan jumlah baris
  yang dihapus, dihitung dari keluaran unified diff tanpa baris pengapit.
  """
  ditambah, dihapus = 0, 0
  for baris in difflib.unified_diff(dasar, varian, n=0, lineterm=""):
    if baris.startswith("+++") or baris.startswith("---"):
      continue
    if baris.startswith("+"):
      ditambah += 1
    elif baris.startswith("-"):
      dihapus += 1
  return ditambah, dihapus


def muat_modul(nama: str, jalur: pathlib.Path):
  """Memuat satu file Python sebagai modul tersendiri lewat jalurnya.

  Cara ini dipakai agar file bernama sama di dua direktori dapat dimuat
  berbarengan. Mengembalikan objek modul yang sudah dijalankan isinya.
  """
  spesifikasi = importlib.util.spec_from_file_location(nama, jalur)
  modul = importlib.util.module_from_spec(spesifikasi)
  spesifikasi.loader.exec_module(modul)
  return modul


def jalankan_susunan(modul) -> tuple:
  """Menjalankan sejumlah request pada susunan yang dirakit modul itu.

  Mengembalikan tuple berisi rata-rata message per request dan jejak langkah
  request terakhir, sehingga terlihat pemroses mana saja yang benar-benar
  dilalui.
  """
  susunan = modul.rakit()
  request = None
  for nomor in range(1, JUMLAH_PERMINTAAN + 1):
    request = domain.buat_request(nomor, susunan.jumlah_langkah())
    susunan.kirim(request)
    request.tunggu(BATAS_TUNGGU)
  pesan = susunan.pesan_terkirim() / JUMLAH_PERMINTAAN
  jejak = list(request.jejak)
  susunan.tutup()
  return pesan, jejak


def periksa_susunan(nama: str) -> dict:
  """Menghitung selisih baris sekaligus selisih message satu susunan.

  Mengembalikan dict berisi nama susunan, jumlah baris ditambah dan dihapus,
  jumlah message sebelum dan sesudah penyisipan, serta jejak langkah sesudahnya.
  """
  berkas_dasar = DIREKTORI / f"{nama}.py"
  berkas_varian = DIREKTORI_VARIAN / f"{nama}.py"
  ditambah, dihapus = hitung_selisih(baris_kode(berkas_dasar),
                                     baris_kode(berkas_varian))
  pesan_dasar, _ = jalankan_susunan(muat_modul(nama, berkas_dasar))
  pesan_varian, jejak = jalankan_susunan(
    muat_modul(f"{nama}_audit", berkas_varian))
  return {
    "nama": nama,
    "ditambah": ditambah,
    "dihapus": dihapus,
    "sebelum": pesan_dasar,
    "sesudah": pesan_varian,
    "jejak": jejak,
  }


def cetak_ringkasan(hasil: list) -> None:
  """Mencetak tabel biaya perubahan ketiga susunan beserta catatannya."""
  print(f"File baru bagi ketiganya      : {BERKAS_BARU}")
  print("File pemroses lama disunting  : 0")
  print(f"Request per pengukuran        : {JUMLAH_PERMINTAAN}\n")
  print(f"{'Susunan':<10}{'File':>5}{'Baris tambah':>13}{'Baris hapus':>12}"
        f"{'Message sebelum':>16}{'Message sesudah':>16}")
  for baris in hasil:
    print(f"{baris['nama']:<10}{1:>5d}{baris['ditambah']:>13d}"
          f"{baris['dihapus']:>12d}{baris['sebelum']:>16.1f}"
          f"{baris['sesudah']:>16.1f}")
  print()
  for baris in hasil:
    print(f"Jejak langkah {baris['nama']:<10}: {baris['jejak']}")


if __name__ == "__main__":
  laporan = [periksa_susunan(nama) for nama in NAMA_SUSUNAN]
  cetak_ringkasan(laporan)
  # Keluarannya, baris broker pada tabel:
  # broker        1            3           0             3.0             4.0
