"""Varian Model-View-ViewModel.

ViewModel menyimpan properti yang dapat diamati. View mendaftarkan diri sebagai
pengamat, lalu memperbarui dirinya sendiri setiap kali properti berubah.
ViewModel tidak mengenal View, sehingga arah ketergantungannya hanya satu.

Cara menjalankan: python mvvm.py
"""

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
  """Mengikat diri pada properti ViewModel dan menyimpan nilai terbarunya."""

  def __init__(self, view_model):
    self.terakhir = None
    self.jumlah_render = 0
    view_model.teks.amati(self.saat_berubah)

  def saat_berubah(self, teks_baru):
    """Dipanggil otomatis oleh properti setiap kali nilainya berubah."""
    self.terakhir = teks_baru
    self.jumlah_render += 1


if __name__ == "__main__":
  view_model = ViewModel(Model())
  tampilan = View(view_model)
  view_model.tangani_masukan("USD", "IDR", 100)
  print(tampilan.terakhir)
  # Keluarannya: Hasil: 1,625,000.00
