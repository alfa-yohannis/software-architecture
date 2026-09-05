"""Varian Model-View-Presenter dengan antarmuka Tkinter.

Presenter mengerjakan seluruh penyusunan teks, lalu mendorong hasilnya ke View.
View bersifat pasif, hanya menerima teks yang sudah jadi, dan tidak mengenal
Model sama sekali. Pengguna menyentuh widget milik View, lalu View meneruskannya
kepada penangan yang dipasang Presenter.

Cara menjalankan: python3 mvp.py
"""

import tkinter as tk

import domain


class Model:
  """Menyediakan perhitungan konversi tanpa menyimpan keadaan tampilan."""

  def konversi(self, kode_asal, kode_tujuan, nominal):
    """Mengembalikan hasil konversi atau melemparkan galat aslinya."""
    return domain.hitung_konversi(kode_asal, kode_tujuan, nominal)


class View:
  """Jendela Tkinter yang hanya menampilkan teks yang diberikan Presenter.

  Tidak ada logika di dalamnya. Karena itu View ini dapat diganti tiruan
  sederhana saat diuji, tanpa membuat jendela sama sekali.
  """

  def __init__(self, induk):
    self.teks = None
    self.saat_ditekan = None
    self.label = tk.Label(induk, text="", font=("Sans", 14))
    self.label.pack(padx=20, pady=20)
    self.tombol = tk.Button(induk, text="Hitung", command=self.teruskan)
    self.tombol.pack(pady=(0, 20))

  def teruskan(self):
    """Meneruskan tindakan pengguna kepada penangan yang sudah dipasang.

    View tidak tahu siapa penangannya. Konstruktornya pun tidak menerima
    Presenter, sehingga View tetap tidak mengenal komponen mana pun.
    """
    self.saat_ditekan()

  def tampilkan(self, teks):
    """Menerima teks jadi dari Presenter lalu menampilkannya."""
    self.teks = teks
    self.label.config(text=teks)


class Presenter:
  """Menghubungkan Model dan View sekaligus menyusun teks tampilannya."""

  def __init__(self, model, view):
    self.model = model
    self.view = view
    view.saat_ditekan = lambda: self.tangani_masukan("USD", "IDR", 100)

  def tangani_masukan(self, kode_asal, kode_tujuan, nominal):
    """Menghitung konversi, menyusun teksnya, lalu mendorongnya ke View."""
    try:
      hasil = self.model.konversi(kode_asal, kode_tujuan, nominal)
      self.view.tampilkan(f"Hasil: {hasil:,.2f}")
    except (ValueError, LookupError) as kesalahan:
      self.view.tampilkan(f"Galat: {kesalahan}")
    return self.view.teks


if __name__ == "__main__":
  jendela = tk.Tk()
  jendela.title("MVP")
  # Tombol dimiliki View, sehingga pengguna menyentuh View bukan Presenter.
  presenter = Presenter(Model(), View(jendela))
  print(presenter.tangani_masukan("USD", "IDR", 100))
  # Keluarannya: Hasil: 1,625,000.00
  jendela.mainloop()
