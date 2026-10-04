"""Kumpulan filter yang menyusun pipeline pengolah gambar pada bab ini.

Setiap filter menerima satu stream lalu menghasilkan stream baru. Filter tanpa
pengaturan ditulis sebagai fungsi generator, sedangkan filter yang butuh
pengaturan ditulis sebagai kelas yang dapat dipanggil. Keduanya dipakai pipeline
dengan cara yang sama persis.

Tidak satu pun filter menyebut nama filter lain, sebab yang menyambung mereka
adalah pipe. Kemandirian itu yang diukur pada Latihan 1 sebagai filter
independence.

Bentuk data yang mengalir adalah tuple berisi nama file dan objek gambar,
kecuali pada stage penyimpanan yang menghasilkan laporan.

Cara menjalankan: file ini diimpor oleh pipa.py, bukan dijalankan langsung.
"""

import pathlib

from PIL import Image

POLA_MASUKAN = "*.jpg"
MODE_BAKU = "RGB"
BAGIAN_LEBAR_TANDA = 0.32
JARAK_TEPI = 24


def baca_gambar(direktori, batas: int | None = None):
  """Membuka file gambar satu per satu tanpa memuat seluruh direktori.

  Pembacaan mengalir agar pipeline dapat mulai bekerja sebelum file terakhir
  dibuka, dan agar memori tidak menampung seluruh kumpulan sekaligus. Batas
  dipakai skrip pengukuran agar putarannya tidak terlalu lama. Menghasilkan
  tuple berisi nama file dan objek Image.
  """
  berkas_terurut = sorted(pathlib.Path(direktori).glob(POLA_MASUKAN))
  for berkas in berkas_terurut[:batas]:
    yield berkas.name, Image.open(berkas)


def ubah_mode(masukan):
  """Menyeragamkan mode warna setiap gambar menjadi RGB.

  File dari sumber yang berbeda kerap memakai mode berbeda, misalnya berindeks
  atau abu-abu. Penyeragaman di hulu membuat stage sesudahnya tidak perlu
  memeriksa mode lagi. Menghasilkan tuple nama dan Image bermode RGB.
  """
  for nama, gambar in masukan:
    yield nama, gambar.convert(MODE_BAKU) if gambar.mode != MODE_BAKU else gambar


class Resize:
  """Filter yang menyeragamkan lebar gambar sambil menjaga rasionya.

  Lebar tujuan disimpan pada objek, sehingga satu kelas yang sama dapat dipakai
  beberapa kali dengan ukuran berbeda pada cabang yang berbeda.
  """

  def __init__(self, lebar: int) -> None:
    """Menyimpan lebar tujuan yang dipakai seluruh gambar pada stage ini."""
    self.lebar = lebar

  def __call__(self, masukan):
    """Mengubah ukuran setiap gambar ke lebar tujuan dengan rasio tetap.

    Gambar yang sudah lebih kecil tetap diperkecil agar keluarannya seragam,
    sebab tujuan stage ini adalah penyeragaman, bukan penghematan. Menghasilkan
    tuple nama dan Image dengan lebar yang sama.
    """
    for nama, gambar in masukan:
      tinggi = round(gambar.height * self.lebar / gambar.width)
      yield nama, gambar.resize((self.lebar, tinggi), Image.LANCZOS)


class Watermark:
  """Filter yang menyatukan gambar dengan satu file tanda air.

  Stage ini adalah merge, yaitu dua sumber gambar menjadi satu keluaran. Tanda
  airnya dibaca sekali saat objek dibuat, bukan pada setiap gambar.
  """

  def __init__(self, berkas_tanda: str) -> None:
    """Membaca file tanda air sekali lalu menyimpannya sebagai RGBA."""
    self.tanda = Image.open(berkas_tanda).convert("RGBA")

  def __call__(self, masukan):
    """Menempelkan tanda air di sudut kanan bawah setiap gambar.

    Tanda air diperkecil mengikuti lebar gambarnya, sehingga porsinya tetap
    sama pada resolusi mana pun. Penempelan memakai alpha channel, sehingga
    bagian tembus pandang tetap tembus. Menghasilkan tuple nama dan Image.
    """
    for nama, gambar in masukan:
      lebar_tanda = max(1, int(gambar.width * BAGIAN_LEBAR_TANDA))
      tinggi_tanda = round(self.tanda.height * lebar_tanda / self.tanda.width)
      tanda = self.tanda.resize((lebar_tanda, tinggi_tanda), Image.LANCZOS)
      letak = (gambar.width - lebar_tanda - JARAK_TEPI,
               gambar.height - tinggi_tanda - JARAK_TEPI)
      salinan = gambar.copy()
      salinan.paste(tanda, letak, tanda)
      yield nama, salinan


class SaveJpeg:
  """Filter ujung yang menulis gambar sebagai JPEG dengan kualitas tetap.

  Direktori dan kualitas disimpan pada objek, sehingga cabang yang berbeda
  dapat menulis ke tempat berbeda dengan mutu berbeda tanpa kelas baru.
  """

  def __init__(self, direktori: str, kualitas: int) -> None:
    """Menyiapkan direktori tujuan beserta kualitas JPEG yang dipakai."""
    self.direktori = pathlib.Path(direktori)
    self.direktori.mkdir(parents=True, exist_ok=True)
    self.kualitas = kualitas

  def __call__(self, masukan):
    """Menulis setiap gambar lalu melaporkan ukuran file hasilnya.

    Laporan dikembalikan sebagai stream agar stage sesudahnya, misalnya
    penggabungan laporan, tetap dapat bekerja mengalir. Menghasilkan tuple
    berisi nama file, nama direktori, dan ukuran file dalam bait.
    """
    for nama, gambar in masukan:
      tujuan = self.direktori / f"{pathlib.Path(nama).stem}.jpg"
      gambar.save(tujuan, "JPEG", quality=self.kualitas, optimize=True)
      yield nama, self.direktori.name, tujuan.stat().st_size
