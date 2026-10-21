"""Menyalakan dan mematikan kedua versi aplikasi lewat modul subprocess.

Versi monolit menempati satu proses, sedangkan versi service-based menempati
empat proses. Menyalakannya satu per satu di terminal yang berbeda melelahkan
dan mudah keliru, sehingga penyalaannya dikumpulkan di sini. Skrip pengukuran
dan skrip kegagalan memakai fungsi yang sama, sehingga yang diukur persis
sama dengan yang dijalankan.

Setiap proses ditunggu sampai jalur /sehat menjawab, bukan ditunggu dengan
jeda tetap. Penantian itu penting, sebab proses yang belum siap membuat
permintaan pertama gagal tanpa sebab yang jelas.

Cara menjalankan:
  python jalankan_layanan.py         # nyalakan, coba empat permintaan, matikan
  python jalankan_layanan.py hidup   # biarkan hidup sampai Ctrl+C ditekan
"""

import pathlib
import subprocess
import sys
import time

import requests

import alamat
import basis_data

DIREKTORI = pathlib.Path(__file__).resolve().parent
BATAS_TUNGGU_SIAP = 20.0
JEDA_PERIKSA = 0.05
JEDA_MATI = 5.0

# Nama proses dipetakan ke modul dan portanya. Urutannya sengaja menaruh
# gerbang di akhir, sebab gerbang hanya berguna sesudah ketiga layanan hidup.
PROSES_MONOLIT = {
  "monolit": ("monolit.py", alamat.PORTA_MONOLIT),
}

PROSES_LAYANAN = {
  "kurs": ("layanan_kurs.py", alamat.PORTA_KURS),
  "pemesanan": ("layanan_pemesanan.py", alamat.PORTA_PEMESANAN),
  "penagihan": ("layanan_penagihan.py", alamat.PORTA_PENAGIHAN),
  "gerbang": ("gerbang.py", alamat.PORTA_GERBANG),
}

# Keempat jenis permintaan yang dipakai seluruh latihan. Ketiganya yang
# pertama menyentuh satu bidang saja, sedangkan yang keempat menyentuh
# ketiga bidang sekaligus.
JENIS_PERMINTAAN = (
  ("baca kurs", "GET", "/kurs/USD"),
  ("baca pesanan", "GET", "/pesanan/1"),
  ("baca tagihan", "GET", "/tagihan/1"),
  ("terbitkan tagihan", "POST", "/pesanan/1/tagihan"),
)


def nyalakan_proses(berkas: str) -> subprocess.Popen:
  """Menyalakan satu proses web sebagai proses anak.

  Keluaran layarnya dibuang, sebab catatan permintaan dari ratusan putaran
  pengukuran akan menenggelamkan angka hasilnya. Mengembalikan objek
  subprocess.Popen yang masih hidup.
  """
  return subprocess.Popen(
    [sys.executable, berkas],
    cwd=DIREKTORI,
    stdout=subprocess.DEVNULL,
    stderr=subprocess.DEVNULL,
  )


def tunggu_siap(porta: int) -> bool:
  """Menunggu sampai satu porta menjawab permintaan kesehatan.

  Penantian dibatasi agar skrip tidak menggantung ketika prosesnya gagal
  mulai, misalnya karena portanya sudah terpakai. Mengembalikan bool bernilai
  True bila proses itu siap sebelum batas waktunya.
  """
  batas = time.perf_counter() + BATAS_TUNGGU_SIAP
  while time.perf_counter() < batas:
    try:
      jawaban = requests.get(f"{alamat.alamat_dasar(porta)}/sehat", timeout=1.0)
      if jawaban.status_code == 200:
        return True
    except requests.RequestException:
      time.sleep(JEDA_PERIKSA)
  return False


def nyalakan(daftar_proses: dict) -> dict:
  """Menyalakan sekelompok proses lalu menunggu seluruhnya siap.

  Melempar RuntimeError bila ada satu proses yang tidak siap sampai batas
  waktunya, sebab pengukuran atas sistem yang setengah hidup tidak ada
  gunanya. Mengembalikan dict berisi pasangan nama proses dan objek
  Popen-nya.
  """
  berjalan = {}
  for nama, (berkas, _) in daftar_proses.items():
    berjalan[nama] = nyalakan_proses(berkas)
  for nama, (_, porta) in daftar_proses.items():
    if not tunggu_siap(porta):
      matikan(berjalan)
      raise RuntimeError(f"proses {nama} tidak siap di porta {porta}")
  return berjalan


def matikan_satu(berjalan: dict, nama: str) -> None:
  """Mematikan satu proses saja, lalu mencabutnya dari daftar yang hidup.

  Dipakai skrip uji_kegagalan.py untuk mematikan layanan kurs tanpa
  mengganggu layanan lain. Tidak mengembalikan apa pun, sebab yang diubah
  adalah dict yang diterimanya.
  """
  proses = berjalan.pop(nama, None)
  if proses is None:
    return
  proses.terminate()
  try:
    proses.wait(timeout=JEDA_MATI)
  except subprocess.TimeoutExpired:
    proses.kill()


def matikan(berjalan: dict) -> None:
  """Mematikan seluruh proses yang masih hidup.

  Dipanggil pada blok finally setiap skrip, sehingga porta tidak tertinggal
  terpakai ketika pengukurannya gagal di tengah jalan. Tidak mengembalikan
  apa pun.
  """
  for nama in list(berjalan):
    matikan_satu(berjalan, nama)


def panggil(porta: int, permintaan: tuple) -> tuple[bool, str]:
  """Mengirim satu jenis permintaan ke sebuah porta lalu menilai jawabannya.

  Permintaan dianggap terlayani hanya bila kode statusnya 200, sehingga
  jawaban 503 dari gerbang terhitung gagal. Mengembalikan tuple berisi bool
  keberhasilan dan str keterangan singkat untuk dicetak.
  """
  _, metode, jalur = permintaan
  try:
    jawaban = requests.request(metode, f"{alamat.alamat_dasar(porta)}{jalur}",
                               timeout=alamat.BATAS_WAKTU_DETIK)
  except requests.RequestException as galat:
    return False, galat.__class__.__name__
  if jawaban.status_code != 200:
    return False, f"status {jawaban.status_code}"
  return True, f"lompatan {jawaban.json()['lompatan']}"


def coba_empat_permintaan(porta: int, judul: str) -> int:
  """Mengirim keempat jenis permintaan ke satu versi lalu mencetak hasilnya.

  Mengembalikan int berisi jumlah jenis permintaan yang terlayani, dari
  empat jenis yang dicoba.
  """
  jumlah_berhasil = 0
  print(f"{judul}")
  for permintaan in JENIS_PERMINTAAN:
    berhasil, keterangan = panggil(porta, permintaan)
    jumlah_berhasil += 1 if berhasil else 0
    tanda = "berhasil" if berhasil else "gagal   "
    print(f"  {permintaan[0]:<18} {tanda}  {keterangan}")
  return jumlah_berhasil


if __name__ == "__main__":
  basis_data.siapkan()
  proses_hidup = nyalakan({**PROSES_MONOLIT, **PROSES_LAYANAN})
  try:
    if len(sys.argv) > 1 and sys.argv[1] == "hidup":
      print(f"Monolit       : {alamat.alamat_dasar(alamat.PORTA_MONOLIT)}")
      print(f"Gerbang       : {alamat.alamat_dasar(alamat.PORTA_GERBANG)}")
      print("Tekan Ctrl+C untuk mematikan seluruh proses.")
      while True:
        time.sleep(1.0)
    else:
      monolit = coba_empat_permintaan(alamat.PORTA_MONOLIT, "Versi monolit")
      layanan = coba_empat_permintaan(alamat.PORTA_GERBANG,
                                      "Versi service-based")
      print(f"Terlayani monolit       : {monolit} dari"
            f" {len(JENIS_PERMINTAAN)}")
      # Keluarannya: Terlayani monolit       : 4 dari 4
      print(f"Terlayani service-based : {layanan} dari"
            f" {len(JENIS_PERMINTAAN)}")
      # Keluarannya: Terlayani service-based : 4 dari 4
  except KeyboardInterrupt:
    print("\nDihentikan dari papan ketik.")
  finally:
    matikan(proses_hidup)
