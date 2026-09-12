"""Inti microkernel yang menemukan, memuat, lalu menjalankan plugin.

Inti tidak menyebut nama satu plugin pun. Yang diketahuinya hanya direktori
tempat manifes berada dan bentuk kontrak pada kontrak.py. Menambah kemampuan
baru karena itu cukup menaruh satu berkas manifes beserta modulnya, tanpa
menyunting berkas ini sama sekali.

Aktivasi lambat ditiru dari Visual Studio Code. Manifes dibaca saat mulai,
sedangkan modul pluginnya baru diimpor ketika perintahnya benar-benar dipanggil.

Cara menjalankan:
  python inti.py daftar
  python inti.py konversi USD IDR 100
"""

import importlib
import json
import pathlib
import sys

import kontrak

DIREKTORI_PLUGIN = pathlib.Path(__file__).parent
POLA_MANIFES = "plugin_*.json"


class PluginRusak(Exception):
  """Ditandai ketika satu plugin gagal dimuat atau gagal dijalankan.

  Galat aslinya dibungkus agar inti dapat melanjutkan hidup. Tanpa pembungkus
  ini, satu plugin yang rusak menghentikan seluruh aplikasi.
  """


class Inti:
  """Pendaftar dan penjalan perintah yang berasal dari plugin.

  Registri hanya berisi manifes, bukan modul. Modul diimpor saat perintahnya
  dipanggil, lalu hasil impornya disimpan agar pemanggilan berikutnya tidak
  mengimpor ulang.
  """

  def __init__(self, direktori=DIREKTORI_PLUGIN):
    self.direktori = direktori
    self.manifes = {}
    self.modul_termuat = {}
    self.galat_muat = {}

  def temukan(self):
    """Membaca seluruh berkas manifes tanpa mengimpor satu modul pun.

    Manifes yang tidak memuat kunci wajib diabaikan, sebab manifes cacat tidak
    boleh menghentikan pemindaian manifes lainnya.
    """
    for berkas in sorted(self.direktori.glob(POLA_MANIFES)):
      isi = json.loads(berkas.read_text(encoding="utf-8"))
      if all(kunci in isi for kunci in kontrak.KUNCI_MANIFES):
        self.manifes[isi["perintah"]] = isi
    return self.manifes

  def daftar_perintah(self):
    """Mengembalikan pasangan nama perintah dan keterangannya."""
    return [(m["perintah"], m["keterangan"]) for m in self.manifes.values()]

  def aktifkan(self, perintah):
    """Mengimpor modul satu plugin, lalu menyimpan hasilnya.

    Impor dibungkus agar modul yang rusak tercatat sebagai galat, bukan
    menghentikan inti. Perilaku itulah yang diukur pada Latihan 2.
    """
    if perintah in self.modul_termuat:
      return self.modul_termuat[perintah]
    manifes = self.manifes[perintah]
    try:
      modul = importlib.import_module(manifes["modul"])
    except Exception as kesalahan:
      self.galat_muat[perintah] = str(kesalahan)
      raise PluginRusak(f"{manifes['nama']} gagal dimuat: {kesalahan}")
    self.modul_termuat[perintah] = modul
    return modul

  def aktifkan_semua(self):
    """Mengimpor seluruh modul plugin sekaligus, seperti aktivasi awal.

    Cara ini dipakai sebagai pembanding pada Latihan 3, sebab inilah yang
    dihindari Visual Studio Code lewat activation event.
    """
    jumlah = 0
    for perintah in self.manifes:
      try:
        self.aktifkan(perintah)
        jumlah += 1
      except PluginRusak:
        pass
    return jumlah

  def jalankan(self, perintah, argumen):
    """Menjalankan satu perintah, lalu mengembalikan teks hasilnya."""
    if perintah not in self.manifes:
      return f"Perintah {perintah} tidak dikenali"
    try:
      modul = self.aktifkan(perintah)
      return modul.jalankan(argumen)
    except PluginRusak as kesalahan:
      return f"Dilewati: {kesalahan}"


def rakit_inti():
  """Membuat inti yang manifesnya sudah terbaca, siap menerima perintah."""
  inti = Inti()
  inti.temukan()
  return inti


if __name__ == "__main__":
  inti = rakit_inti()
  if len(sys.argv) < 2 or sys.argv[1] == "daftar":
    print(f"Plugin terpasang: {len(inti.manifes)}")
    # Keluarannya: Plugin terpasang: 4
    for nama_perintah, keterangan in inti.daftar_perintah():
      print(f"  {nama_perintah:<10} {keterangan}")
    print(f"Modul yang sudah diimpor: {len(inti.modul_termuat)}")
    # Keluarannya: Modul yang sudah diimpor: 0
  else:
    print(inti.jalankan(sys.argv[1], sys.argv[2:]))
