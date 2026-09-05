"""Varian Model-View-Controller dengan antarmuka Tkinter.

Pengguna menyentuh widget milik View, lalu View meneruskannya ke Controller.
Controller memanggil Model, lalu memerintah View menggambar ulang. View membaca
Model secara langsung untuk mengambil nilai yang akan ditampilkan, sehingga View
wajib mengenal Model.

Cara menjalankan: python3 mvc.py
"""

import tkinter as tk

import domain


class Model:
  """Menyimpan hasil konversi terakhir beserta pesan galatnya."""

  def __init__(self):
    self.hasil = None
    self.galat = None

  def konversi(self, kode_asal, kode_tujuan, nominal):
    """Menghitung konversi lalu menyimpan hasilnya di dalam Model."""
    try:
      self.hasil = domain.hitung_konversi(kode_asal, kode_tujuan, nominal)
      self.galat = None
    except (ValueError, LookupError) as kesalahan:
      self.hasil = None
      self.galat = str(kesalahan)


class View:
  """Jendela Tkinter yang membaca Model untuk menyusun tampilannya.

  Konstruktornya menerima Model, dan di situlah ketergantungan MVC terlihat.
  View tidak dapat dibuat tanpa Model, sehingga pengujian pun menuntut keduanya.
  """

  def __init__(self, induk, model):
    self.model = model
    self.controller = None
    self.label = tk.Label(induk, text="", font=("Sans", 14))
    self.label.pack(padx=20, pady=20)
    self.tombol = tk.Button(induk, text="Hitung", command=self.saat_ditekan)
    self.tombol.pack(pady=(0, 20))

  def saat_ditekan(self):
    """Meneruskan tindakan pengguna ke Controller.

    Widget dimiliki View, sehingga pengguna menyentuh View. View hanya
    meneruskan, dan tidak memutuskan apa pun sendiri.
    """
    self.controller.tangani_masukan("USD", "IDR", 100)

  def render(self):
    """Membaca keadaan Model saat ini lalu memperbarui label."""
    if self.model.galat is not None:
      teks = f"Galat: {self.model.galat}"
    else:
      teks = f"Hasil: {self.model.hasil:,.2f}"
    self.label.config(text=teks)
    return teks


class Controller:
  """Menerima masukan pengguna lalu meneruskannya ke Model."""

  def __init__(self, model, view):
    self.model = model
    self.view = view

  def tangani_masukan(self, kode_asal, kode_tujuan, nominal):
    """Meneruskan masukan ke Model, lalu memerintah View menggambar ulang."""
    self.model.konversi(kode_asal, kode_tujuan, nominal)
    return self.view.render()


if __name__ == "__main__":
  jendela = tk.Tk()
  jendela.title("MVC")
  model = Model()
  tampilan = View(jendela, model)
  controller = Controller(model, tampilan)
  tampilan.controller = controller
  print(controller.tangani_masukan("USD", "IDR", 100))
  # Keluarannya: Hasil: 1,625,000.00
  jendela.mainloop()
