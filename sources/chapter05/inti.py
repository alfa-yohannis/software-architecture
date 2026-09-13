"""Inti microkernel yang menemukan, memuat, lalu menjalankan plugin.

Inti tidak menyebut nama satu plugin pun. Yang diketahuinya hanya direktori
tempat manifes berada dan bentuk kontrak pada kontrak.py. Menambah kemampuan
baru karena itu cukup menaruh satu berkas manifes beserta modulnya, tanpa
menyunting berkas ini sama sekali.

Pemuatannya memakai importlib dan getattr, yaitu padanan Class.forName beserta
konstruktor hasil refleksi pada contoh Java di java-example. Aktivasi lambat
ditiru dari Visual Studio Code. Manifes dibaca saat mulai, sedangkan modul
pluginnya baru diimpor ketika perintahnya benar-benar dipanggil.

Cara menjalankan:
  python inti.py daftar
  python inti.py konversi USD IDR 100
"""

import importlib
import json
import pathlib
import sys

import kontrak

DIREKTORI_PLUGIN = pathlib.Path(__file__).parent / "plugins"
POLA_MANIFES = "plugin_*.json"


class PluginGagal(Exception):
  """Ditandai ketika satu plugin gagal dimuat atau gagal dijalankan.

  Galat aslinya dibungkus agar inti dapat melanjutkan hidup. Tanpa pembungkus
  ini, satu plugin yang rusak menghentikan seluruh aplikasi.
  """


class Inti:
  """Pendaftar dan penjalan kemampuan yang berasal dari plugin.

  Registri hanya berisi manifes, bukan objek plugin. Objeknya dibuat saat
  perintahnya dipanggil, lalu disimpan agar pemanggilan berikutnya tidak
  mengimpor dan menginstansiasi ulang.
  """

  def __init__(self, direktori: pathlib.Path = DIREKTORI_PLUGIN) -> None:
    """Menyiapkan tiga registri kosong sebelum manifes apa pun dibaca.

    Registri sengaja dipisah menjadi tiga, yaitu manifes yang terbaca, plugin
    yang sudah aktif, dan galat pemuatan. Pemisahan itu membuat inti dapat
    melaporkan plugin yang gagal tanpa kehilangan yang berhasil.
    """
    self.direktori = direktori
    self.manifes = {}
    self.plugin_aktif = {}
    self.galat_muat = {}

  def temukan(self) -> dict:
    """Membaca seluruh berkas manifes tanpa mengimpor satu modul pun.

    Manifes yang tidak memuat kunci wajib diabaikan, sebab manifes cacat tidak
    boleh menghentikan pemindaian manifes lainnya. Mengembalikan dict berisi
    manifes yang lolos, dengan nama perintah sebagai kuncinya.
    """
    for berkas in sorted(self.direktori.glob(POLA_MANIFES)):
      isi = json.loads(berkas.read_text(encoding="utf-8"))
      if all(kunci in isi for kunci in kontrak.KUNCI_MANIFES):
        self.manifes[isi["perintah"]] = isi
    return self.manifes

  def daftar_perintah(self) -> list[tuple[str, str]]:
    """Menyusun isi registri menjadi daftar yang siap ditampilkan.

    Keterangan diambil dari manifes, bukan dari kode pluginnya, sehingga daftar
    ini dapat dicetak tanpa mengimpor satu modul pun. Mengembalikan list berisi
    pasangan nama perintah dan keterangannya.
    """
    return [(m["perintah"], m["keterangan"]) for m in self.manifes.values()]

  def aktifkan(self, perintah: str) -> kontrak.Plugin:
    """Mengimpor modul, mengambil kelasnya, lalu membuat objek pluginnya.

    Kelas diambil lewat getattr, dan objeknya menerima inti sebagai argumen
    konstruktor. Seluruh langkahnya dibungkus agar plugin yang rusak tercatat
    sebagai galat, bukan menghentikan inti. Perilaku itu diukur pada Latihan 2.
    Mengembalikan objek plugin yang memenuhi kontrak.Plugin, dan melempar
    PluginGagal bila salah satu langkahnya gagal.
    """
    if perintah in self.plugin_aktif:
      return self.plugin_aktif[perintah]  # objek pemenuh kontrak.Plugin
    manifes = self.manifes[perintah]
    try:
      modul = importlib.import_module(manifes["modul"])
      kelas = getattr(modul, manifes["kelas"])
      plugin = kelas(self)
    except Exception as kesalahan:
      self.galat_muat[perintah] = str(kesalahan)
      raise PluginGagal(f"{manifes['nama']} gagal dimuat: {kesalahan}")
    self.plugin_aktif[perintah] = plugin
    return plugin

  def aktifkan_semua(self) -> int:
    """Mengaktifkan seluruh plugin sekaligus, seperti aktivasi awal.

    Cara ini dipakai sebagai pembanding pada Latihan 3, sebab inilah yang
    dihindari Visual Studio Code lewat activation event. Mengembalikan int
    berisi jumlah plugin yang berhasil aktif, sehingga yang gagal terlihat dari
    selisihnya terhadap jumlah manifes.
    """
    jumlah = 0
    for perintah in self.manifes:
      try:
        self.aktifkan(perintah)
        jumlah += 1
      except PluginGagal:
        pass
    return jumlah

  def jalankan(self, perintah: str, argumen: list[str]) -> str:
    """Melayani satu perintah dari awal sampai teks siap tampil.

    Perintah yang tidak dikenali maupun plugin yang gagal sama-sama dijawab
    dengan teks, bukan dengan galat yang naik ke pemanggil. Pilihan itu yang
    membuat satu plugin rusak tidak menjatuhkan aplikasi. Mengembalikan str,
    baik hasil pluginnya maupun pesan penolakannya.
    """
    if perintah not in self.manifes:
      return f"Perintah {perintah} tidak dikenali"
    try:
      plugin = self.aktifkan(perintah)
      return plugin.jalankan(argumen)
    except PluginGagal as kesalahan:
      return f"Dilewati: {kesalahan}"


def rakit_inti() -> Inti:
  """Merangkai inti pada satu tempat, agar skrip lain tidak mengulanginya.

  Skrip pengukuran dan skrip pengujian memakai fungsi yang sama, sehingga
  susunan yang diukur persis sama dengan yang dijalankan. Mengembalikan objek
  Inti yang manifesnya sudah terbaca dan siap menerima perintah.
  """
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
    print(f"Plugin yang sudah aktif: {len(inti.plugin_aktif)}")
    # Keluarannya: Plugin yang sudah aktif: 0
  else:
    print(inti.jalankan(sys.argv[1], sys.argv[2:]))
