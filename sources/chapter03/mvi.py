"""Varian Model-View-Intent dengan antarmuka Tkinter.

Setiap tindakan pengguna dibungkus sebagai Intent. Sebuah fungsi reduksi
mengubah pasangan keadaan lama dan Intent menjadi keadaan baru yang tidak dapat
diubah lagi. View hanya menggambar keadaan tersebut.

Cara menjalankan: python3 mvi.py
"""

import tkinter as tk
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
    hasil = domain.hitung_konversi(intent.kode_asal, intent.kode_tujuan,
                                   intent.nominal)
    return replace(keadaan, teks=f"Hasil: {hasil:,.2f}", sedang_sibuk=False)
  except (ValueError, LookupError) as kesalahan:
    return replace(keadaan, teks=f"Galat: {kesalahan}", sedang_sibuk=False)


class View:
  """Jendela Tkinter yang menggambar sebuah Keadaan lalu menyimpannya.

  View menerima Keadaan sebagai argumen, bukan menyimpan rujukan ke komponen
  lain. Karena itu View tidak bergantung pada apa pun.
  """

  def __init__(self, induk):
    self.riwayat = []
    self.label = tk.Label(induk, text="", font=("Sans", 14))
    self.label.pack(padx=20, pady=20)

  def gambar(self, keadaan):
    """Menyimpan keadaan yang digambar lalu menampilkan teksnya."""
    self.riwayat.append(keadaan)
    self.label.config(text=keadaan.teks)
    return keadaan.teks


if __name__ == "__main__":
  jendela = tk.Tk()
  jendela.title("MVI")
  tampilan = View(jendela)
  # View membungkus tindakan pengguna menjadi Intent, lalu mereduksinya.
  tk.Button(jendela, text="Hitung",
            command=lambda: tampilan.gambar(
              reduksi(tampilan.riwayat[-1], IntentKonversi("USD", "IDR", 100)))).pack()
  keadaan_kini = reduksi(Keadaan(), IntentKonversi("USD", "IDR", 100))
  print(tampilan.gambar(keadaan_kini))
  # Keluarannya: Hasil: 1,625,000.00
  jendela.mainloop()
