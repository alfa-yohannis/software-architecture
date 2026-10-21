"""Menghitung biaya menyisipkan satu langkah baru ke tengah alur kerja.

Langkah yang disisipkan adalah pemeriksaan batas harian, dan tempatnya sesudah
langkah kurs, sebab angka rupiah yang diperiksanya baru dihitung di sana.
Keadaan sesudah penyisipan disimpan apa adanya di direktori sesudah/, lalu
skrip ini membandingkannya dengan keadaan sekarang memakai difflib.

Angka yang dilaporkan karena itu bukan perkiraan, melainkan hasil pembacaan
berkas. Selain jumlah baris, skrip ini juga menghitung berapa layanan yang
sudah berjalan ikut wajib disunting, sebab angka itulah yang menentukan berapa
banyak pemasangan ulang yang dibutuhkan.

Bagian terakhir membuktikan bahwa alur kerja hasil suntingan benar-benar
berjalan, yaitu dengan memasang definisi alur kerja yang baru lalu
menjalankannya satu kali.

Cara menjalankan: python ukur_perubahan.py
"""

import ast
import difflib
import pathlib

import data
import klien
import orkestrator
import server

DIREKTORI = pathlib.Path(__file__).parent
DIREKTORI_SESUDAH = DIREKTORI / "sesudah"
DIREKTORI_BERANTAI = DIREKTORI / "berantai"

# Berkas yang berubah pada masing-masing versi. Versi orkestrasi hanya
# menyentuh definisi alur kerja, sebab layanan batas memang sudah berjalan dan
# sudah dipakai dua alur kerja lain.
BERKAS_ORKESTRASI = ["orkestrator.py"]
BERKAS_BERANTAI = ["konfigurasi.py", "berantai/kurs.py", "berantai/batas.py"]

NAMA_ALUR = "pesan-valas"


def bandingkan_berkas(nama: str) -> tuple:
  """Membandingkan satu berkas sebelum dan sesudah langkah baru disisipkan.

  Berkas yang belum ada sebelumnya diperlakukan sebagai berkas kosong,
  sehingga seluruh barisnya terhitung sebagai tambahan. Mengembalikan tuple
  berisi int baris ditambah, int baris dihapus, dan bool berkas baru.
  """
  jalur_lama = DIREKTORI / nama
  jalur_baru = DIREKTORI_SESUDAH / nama
  berkas_baru = not jalur_lama.exists()
  baris_lama = [] if berkas_baru else jalur_lama.read_text().splitlines()
  baris_baru = jalur_baru.read_text().splitlines()
  beda = list(difflib.unified_diff(baris_lama, baris_baru, n=0))
  ditambah = sum(1 for baris in beda
                 if baris.startswith("+") and not baris.startswith("+++"))
  dihapus = sum(1 for baris in beda
                if baris.startswith("-") and not baris.startswith("---"))
  return ditambah, dihapus, berkas_baru


def hitung_versi(daftar_berkas: list) -> dict:
  """Menjumlahkan perubahan seluruh berkas pada satu versi.

  Mengembalikan dict berisi jumlah berkas, baris ditambah, baris dihapus, dan
  jumlah layanan lama yang ikut disunting.
  """
  ditambah, dihapus, baru, layanan_lama = 0, 0, 0, 0
  for nama in daftar_berkas:
    tambah, hapus, berkas_baru = bandingkan_berkas(nama)
    ditambah += tambah
    dihapus += hapus
    baru += 1 if berkas_baru else 0
    if nama.startswith("berantai/") and not berkas_baru:
      layanan_lama += 1
  return {
    "berkas": len(daftar_berkas),
    "berkas_baru": baru,
    "ditambah": ditambah,
    "dihapus": dihapus,
    "layanan_lama": layanan_lama,
  }


def memuat_tetapan(jalur: pathlib.Path, nama: str) -> bool:
  """Memeriksa apakah sebuah berkas memuat tetapan bernama tertentu.

  Pemeriksaannya memakai ast, bukan pencarian teks, sebab penyebutan nama di
  dalam komentar atau untai teks tidak boleh ikut terhitung. Mengembalikan
  bool bernilai benar bila tetapan itu ada di tingkat modul.
  """
  pohon = ast.parse(jalur.read_text())
  for simpul in pohon.body:
    if not isinstance(simpul, ast.Assign):
      continue
    if getattr(simpul.targets[0], "id", "") == nama:
      return True
  return False


def hitung_tempat_urutan() -> tuple:
  """Menghitung berapa berkas yang memuat potongan urutan langkah.

  Versi orkestrasi menuliskan urutannya pada satu tempat saja, sedangkan versi
  tanpa orkestrasi menyebarkannya ke setiap layanan lewat tetapan BERIKUTNYA.
  Mengembalikan tuple berisi dua int, yaitu jumlah tempat pada kedua versi.
  """
  terpusat = sum(1 for jalur in sorted(DIREKTORI.glob("*.py"))
                 if memuat_tetapan(jalur, "DEFINISI_ALUR"))
  tersebar = sum(1 for jalur in sorted(DIREKTORI_BERANTAI.glob("*.py"))
                 if memuat_tetapan(jalur, "BERIKUTNYA"))
  return terpusat, tersebar


def baca_definisi_sesudah() -> dict:
  """Membaca definisi alur kerja hasil suntingan tanpa mengimpor berkasnya.

  Pembacaannya memakai ast, sebab mengimpor salinan orkestrator akan membuat
  dua mesin hidup berdampingan. Mengembalikan dict definisi alur kerja yang
  tertulis di direktori sesudah.
  """
  pohon = ast.parse((DIREKTORI_SESUDAH / "orkestrator.py").read_text())
  for simpul in pohon.body:
    if not isinstance(simpul, ast.Assign):
      continue
    if getattr(simpul.targets[0], "id", "") == "DEFINISI_ALUR":
      return ast.literal_eval(simpul.value)
  raise ValueError("DEFINISI_ALUR tidak ditemukan pada salinan sesudah")


def uji_alur_sesudah(urutan_baru: list) -> dict:
  """Memasang definisi alur kerja hasil suntingan lalu menjalankannya sekali.

  Definisi lamanya dikembalikan sesudah pengujian, sehingga skrip lain tetap
  menemukan alur kerja seperti semula. Mengembalikan dict berisi keadaan
  proses, jumlah langkah, dan jumlah permintaan HTTP.
  """
  kumpulan = server.KumpulanLayanan()
  kumpulan.nyalakan_semua()
  urutan_lama = list(orkestrator.DEFINISI_ALUR[NAMA_ALUR])
  try:
    data.setel_ulang()
    orkestrator.DEFINISI_ALUR[NAMA_ALUR] = urutan_baru
    data.nolkan_pencacah()
    hasil, _ = klien.jalankan_orkestrasi(NAMA_ALUR)
    return {
      "keadaan": hasil["keadaan"],
      "langkah": len(urutan_baru),
      "lompatan": data.baca_pencacah(),
    }
  finally:
    orkestrator.DEFINISI_ALUR[NAMA_ALUR] = urutan_lama
    kumpulan.matikan_semua()


def cetak_ringkasan(orkestrasi: dict, berantai: dict, tempat: tuple,
                    jalan: dict) -> None:
  """Mencetak biaya perubahan kedua versi berdampingan.

  Tidak mengembalikan nilai.
  """
  print("Langkah baru                 : batas (periksa batas harian)")
  print("Disisipkan sesudah langkah   : kurs")
  print(f"Berkas disunting orkestrasi  : {orkestrasi['berkas']}")
  print(f"Berkas disunting berantai    : {berantai['berkas']}")
  print(f"Berkas baru orkestrasi       : {orkestrasi['berkas_baru']}")
  print(f"Berkas baru berantai         : {berantai['berkas_baru']}")
  print(f"Baris berubah orkestrasi     : "
        f"{orkestrasi['ditambah'] + orkestrasi['dihapus']} "
        f"({orkestrasi['ditambah']} tambah, {orkestrasi['dihapus']} hapus)")
  print(f"Baris berubah berantai       : "
        f"{berantai['ditambah'] + berantai['dihapus']} "
        f"({berantai['ditambah']} tambah, {berantai['dihapus']} hapus)")
  print(f"Layanan lama ikut disunting  : {orkestrasi['layanan_lama']} "
        f"lawan {berantai['layanan_lama']}")
  print(f"Tempat urutan langkah ditulis: {tempat[0]} lawan {tempat[1]}")
  print(f"Langkah sesudah disisipkan   : {jalan['langkah']}")
  print(f"Permintaan HTTP sesudahnya   : {jalan['lompatan']}")
  print(f"Keadaan proses sesudahnya    : {jalan['keadaan']}")


if __name__ == "__main__":
  hasil_orkestrasi = hitung_versi(BERKAS_ORKESTRASI)
  hasil_berantai = hitung_versi(BERKAS_BERANTAI)
  definisi_sesudah = baca_definisi_sesudah()
  hasil_jalan = uji_alur_sesudah(definisi_sesudah[NAMA_ALUR])
  cetak_ringkasan(hasil_orkestrasi, hasil_berantai, hitung_tempat_urutan(),
                  hasil_jalan)
  # Keluarannya: Layanan lama ikut disunting  : 0 lawan 1
