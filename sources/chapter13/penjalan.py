"""Menyalakan dan mematikan seluruh proses Bab 13 lewat modul subprocess.

Versi mikroservis terdiri atas empat proses, sedangkan versi monolit hanya
satu. Perbedaan itu merepotkan bila dikerjakan dengan tangan, sehingga seluruh
skrip pengukuran memanggil berkas ini. Setiap proses dinyalakan sebagai perintah
python tersendiri, lalu ditunggu sampai jalur /sehat miliknya menjawab.

Menunggu jawaban /sehat lebih jujur daripada menunggu sekian detik, sebab waktu
nyala sebuah proses berbeda pada tiap mesin. Lama tunggu itu sendiri dilaporkan,
dan angkanya dipakai pada Latihan 3 sebagai ukuran lama padam sebuah rilis.

Cara menjalankan sendiri, lalu dihentikan dengan Ctrl+C:
  python penjalan.py mikroservis
  python penjalan.py monolit
"""

import pathlib
import subprocess
import sys
import time

import requests

import alamat

DIREKTORI = pathlib.Path(__file__).parent
TENGGANG_NYALA_DETIK = 20.0
JEDA_PERIKSA_DETIK = 0.01
TENGGANG_SEHAT_DETIK = 0.5
DETIK_KE_MILIDETIK = 1000.0

PROSES = {
  "nasabah": ("layanan_nasabah.py", alamat.NASABAH),
  "pesanan": ("layanan_pesanan.py", alamat.PESANAN),
  "kurs": ("layanan_kurs.py", alamat.KURS),
  "gerbang": ("gerbang.py", alamat.GERBANG),
  "monolit": ("monolit.py", alamat.MONOLIT),
}

NAMA_MIKROSERVIS = ("nasabah", "pesanan", "kurs", "gerbang")
NAMA_MONOLIT = ("monolit",)


def nyalakan_satu(nama: str) -> subprocess.Popen:
  """Menyalakan satu proses layanan sebagai perintah python tersendiri.

  Keluaran layarnya dibuang agar laporan pengukuran tidak tertimbun catatan
  server. Proses belum tentu siap saat fungsi ini selesai, sehingga pemanggil
  wajib menunggunya lewat tunggu_sehat. Mengembalikan objek Popen milik proses
  yang baru dinyalakan.
  """
  berkas = PROSES[nama][0]
  return subprocess.Popen(
    [sys.executable, berkas],
    cwd=DIREKTORI,
    stdout=subprocess.DEVNULL,
    stderr=subprocess.DEVNULL,
  )


def tunggu_sehat(nama: str, tenggang: float = TENGGANG_NYALA_DETIK) -> float:
  """Menunggu sampai jalur /sehat sebuah proses menjawab dengan kode 200.

  Pemeriksaan diulang setiap sepersepuluh detik sampai menjawab atau sampai
  tenggangnya habis. Mengembalikan float berisi lama tunggu dalam milidetik,
  dan melempar TimeoutError bila prosesnya tidak pernah menjawab.
  """
  url = f"{PROSES[nama][1]}/sehat"
  mulai = time.perf_counter()
  while time.perf_counter() - mulai < tenggang:
    try:
      if requests.get(url, timeout=TENGGANG_SEHAT_DETIK).status_code == 200:
        return (time.perf_counter() - mulai) * DETIK_KE_MILIDETIK
    except requests.RequestException:
      time.sleep(JEDA_PERIKSA_DETIK)
  raise TimeoutError(f"proses {nama} tidak menjawab dalam {tenggang} detik")


def nyalakan(daftar_nama: tuple) -> dict:
  """Menyalakan sekumpulan proses lalu menunggu seluruhnya siap.

  Urutan penyalaan mengikuti urutan daftarnya, sehingga gerbang ditaruh paling
  belakang agar layanan yang dipanggilnya sudah siap. Mengembalikan dict yang
  memetakan nama proses ke objek Popen miliknya.
  """
  berjalan = {}
  for nama in daftar_nama:
    berjalan[nama] = nyalakan_satu(nama)
    tunggu_sehat(nama)
  return berjalan


def matikan_satu(proses: subprocess.Popen) -> None:
  """Menghentikan satu proses dengan sinyal terminate lalu menunggunya selesai.

  Penungguan diperlukan agar portanya benar-benar dilepas sebelum proses
  penggantinya dinyalakan. Fungsi ini tidak mengembalikan nilai.
  """
  proses.terminate()
  proses.wait()


def matikan(berjalan: dict) -> None:
  """Menghentikan seluruh proses yang tercatat pada sebuah dict penjalan.

  Dipanggil pada blok finally setiap skrip pengukuran, agar tidak ada proses
  yang tertinggal hidup ketika pengukurannya gagal di tengah jalan. Fungsi ini
  tidak mengembalikan nilai.
  """
  for proses in berjalan.values():
    matikan_satu(proses)


def nyalakan_ulang(berjalan: dict, nama: str) -> float:
  """Mematikan lalu menyalakan kembali satu proses, meniru sebuah rilis.

  Inilah yang dikerjakan saat versi baru sebuah layanan dipasang, yaitu proses
  lama dihentikan dan proses baru dijalankan. Mengembalikan float berisi lama
  padam dalam milidetik, terhitung sejak proses lama dihentikan sampai proses
  baru menjawab /sehat.
  """
  mulai = time.perf_counter()
  matikan_satu(berjalan[nama])
  berjalan[nama] = nyalakan_satu(nama)
  tunggu_sehat(nama)
  return (time.perf_counter() - mulai) * DETIK_KE_MILIDETIK


if __name__ == "__main__":
  pilihan = sys.argv[1] if len(sys.argv) > 1 else "mikroservis"
  daftar = NAMA_MONOLIT if pilihan == "monolit" else NAMA_MIKROSERVIS
  proses_hidup = nyalakan(daftar)
  print(f"Versi {pilihan} menyala, {len(proses_hidup)} proses.")
  for nama_proses in daftar:
    print(f"  {nama_proses:<9} {PROSES[nama_proses][1]}")
  print("Tekan Ctrl+C untuk mematikannya.")
  try:
    for proses_satu in proses_hidup.values():
      proses_satu.wait()
  except KeyboardInterrupt:
    matikan(proses_hidup)
    print("\nSeluruh proses dimatikan.")
  # Keluarannya baris pertama: Versi mikroservis menyala, 4 proses.
