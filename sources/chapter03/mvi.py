"""Varian Model-View-Intent.

Setiap tindakan pengguna dibungkus sebagai Intent. Sebuah fungsi reduksi
mengubah pasangan keadaan lama dan Intent menjadi keadaan baru yang tidak dapat
diubah lagi. View hanya menggambar keadaan tersebut.

Cara menjalankan: python mvi.py
"""

from dataclasses import dataclass, replace

import domain


@dataclass(frozen=True)
class Keadaan:
  """Keadaan tampilan yang tidak dapat diubah setelah dibuat.

  Karena setiap perubahan menghasilkan objek baru, seluruh riwayat interaksi
  dapat disimpan lalu diputar ulang persis seperti semula.
  """

  teks: str = ""
  sedang_sibuk: bool = False


@dataclass(frozen=True)
class IntentKonversi:
  """Menyatakan niat pengguna untuk mengonversi sejumlah nominal."""

  kode_asal: str
  kode_tujuan: str
  nominal: float


def reduksi(keadaan, intent):
  """Mengubah keadaan lama dan sebuah Intent menjadi keadaan baru.

  Fungsi ini murni, artinya keluarannya hanya bergantung pada kedua masukannya.
  Sifat itulah yang membuat riwayat tampilan dapat diputar ulang.
  """
  try:
    hasil = domain.hitung_konversi(intent.kode_asal, intent.kode_tujuan, intent.nominal)
    return replace(keadaan, teks=f"Hasil: {hasil:,.2f}", sedang_sibuk=False)
  except (ValueError, LookupError) as kesalahan:
    return replace(keadaan, teks=f"Galat: {kesalahan}", sedang_sibuk=False)


class View:
  """Menggambar keadaan dan menyimpan seluruh keadaan yang pernah digambar."""

  def __init__(self):
    self.riwayat = []

  def gambar(self, keadaan):
    """Menyimpan keadaan yang digambar lalu mengembalikan teksnya."""
    self.riwayat.append(keadaan)
    return keadaan.teks


if __name__ == "__main__":
  tampilan = View()
  keadaan_kini = reduksi(Keadaan(), IntentKonversi("USD", "IDR", 100))
  print(tampilan.gambar(keadaan_kini))
  # Keluarannya: Hasil: 1,625,000.00
