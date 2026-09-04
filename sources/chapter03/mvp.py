"""Varian Model-View-Presenter.

Presenter mengerjakan seluruh penyusunan teks, lalu mendorong hasilnya ke View.
View bersifat pasif, hanya menyimpan apa yang diberikan Presenter, dan tidak
mengenal Model sama sekali.

Cara menjalankan: python mvp.py
"""

import domain


class Model:
  """Menyediakan perhitungan konversi tanpa menyimpan keadaan tampilan."""

  def konversi(self, kode_asal, kode_tujuan, nominal):
    """Mengembalikan hasil konversi atau melemparkan galat aslinya."""
    return domain.hitung_konversi(kode_asal, kode_tujuan, nominal)


class View:
  """Menyimpan teks yang diberikan Presenter, tanpa logika apa pun.

  View pasif seperti ini dapat diganti tiruan sederhana saat diuji, sebab tidak
  ada perilaku yang perlu ditiru selain menyimpan teks.
  """

  def __init__(self):
    self.teks = None

  def tampilkan(self, teks):
    """Menerima teks jadi dari Presenter."""
    self.teks = teks


class Presenter:
  """Menghubungkan Model dan View sekaligus menyusun teks tampilannya."""

  def __init__(self, model, view):
    self.model = model
    self.view = view

  def tangani_masukan(self, kode_asal, kode_tujuan, nominal):
    """Menghitung konversi, menyusun teksnya, lalu mendorongnya ke View."""
    try:
      hasil = self.model.konversi(kode_asal, kode_tujuan, nominal)
      self.view.tampilkan(f"Hasil: {hasil:,.2f}")
    except (ValueError, LookupError) as kesalahan:
      self.view.tampilkan(f"Galat: {kesalahan}")
    return self.view.teks


if __name__ == "__main__":
  tampilan = View()
  print(Presenter(Model(), tampilan).tangani_masukan("USD", "IDR", 100))
  # Keluarannya: Hasil: 1,625,000.00
