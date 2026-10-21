"""Menyalakan seluruh layanan Bab 12 pada utasnya masing-masing.

Empat belas server dinyalakan sekaligus, yaitu mesin orkestrasi, tujuh layanan
pasif versi orkestrasi, dan enam layanan versi tanpa orkestrasi. Seluruhnya
berjalan di dalam satu proses Python agar latihan cukup dijalankan dengan satu
perintah, sedangkan pemanggilan antar layanan tetap lewat HTTP.

Kumpulan ini juga menyediakan cara mematikan dan menyalakan kembali satu
layanan. Kemampuan itu dipakai skrip kegagalan, yang memang perlu mematikan
satu layanan di tengah alur kerja.

Cara menjalankan: python server.py
"""

import importlib
import logging
import threading

import werkzeug.serving

import konfigurasi
import layanan
import orkestrator

# Werkzeug mencetak satu baris log untuk setiap permintaan. Pada pengukuran
# dua ratus alur kerja, cetakan itu sendiri menjadi biaya yang ikut terukur.
logging.getLogger("werkzeug").setLevel(logging.ERROR)

BATAS_TUTUP = 3.0


def buat_aplikasi_berantai(nama: str):
  """Mengimpor modul satu layanan berantai lalu membentuk aplikasinya.

  Modulnya dicari berdasarkan namanya, sehingga menambah layanan berantai baru
  tidak menuntut penyuntingan berkas ini. Mengembalikan objek Flask milik
  layanan tersebut.
  """
  modul = importlib.import_module(f"berantai.{nama}")
  return modul.buat_aplikasi()


class KumpulanLayanan:
  """Pengelola seluruh server HTTP yang dipakai latihan bab ini.

  Setiap server disimpan dengan kunci berupa pasangan versi dan nama layanan,
  sehingga satu layanan dapat dimatikan tanpa mengganggu yang lain. Mesin
  orkestrasi dibuat sekali di sini agar riwayat prosesnya tetap utuh selama
  skrip berjalan.
  """

  def __init__(self) -> None:
    """Menyiapkan mesin orkestrasi beserta daftar server yang masih kosong.

    Server belum satu pun dinyalakan di sini, sebab sebagian skrip hanya
    membutuhkan salah satu versi. Konstruktor tidak mengembalikan nilai.
    """
    self.mesin = orkestrator.MesinOrkestrasi()
    self.server = {}

  def port_layanan(self, versi: str, nama: str) -> int:
    """Menentukan port sebuah layanan berdasarkan versi dan namanya.

    Mengembalikan int berisi nomor port yang dipakai layanan tersebut.
    """
    if versi == "mesin":
      return konfigurasi.PORT_MESIN
    if versi == "orkestrasi":
      return konfigurasi.PORT_ORKESTRASI[nama]
    return konfigurasi.PORT_BERANTAI[nama]

  def buat_aplikasi(self, versi: str, nama: str):
    """Membentuk aplikasi Flask yang sesuai dengan versi dan nama layanan.

    Mengembalikan objek Flask milik layanan tersebut.
    """
    if versi == "mesin":
      return orkestrator.buat_aplikasi(self.mesin)
    if versi == "orkestrasi":
      return layanan.buat_layanan(nama)
    return buat_aplikasi_berantai(nama)

  def nyalakan(self, versi: str, nama: str = "") -> None:
    """Menyalakan satu layanan pada utas tersendiri bila belum hidup.

    Soket sudah terbuka begitu server dibentuk, sehingga pemanggil tidak perlu
    menunggu. Tidak mengembalikan nilai.
    """
    kunci = (versi, nama)
    if kunci in self.server:
      return
    aplikasi = self.buat_aplikasi(versi, nama)
    port = self.port_layanan(versi, nama)
    server = werkzeug.serving.make_server(konfigurasi.ALAMAT, port, aplikasi,
                                          threaded=True)
    utas = threading.Thread(target=server.serve_forever, daemon=True)
    utas.start()
    self.server[kunci] = (server, utas)

  def matikan(self, versi: str, nama: str = "") -> None:
    """Menghentikan satu layanan lalu melepaskan portnya.

    Port wajib dilepas, sebab skrip kegagalan menyalakan kembali layanan yang
    sama pada port yang sama. Tidak mengembalikan nilai.
    """
    kunci = (versi, nama)
    if kunci not in self.server:
      return
    server, utas = self.server.pop(kunci)
    server.shutdown()
    utas.join(timeout=BATAS_TUTUP)
    server.server_close()

  def nyalakan_semua(self) -> int:
    """Menyalakan mesin orkestrasi beserta kedua kumpulan layanan.

    Mengembalikan int berisi jumlah server yang sedang hidup.
    """
    self.nyalakan("mesin")
    for nama in konfigurasi.PORT_ORKESTRASI:
      self.nyalakan("orkestrasi", nama)
    for nama in konfigurasi.PORT_BERANTAI:
      self.nyalakan("berantai", nama)
    return len(self.server)

  def matikan_semua(self) -> None:
    """Menghentikan seluruh server yang masih hidup.

    Tidak mengembalikan nilai.
    """
    for versi, nama in list(self.server):
      self.matikan(versi, nama)


if __name__ == "__main__":
  kumpulan = KumpulanLayanan()
  jumlah = kumpulan.nyalakan_semua()
  print(f"Server hidup          : {jumlah}")
  print(f"Mesin orkestrasi      : port {konfigurasi.PORT_MESIN}")
  print(f"Layanan orkestrasi    : {len(konfigurasi.PORT_ORKESTRASI)}")
  print(f"Layanan berantai      : {len(konfigurasi.PORT_BERANTAI)}")
  print("Tekan Ctrl+C untuk berhenti.")
  try:
    threading.Event().wait()
  except KeyboardInterrupt:
    kumpulan.matikan_semua()
    print("\nSeluruh server berhenti.")
  # Keluarannya: Server hidup          : 14
