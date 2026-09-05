"""Varian Model-View-ViewModel dengan antarmuka Tkinter.

ViewModel menyimpan properti yang dapat diamati. View mendaftarkan diri sebagai
pengamat, lalu memperbarui dirinya sendiri setiap kali properti berubah.
ViewModel tidak mengenal View, sehingga arah ketergantungannya hanya satu.

Cara menjalankan: python3 mvvm.py
"""

import tkinter as tk

import domain


class Properti:
  """Nilai yang memberi tahu pengamatnya setiap kali isinya berubah.

  Kelas kecil ini menggantikan mekanisme data binding yang pada framework nyata
  disediakan oleh pustaka antarmuka.
  """

  def __init__(self, nilai_awal=None):
    self.nilai = nilai_awal
    self.pengamat = []

  def amati(self, fungsi_pengamat):
    """Mendaftarkan satu fungsi yang dipanggil setiap nilai berubah."""
    self.pengamat.append(fungsi_pengamat)

  def ubah(self, nilai_baru):
    """Mengganti nilai lalu memberi tahu seluruh pengamatnya."""
    self.nilai = nilai_baru
    for fungsi_pengamat in self.pengamat:
      fungsi_pengamat(nilai_baru)


class Model:
  """Menyediakan perhitungan konversi tanpa menyimpan keadaan tampilan."""

  def konversi(self, kode_asal, kode_tujuan, nominal):
    """Mengembalikan hasil konversi atau melemparkan galat aslinya."""
    return domain.hitung_konversi(kode_asal, kode_tujuan, nominal)


class ViewModel:
  """Menyimpan teks tampilan sebagai properti yang dapat diamati."""

  def __init__(self, model):
    self.model = model
    self.teks = Properti("")

  def tangani_masukan(self, kode_asal, kode_tujuan, nominal):
    """Menghitung konversi lalu menuliskan hasilnya ke properti teks."""
    try:
      hasil = self.model.konversi(kode_asal, kode_tujuan, nominal)
      self.teks.ubah(f"Hasil: {hasil:,.2f}")
    except (ValueError, LookupError) as kesalahan:
      self.teks.ubah(f"Galat: {kesalahan}")


class View:
  """Jendela Tkinter yang mengikat labelnya pada properti ViewModel.

  View mendaftar sekali di awal, lalu tidak pernah dipanggil ViewModel secara
  langsung. Propertilah yang memberi tahu setiap pengamatnya.
  """

  def __init__(self, induk, view_model):
    self.jumlah_render = 0
    self.label = tk.Label(induk, text="", font=("Sans", 14))
    self.label.pack(padx=20, pady=20)
    view_model.teks.amati(self.saat_berubah)

  def saat_berubah(self, teks_baru):
    """Dipanggil otomatis oleh properti setiap kali nilainya berubah."""
    self.jumlah_render += 1
    self.label.config(text=teks_baru)


if __name__ == "__main__":
  jendela = tk.Tk()
  jendela.title("MVVM")
  view_model = ViewModel(Model())
  View(jendela, view_model)
  # View meneruskan tindakan pengguna ke ViewModel.
  tk.Button(jendela, text="Hitung",
            command=lambda: view_model.tangani_masukan("USD", "IDR", 100)).pack()
  view_model.tangani_masukan("USD", "IDR", 100)
  print(view_model.teks.nilai)
  # Keluarannya: Hasil: 1,625,000.00
  jendela.mainloop()
