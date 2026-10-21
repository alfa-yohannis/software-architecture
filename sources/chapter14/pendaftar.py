"""Pendaftar fungsi yang membaca manifes tanpa mengimpor satu modul pun.

Pemisahan antara pendaftaran dan pemuatan inilah yang memungkinkan turun ke
nol. Penjalan dapat menjawab pertanyaan peristiwa apa saja yang dilayani
walaupun tidak satu pun contoh fungsi sedang hidup, sebab jawabannya diambil
dari berkas manifes, bukan dari kode fungsinya.

Menambah satu fungsi baru karena itu cukup menaruh dua berkas di direktori
fungsi, yaitu modul beserta manifesnya. Skrip ukur_perubahan.py membuktikan
bahwa berkas ini dan penjalan.py sama sekali tidak ikut disunting.

Cara menjalankan: python pendaftar.py
"""

import json
import pathlib

import kontrak

DIREKTORI_FUNGSI = pathlib.Path(__file__).parent / "fungsi"
POLA_MANIFES = "fungsi_*.json"


class PendaftarFungsi:
  """Registri manifes fungsi, yaitu satu-satunya hal yang hidup saat nol."""

  def __init__(self, direktori: pathlib.Path = DIREKTORI_FUNGSI) -> None:
    """Menyiapkan registri kosong beserta direktori tempat manifes dicari.

    Registri sengaja dibiarkan kosong sampai temukan dipanggil, agar biaya
    pembacaan manifes terlihat sebagai langkah tersendiri pada pengukuran.
    """
    self.direktori = direktori
    self.manifes = {}

  def temukan(self) -> dict:
    """Membaca seluruh berkas manifes lalu menyimpannya di dalam registri.

    Manifes yang tidak memuat seluruh kunci wajib dilewati, sebab satu manifes
    cacat tidak boleh menghentikan pembacaan manifes lainnya. Mengembalikan
    dict berisi manifes yang lolos, dengan nama peristiwa sebagai kuncinya.
    """
    for berkas in sorted(self.direktori.glob(POLA_MANIFES)):
      isi = json.loads(berkas.read_text(encoding="utf-8"))
      if all(kunci in isi for kunci in kontrak.KUNCI_MANIFES):
        self.manifes[isi["peristiwa"]] = isi
    return self.manifes

  def manifes_untuk(self, peristiwa: str) -> dict:
    """Mengembalikan dict manifes satu peristiwa, dan melempar KeyError.

    Kegagalan sengaja dibiarkan naik, sebab peristiwa yang tidak terdaftar
    adalah kesalahan pemanggil, bukan kegagalan fungsinya.
    """
    return self.manifes[peristiwa]

  def daftar_peristiwa(self) -> list[tuple[str, str]]:
    """Menyusun isi registri menjadi daftar pasangan peristiwa dan keterangan.

    Daftar ini dapat dicetak tanpa mengimpor satu modul pun, sehingga sebuah
    penjalan yang sedang berada di angka nol tetap dapat menjawab pertanyaan
    peristiwa apa saja yang dilayaninya.
    """
    return [(m["peristiwa"], m["keterangan"]) for m in self.manifes.values()]

  def memori_dipesan_mb(self, peristiwa: str) -> int:
    """Mengembalikan int memori yang dipesan satu fungsi dalam megabita.

    Angka ini dibaca dari manifes, meniru pengaturan memori per fungsi pada
    AWS Lambda, dan menjadi pengali pada perhitungan gigabita detik.
    """
    return int(self.manifes[peristiwa]["memori_mb"])


def rakit_pendaftar() -> PendaftarFungsi:
  """Merangkai pendaftar pada satu tempat agar skrip lain tidak mengulanginya.

  Seluruh skrip pengukuran memakai fungsi ini, sehingga susunan yang diukur
  persis sama dengan yang dijalankan. Mengembalikan objek PendaftarFungsi yang
  manifesnya sudah terbaca.
  """
  pendaftar = PendaftarFungsi()
  pendaftar.temukan()
  return pendaftar


if __name__ == "__main__":
  registri = rakit_pendaftar()
  print(f"Fungsi terdaftar: {len(registri.manifes)}")
  # Keluarannya: Fungsi terdaftar: 3
  for nama_peristiwa, keterangan in registri.daftar_peristiwa():
    memori = registri.memori_dipesan_mb(nama_peristiwa)
    print(f"  {nama_peristiwa:<9} {memori:>4} MB  {keterangan}")
