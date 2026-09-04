"""Varian Model-View-Controller.

Controller menerima masukan, memanggil Model, lalu memerintahkan View
menampilkan hasilnya. View membaca Model secara langsung untuk mengambil nilai
yang akan ditampilkan.

Cara menjalankan: python mvc.py
"""

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
  """Membaca Model lalu menyusun teks yang akan ditampilkan.

  View pada MVC mengenal Model, sehingga pengujian View tetap membutuhkan
  sebuah objek Model.
  """

  def __init__(self, model):
    self.model = model

  def render(self):
    """Menyusun satu baris teks dari keadaan Model saat ini."""
    if self.model.galat is not None:
      return f"Galat: {self.model.galat}"
    return f"Hasil: {self.model.hasil:,.2f}"


class Controller:
  """Menerima masukan pengguna lalu meneruskannya ke Model."""

  def __init__(self, model, view):
    self.model = model
    self.view = view

  def tangani_masukan(self, kode_asal, kode_tujuan, nominal):
    """Meneruskan masukan ke Model, lalu meminta View menyusun tampilannya."""
    self.model.konversi(kode_asal, kode_tujuan, nominal)
    return self.view.render()


if __name__ == "__main__":
  model = Model()
  print(Controller(model, View(model)).tangani_masukan("USD", "IDR", 100))
  # Keluarannya: Hasil: 1,625,000.00
