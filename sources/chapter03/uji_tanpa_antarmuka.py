"""Menguji logika keempat varian dengan seminimal mungkin menyentuh antarmuka.

Sejak View memakai Tkinter, perbedaan antar varian menjadi nyata. Varian yang
View-nya bergantung pada komponen lain menuntut jendela sungguhan dibuat lebih
dahulu, sedangkan varian yang View-nya mandiri dapat diuji tanpa jendela sama
sekali.

Cara menjalankan: python3 uji_tanpa_antarmuka.py
"""

import mvc
import mvi
import mvp
import mvvm

NOMINAL_UJI = 100
HASIL_DIHARAPKAN = "Hasil: 1,625,000.00"


class ViewTiruan:
  """Pengganti View pasif pada MVP, hanya menyimpan teks yang diterimanya."""

  def __init__(self):
    self.teks = None

  def tampilkan(self, teks):
    """Menyimpan teks tanpa membuat jendela apa pun."""
    self.teks = teks


def uji_mvc():
  """MVC menuntut jendela sungguhan, sebab View-nya membaca Model.

  View pada MVC membuat widget di dalam konstruktornya, sehingga pengujian
  tidak dapat berjalan tanpa jendela Tkinter.
  """
  import tkinter as tk
  jendela = tk.Tk()
  jendela.withdraw()
  model = mvc.Model()
  tampilan = mvc.View(jendela, model)
  hasil = mvc.Controller(model, tampilan).tangani_masukan("USD", "IDR", NOMINAL_UJI)
  jendela.destroy()
  return hasil == HASIL_DIHARAPKAN, "butuh jendela Tkinter"


def uji_mvp():
  """MVP dapat diuji dengan View tiruan, sebab View-nya pasif."""
  tampilan = ViewTiruan()
  presenter = mvp.Presenter(mvp.Model(), tampilan)
  hasil = presenter.tangani_masukan("USD", "IDR", NOMINAL_UJI)
  return hasil == HASIL_DIHARAPKAN, "cukup View tiruan, tanpa jendela"


def uji_mvvm():
  """MVVM dapat diuji tanpa View sama sekali, cukup membaca propertinya."""
  view_model = mvvm.ViewModel(mvvm.Model())
  view_model.tangani_masukan("USD", "IDR", NOMINAL_UJI)
  return view_model.teks.nilai == HASIL_DIHARAPKAN, "tanpa View, tanpa jendela"


def uji_mvi():
  """MVI dapat diuji tanpa View sama sekali, cukup memanggil fungsi reduksi."""
  intent = mvi.IntentKonversi("USD", "IDR", NOMINAL_UJI)
  keadaan = mvi.reduksi(mvi.Keadaan(), intent)
  return keadaan.teks == HASIL_DIHARAPKAN, "tanpa View, tanpa jendela"


if __name__ == "__main__":
  for nama, fungsi_uji in [("mvc", uji_mvc), ("mvp", uji_mvp),
                           ("mvvm", uji_mvvm), ("mvi", uji_mvi)]:
    lulus, keterangan = fungsi_uji()
    print(f"{nama:<5} lulus={lulus}  cara uji: {keterangan}")
  # Keluarannya: mvc   lulus=True  cara uji: butuh jendela Tkinter
