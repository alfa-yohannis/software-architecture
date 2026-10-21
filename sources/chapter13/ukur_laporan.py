"""Membandingkan penggabungan di dalam kode dengan penggabungan lewat SQL.

Laporan yang sama disusun dua kali. Versi monolit memakai satu kueri SQL dengan
dua JOIN, sebab ketiga tabelnya berada pada satu berkas. Versi mikroservis
memanggil tiga layanan lalu mencocokkan hasilnya di dalam kode, sebab tidak ada
satu pun kueri yang boleh menyentuh dua berkas sekaligus.

Tiga harga dihitung, yaitu waktu, jumlah baris kode penggabung, dan jumlah
permintaan jaringan per laporan. Baris kode dihitung dari kode sumbernya sendiri
lewat modul ast, sehingga angkanya berubah sendiri bila kodenya disunting.
Isi kedua laporan juga dibandingkan, agar jelas bahwa yang berbeda hanya
susunannya dan bukan hasilnya.

Kedua versi dinyalakan berbarengan lalu diukur bergantian di dalam putaran yang
sama, sama seperti pada ukur_latensi.py.

Cara menjalankan: python ukur_laporan.py
"""

import ast
import inspect
import statistics
import textwrap
import time

import requests

import alamat
import gerbang
import monolit
import penjalan
import ukur_latensi

JUMLAH_PUTARAN = 200
PUTARAN_PEMANASAN = 20
JALUR_LAPORAN = "/laporan/N-001"
TENGGANG_DETIK = 5.0
DETIK_KE_MILIDETIK = 1000.0

PENGGABUNG_MIKROSERVIS = (gerbang.susun_laporan, gerbang.kumpulkan_kurs,
                          gerbang.gabungkan_baris, gerbang.ambil_json)
PENGGABUNG_MONOLIT = (monolit.susun_laporan, monolit.bentuk_baris_laporan)

SESI = requests.Session()


def hitung_baris_fungsi(fungsi) -> int:
  """Menghitung baris kode satu fungsi, tanpa docstring dan tanpa baris kosong.

  Docstring dibuang sebab panjangnya tidak mencerminkan rumitnya pekerjaan,
  sedangkan baris def tetap dihitung sebab fungsinya memang perlu ada.
  Mengembalikan int berisi jumlah baris kode fungsi tersebut.
  """
  sumber = textwrap.dedent(inspect.getsource(fungsi))
  simpul = ast.parse(sumber).body[0]
  isi = simpul.body
  if isinstance(isi[0], ast.Expr) and isinstance(isi[0].value, ast.Constant):
    isi = isi[1:]
  if not isi:
    return 1
  baris = sumber.splitlines()[isi[0].lineno - 1:max(s.end_lineno for s in isi)]
  return 1 + len([satu for satu in baris if satu.strip()])


def hitung_baris_kueri(kueri: str) -> int:
  """Menghitung baris kueri SQL, ditambah satu baris untuk penamaannya.

  Kueri dihitung sebagai kode, sebab kueri itulah yang mengerjakan penggabungan
  pada versi monolit. Mengembalikan int berisi jumlah baris kueri tersebut.
  """
  return 1 + len([satu for satu in kueri.splitlines() if satu.strip()])


def baris_penggabung(daftar_fungsi: tuple, kueri: str = "") -> int:
  """Menjumlahkan baris kode seluruh bagian yang mengerjakan penggabungan.

  Aturan bisnis seperti penyamaran rekening tidak ikut dihitung, sebab kedua
  versi memakai fungsi yang sama persis untuk itu. Mengembalikan int berisi
  jumlah baris penggabung sebuah versi.
  """
  jumlah = sum(hitung_baris_fungsi(satu) for satu in daftar_fungsi)
  return jumlah + (hitung_baris_kueri(kueri) if kueri else 0)


def ambil_laporan(induk: str) -> dict:
  """Meminta satu laporan gabungan kepada salah satu versi.

  Dipakai baik untuk pengukuran waktu maupun untuk membandingkan isinya.
  Mengembalikan dict berisi badan jawaban laporan.
  """
  return SESI.get(induk + JALUR_LAPORAN, timeout=TENGGANG_DETIK).json()


def waktu_satu_laporan(induk: str) -> float:
  """Mengukur lama satu permintaan laporan dari sisi klien.

  Waktu ini sudah memuat seluruh lompatan yang dibutuhkan versi tersebut.
  Mengembalikan float berisi lama dalam milidetik.
  """
  mulai = time.perf_counter()
  ambil_laporan(induk)
  return (time.perf_counter() - mulai) * DETIK_KE_MILIDETIK


def jalankan_putaran() -> tuple[list[float], list[float]]:
  """Mengukur kedua versi bergantian sebanyak putaran yang diminta.

  Putaran pemanasan dibuang lebih dahulu, sebab permintaan pertama menanggung
  pembuatan sambungan TCP pada setiap layanan. Mengembalikan tuple berisi dua
  list lama laporan, yaitu versi monolit dan versi mikroservis.
  """
  for _ in range(PUTARAN_PEMANASAN):
    waktu_satu_laporan(alamat.MONOLIT)
    waktu_satu_laporan(alamat.GERBANG)
  lama_monolit, lama_mikro = [], []
  for _ in range(JUMLAH_PUTARAN):
    lama_monolit.append(waktu_satu_laporan(alamat.MONOLIT))
    lama_mikro.append(waktu_satu_laporan(alamat.GERBANG))
  return lama_monolit, lama_mikro


def tanpa_lompatan(laporan: dict) -> dict:
  """Membuang kunci lompatan agar isi kedua laporan dapat dibandingkan.

  Kunci lompatan memang sengaja berbeda antar versi, sehingga harus dibuang
  sebelum perbandingan. Mengembalikan dict salinan laporan tanpa kunci
  lompatan, baik pada tingkat luar maupun pada bagian nasabah.
  """
  salinan = {kunci: nilai for kunci, nilai in laporan.items() if kunci != "lompatan"}
  salinan["nasabah"] = {kunci: nilai for kunci, nilai in laporan["nasabah"].items()
                        if kunci != "lompatan"}
  return salinan


if __name__ == "__main__":
  berjalan = penjalan.nyalakan(penjalan.NAMA_MONOLIT + penjalan.NAMA_MIKROSERVIS)
  print(f"Menjalankan {JUMLAH_PUTARAN} putaran pada kedua versi.", flush=True)
  try:
    hasil_monolit, hasil_mikro = jalankan_putaran()
    contoh_monolit = ambil_laporan(alamat.MONOLIT)
    contoh_mikro = ambil_laporan(alamat.GERBANG)
  finally:
    penjalan.matikan(berjalan)

  median_monolit = statistics.median(hasil_monolit)
  median_mikro = statistics.median(hasil_mikro)
  baris_monolit = baris_penggabung(PENGGABUNG_MONOLIT, monolit.KUERI_LAPORAN)
  baris_mikro = baris_penggabung(PENGGABUNG_MIKROSERVIS)
  menang = sum(1 for satu, dua in zip(hasil_monolit, hasil_mikro) if satu < dua)

  print(f"\nPutaran per versi                 : {JUMLAH_PUTARAN}")
  print(f"Median laporan monolit            : {median_monolit:.2f} ms")
  print(f"Median laporan mikroservis        : {median_mikro:.2f} ms")
  print(f"Persentil ke-95 monolit           : "
        f"{ukur_latensi.persentil_95(hasil_monolit):.2f} ms")
  print(f"Persentil ke-95 mikroservis       : "
        f"{ukur_latensi.persentil_95(hasil_mikro):.2f} ms")
  print(f"Terbesar monolit                  : {max(hasil_monolit):.2f} ms")
  print(f"Terbesar mikroservis              : {max(hasil_mikro):.2f} ms")
  print(f"Putaran monolit lebih cepat       : {menang} dari {JUMLAH_PUTARAN}")
  print(f"Baris kode penggabung monolit     : {baris_monolit}")
  print(f"Baris kode penggabung mikroservis : {baris_mikro}")
  print(f"Permintaan jaringan monolit       : {contoh_monolit['lompatan']}")
  print(f"Permintaan jaringan mikroservis   : {contoh_mikro['lompatan']}")
  print(f"Isi kedua laporan sama            : "
        f"{tanpa_lompatan(contoh_monolit) == tanpa_lompatan(contoh_mikro)}")
  # Keluarannya: Isi kedua laporan sama            : True
