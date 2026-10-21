"""Menghitung biaya menambah satu fungsi baru pada kedua jalur bab ini.

Yang dihitung bukan waktu, melainkan berkas dan baris. Pada penjalan fungsi,
sebuah fungsi baru cukup ditaruh sebagai dua berkas, yaitu modul beserta
manifesnya, dan tidak satu baris pun penjalan ikut disunting. Pada layanan yang
hidup terus, modul barunya harus disebut namanya di dalam kode layanan, sehingga
berkas layanannya ikut berubah.

Pemeriksaan pertama membaca kode tanpa menjalankannya, lalu mencacah baris yang
menyebut nama modul atau nama kelas setiap fungsi. Pemeriksaan kedua benar-benar
menambah satu fungsi baru, menjalankannya lewat penjalan, lalu memeriksa apakah
layanan hidup ikut mengenalinya. Kedua berkas yang ditambahkan dihapus kembali
di akhir.

Cara menjalankan: python ukur_perubahan.py
"""

import json
import pathlib

import layanan_hidup as modul_layanan
import pendaftar as modul_pendaftar
import penjalan as modul_penjalan

DIREKTORI = pathlib.Path(__file__).parent
BERKAS_PENJALAN = ("penjalan.py", "pendaftar.py", "kontrak.py")
BERKAS_LAYANAN = ("layanan_hidup.py",)
# Fungsi yang disalin beserta nama fungsi barunya pada percobaan penambahan.
SUMBER_SALINAN = "fungsi_kurs"
KELAS_SUMBER = "FungsiKurs"
NAMA_BARU = "fungsi_diskon"
KELAS_BARU = "FungsiDiskon"
PERISTIWA_BARU = "diskon"
MUATAN_BARU = {"asal": "USD", "tujuan": "IDR", "nominal": 100.0}


def baris_berkode(berkas: pathlib.Path) -> int:
  """Mengembalikan int jumlah baris berisi kode, tanpa baris kosong.

  Baris kosong dibuang agar perbandingan antar berkas tidak terpengaruh selera
  penulisnya dalam memberi jarak.
  """
  return sum(1 for baris in berkas.read_text(encoding="utf-8").splitlines()
             if baris.strip())


def baris_menyebut_fungsi(berkas: pathlib.Path, nama_fungsi: list) -> int:
  """Mencacah baris yang menyebut nama modul atau nama kelas sebuah fungsi.

  Satu penyebutan saja sudah cukup untuk membuktikan bahwa berkas itu mengenal
  fungsinya, sehingga penambahan fungsi baru akan menyentuhnya. Mengembalikan
  int jumlah baris yang menyebut salah satu nama tersebut.
  """
  jumlah = 0
  for baris in berkas.read_text(encoding="utf-8").splitlines():
    if any(nama in baris for nama in nama_fungsi):
      jumlah += 1
  return jumlah


def kumpulkan_nama_fungsi(pendaftar) -> list:
  """Menyusun daftar nama modul pendek beserta nama kelas seluruh fungsi.

  Nama modul dipendekkan menjadi bagian sesudah titik, sebab layanan hidup
  memakai bentuk from fungsi import fungsi_kurs. Mengembalikan list berisi
  seluruh nama yang dicari di dalam kode.
  """
  nama = []
  for manifes in pendaftar.manifes.values():
    nama.append(manifes["modul"].rpartition(".")[2])
    nama.append(manifes["kelas"])
  return nama


def salin_fungsi_baru() -> tuple:
  """Menyalin satu modul fungsi beserta manifesnya menjadi fungsi baru.

  Penyalinan meniru langkah yang diminta pada Latihan 1, yaitu menambah
  kemampuan tanpa menyentuh penjalan. Mengembalikan tuple berisi kedua jalur
  berkas yang baru dibuat.
  """
  asal_modul = DIREKTORI / "fungsi" / f"{SUMBER_SALINAN}.py"
  asal_manifes = DIREKTORI / "fungsi" / f"{SUMBER_SALINAN}.json"
  tujuan_modul = DIREKTORI / "fungsi" / f"{NAMA_BARU}.py"
  tujuan_manifes = DIREKTORI / "fungsi" / f"{NAMA_BARU}.json"
  tujuan_modul.write_text(
    asal_modul.read_text(encoding="utf-8").replace(KELAS_SUMBER, KELAS_BARU),
    encoding="utf-8")
  manifes = json.loads(asal_manifes.read_text(encoding="utf-8"))
  manifes["nama"] = "Hitung Diskon"
  manifes["peristiwa"] = PERISTIWA_BARU
  manifes["modul"] = f"fungsi.{NAMA_BARU}"
  manifes["kelas"] = KELAS_BARU
  tujuan_manifes.write_text(json.dumps(manifes, indent=2) + "\n",
                            encoding="utf-8")
  return tujuan_modul, tujuan_manifes


class PemeriksaPerubahan:
  """Pemeriksa biaya perubahan pada penjalan fungsi dan layanan hidup."""

  def __init__(self) -> None:
    """Membaca registri awal beserta jumlah penangan layanan hidup.

    Keadaan awal dicatat lebih dahulu agar perubahan sesudah penambahan fungsi
    dapat dibandingkan dengan angka yang benar.
    """
    self.pendaftar = modul_pendaftar.rakit_pendaftar()
    self.nama_fungsi = kumpulkan_nama_fungsi(self.pendaftar)
    self.layanan = modul_layanan.rakit_layanan()
    self.hasil = {"fungsi_awal": len(self.pendaftar.manifes),
                  "penangan_awal": self.layanan.jumlah_penangan()}

  def periksa_penyebutan(self) -> None:
    """Mencacah baris kode dan baris penyebutan pada kedua jalur.

    Angka penyebutan nol berarti berkas itu tidak akan tersentuh ketika sebuah
    fungsi ditambahkan, sedangkan angka lebih dari nol berarti sebaliknya.
    """
    self.hasil["baris_penjalan"] = sum(
      baris_berkode(DIREKTORI / nama) for nama in BERKAS_PENJALAN)
    self.hasil["sebut_penjalan"] = sum(
      baris_menyebut_fungsi(DIREKTORI / nama, self.nama_fungsi)
      for nama in BERKAS_PENJALAN)
    self.hasil["baris_layanan"] = sum(
      baris_berkode(DIREKTORI / nama) for nama in BERKAS_LAYANAN)
    self.hasil["sebut_layanan"] = sum(
      baris_menyebut_fungsi(DIREKTORI / nama, self.nama_fungsi)
      for nama in BERKAS_LAYANAN)
    self.hasil["sebut_per_fungsi"] = (self.hasil["sebut_layanan"]
                                      / self.hasil["fungsi_awal"])

  def periksa_penambahan(self) -> None:
    """Menambah satu fungsi baru sungguhan, lalu memeriksa siapa yang tahu.

    Penjalan cukup membaca ulang manifes, sedangkan layanan hidup tetap tidak
    mengenali fungsi barunya sampai kodenya disunting. Kedua berkas yang
    ditambahkan dihapus kembali, berhasil maupun gagal.
    """
    berkas_baru = salin_fungsi_baru()
    try:
      penjalan_baru = modul_penjalan.rakit_penjalan()
      self.hasil["fungsi_sesudah"] = len(penjalan_baru.pendaftar.manifes)
      hasil = penjalan_baru.panggil(PERISTIWA_BARU, MUATAN_BARU)
      self.hasil["hasil_fungsi_baru"] = hasil.isi["hasil"]
      self.hasil["penangan_sesudah"] = self.layanan.jumlah_penangan()
      self.hasil["sebut_penjalan_sesudah"] = sum(
        baris_menyebut_fungsi(DIREKTORI / nama, self.nama_fungsi)
        for nama in BERKAS_PENJALAN)
      penjalan_baru.turunkan_ke_nol()
    finally:
      for berkas in berkas_baru:
        berkas.unlink(missing_ok=True)
    self.hasil["berkas_baru"] = len(berkas_baru)

  def cetak_ringkasan(self) -> None:
    """Mencetak seluruh cacah berkas dan baris kedua jalur berdampingan."""
    isi = self.hasil
    print(f"Fungsi terdaftar semula       : {isi['fungsi_awal']}")
    print(f"Fungsi terdaftar sesudah      : {isi['fungsi_sesudah']}")
    print(f"Penangan layanan semula       : {isi['penangan_awal']}")
    print(f"Penangan layanan sesudah      : {isi['penangan_sesudah']}")
    print(f"Berkas baru yang ditambahkan  : {isi['berkas_baru']}")
    print(f"Hasil fungsi baru             : {isi['hasil_fungsi_baru']:,.2f}")
    print()
    print(f"Baris kode penjalan           : {isi['baris_penjalan']}")
    print(f"Baris penjalan menyebut fungsi: {isi['sebut_penjalan']}")
    print(f"Baris penjalan disunting      : "
          f"{isi['sebut_penjalan_sesudah'] - isi['sebut_penjalan']}")
    print(f"Baris kode layanan hidup      : {isi['baris_layanan']}")
    print(f"Baris layanan menyebut fungsi : {isi['sebut_layanan']}")
    print(f"Baris layanan per fungsi      : {isi['sebut_per_fungsi']:.1f}")


if __name__ == "__main__":
  pemeriksa = PemeriksaPerubahan()
  pemeriksa.periksa_penyebutan()
  pemeriksa.periksa_penambahan()
  pemeriksa.cetak_ringkasan()
  # Keluarannya: Baris penjalan menyebut fungsi: 0
