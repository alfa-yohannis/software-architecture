"""Varian Model-View-Controller klasik seperti pada Smalltalk-80.

Model memberi tahu setiap pengamat yang terdaftar ketika isinya berubah, lalu
View menarik sendiri nilainya dari Model. Pemberitahuannya tidak membawa data
apa pun, sehingga View wajib mengenal Model. Controller memiliki tombolnya
sendiri, sehingga pengguna menyentuh Controller, bukan View. Controller juga
tidak pernah menyimpan rujukan ke View.

Bandingkan berkas ini dengan mvc.py, yaitu bentuk MVC masa kini, tempat
Controller memerintah View menggambar ulang.

Cara menjalankan: python3 mvc_klasik.py
"""

import tkinter as tk

import domain


class Model:
  """Menyimpan hasil konversi terakhir lalu memberi tahu para pengamatnya.

  Daftar pengamat berisi fungsi, bukan objek View, sehingga Model tidak pernah
  mengenal jenis tampilan yang memakainya. Satu Model karena itu dapat melayani
  beberapa tampilan sekaligus tanpa diubah.
  """

  def __init__(self):
    self.hasil = None
    self.galat = None
    self.pengamat = []

  def amati(self, fungsi_pengamat):
    """Mendaftarkan satu fungsi yang dipanggil setiap isi Model berubah.

    Pendaftaran dijalankan sekali saat aplikasi disusun, bukan pada setiap
    tindakan pengguna.
    """
    self.pengamat.append(fungsi_pengamat)

  def beri_tahu(self):
    """Memanggil seluruh pengamat tanpa menyertakan nilai apa pun.

    Pemberitahuan sengaja dibiarkan kosong, sebab di situlah letak ciri MVC
    klasik. Penerimanya yang menarik sendiri nilai yang dibutuhkannya.
    """
    for fungsi_pengamat in self.pengamat:
      fungsi_pengamat()

  def konversi(self, kode_asal, kode_tujuan, nominal):
    """Menghitung konversi, menyimpan hasilnya, lalu memberi tahu pengamatnya."""
    try:
      self.hasil = domain.hitung_konversi(kode_asal, kode_tujuan, nominal)
      self.galat = None
    except (ValueError, LookupError) as kesalahan:
      self.hasil = None
      self.galat = str(kesalahan)
    self.beri_tahu()


class View:
  """Label Tkinter yang mendaftar sebagai pengamat Model.

  Konstruktornya menerima Model untuk dua keperluan, yaitu mendaftarkan diri
  sebagai pengamat dan menarik nilainya nanti. View karena itu tidak dapat
  dibuat tanpa Model, dan pengujiannya pun menuntut keduanya.
  """

  def __init__(self, induk, model):
    self.model = model
    self.teks = ""
    self.label = tk.Label(induk, text="", font=("Sans", 14))
    self.label.pack(padx=20, pady=20)
    model.amati(self.berubah)

  def berubah(self):
    """Dipanggil Model setiap kali isinya berubah, tanpa membawa nilai.

    Nilainya ditarik sendiri dari Model pada baris berikutnya, dan tarikan
    itulah yang membuat View wajib mengenal Model.
    """
    if self.model.galat is not None:
      self.teks = f"Galat: {self.model.galat}"
    else:
      self.teks = f"Hasil: {self.model.hasil:,.2f}"
    self.label.config(text=self.teks)
    return self.teks


class Controller:
  """Menerima tindakan pengguna lalu meneruskannya ke Model.

  Tombolnya dimiliki Controller, sesuai bentuk aslinya yang menyerahkan seluruh
  penanganan masukan ke Controller. Rujukan ke View tidak disimpan sama sekali,
  sebab penggambaran ulang dipicu Model lewat pemberitahuan.
  """

  def __init__(self, induk, model):
    self.model = model
    self.tombol = tk.Button(induk, text="Hitung", command=self.saat_ditekan)
    self.tombol.pack(pady=(0, 20))

  def saat_ditekan(self):
    """Menangani penekanan tombol dengan nilai contoh yang tetap."""
    self.tangani_masukan("USD", "IDR", 100)

  def tangani_masukan(self, kode_asal, kode_tujuan, nominal):
    """Meneruskan masukan ke Model, lalu berhenti di situ.

    Tidak ada perintah menggambar di sini. View yang menerima pemberitahuan
    dari Model, lalu memperbarui dirinya sendiri.
    """
    self.model.konversi(kode_asal, kode_tujuan, nominal)


if __name__ == "__main__":
  jendela = tk.Tk()
  jendela.title("MVC Klasik")
  model = Model()
  tampilan = View(jendela, model)
  controller = Controller(jendela, model)
  controller.tangani_masukan("USD", "IDR", 100)
  print(tampilan.teks)
  # Keluarannya: Hasil: 1,625,000.00
  jendela.mainloop()
