"""Core microkernel yang menemukan, memuat, lalu menjalankan plugin.

Core tidak menyebut nama satu plugin pun. Yang diketahuinya hanya direktori
tempat manifest berada dan bentuk contract pada kontrak.py. Menambah kemampuan
baru karena itu cukup menaruh satu file manifest beserta modulnya, tanpa
menyunting file ini sama sekali.

Pemuatannya memakai importlib dan getattr, yaitu padanan Class.forName beserta
konstruktor hasil refleksi pada contoh Java di java-example. Lazy activation
ditiru dari Visual Studio Code. Manifest dibaca saat mulai, sedangkan modul
pluginnya baru diimpor ketika perintahnya benar-benar dipanggil.

Setiap panggilan ditulis satu per satu, bukan disarangkan menjadi a(b(c())),
agar nilai antaranya terlihat saat latihan.

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


class PluginError(Exception):
  """Ditandai ketika satu plugin gagal dimuat atau gagal dijalankan.

  Error aslinya ditangkap error handler agar core dapat melanjutkan hidup.
  Tanpa error handler itu, satu plugin rusak menghentikan seluruh aplikasi.
  """


class Core:
  """Pendaftar dan penjalan kemampuan yang berasal dari plugin.

  Registry hanya berisi manifest, bukan objek plugin. Objeknya dibuat saat
  perintahnya dipanggil, lalu disimpan agar pemanggilan berikutnya tidak
  mengimpor dan menginstansiasi ulang.
  """

  def __init__(self, direktori: pathlib.Path = DIREKTORI_PLUGIN) -> None:
    """Menyiapkan tiga registry kosong sebelum manifest apa pun dibaca.

    Registry sengaja dipisah menjadi tiga, yaitu manifest yang terbaca, plugin
    yang sudah aktif, dan error pemuatan. Pemisahan itu membuat core dapat
    melaporkan plugin yang gagal tanpa kehilangan yang berhasil.
    """
    self.direktori = direktori
    self.manifes = {}
    self.plugin_aktif = {}
    self.galat_muat = {}

  def temukan(self) -> dict:
    """Membaca seluruh file manifest tanpa mengimpor satu modul pun.

    Manifest yang tidak memuat kunci wajib diabaikan, sebab manifest cacat
    tidak boleh menghentikan pemindaian manifest lainnya. Mengembalikan dict
    berisi manifest yang lolos, dengan nama perintah sebagai kuncinya.
    """
    daftar_file = sorted(self.direktori.glob(POLA_MANIFES))
    for berkas in daftar_file:
      teks = berkas.read_text(encoding="utf-8")
      isi = json.loads(teks)
      lengkap = all(kunci in isi for kunci in kontrak.KUNCI_MANIFES)
      if lengkap:
        self.manifes[isi["perintah"]] = isi
    return self.manifes

  def daftar_perintah(self) -> list[tuple[str, str]]:
    """Menyusun isi registry menjadi daftar yang siap ditampilkan.

    Keterangan diambil dari manifest, bukan dari kode pluginnya, sehingga
    daftar ini dapat dicetak tanpa mengimpor satu modul pun. Mengembalikan list
    berisi pasangan nama perintah dan keterangannya.
    """
    daftar = []
    for manifes in self.manifes.values():
      daftar.append((manifes["perintah"], manifes["keterangan"]))
    return daftar

  def aktifkan(self, perintah: str) -> kontrak.Plugin:
    """Mengimpor modul, mengambil kelasnya, lalu membuat objek pluginnya.

    Kelas diambil lewat getattr, dan objeknya menerima core sebagai argumen
    konstruktor. Langkahnya dilindungi error handler agar plugin rusak tercatat
    sebagai error, bukan menghentikan core. Perilaku itu diukur pada Latihan 2.
    Mengembalikan objek plugin yang memenuhi kontrak.Plugin, dan melempar
    PluginError bila salah satu langkahnya gagal.
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
      raise PluginError(f"{manifes['nama']} gagal dimuat: {kesalahan}")
    self.plugin_aktif[perintah] = plugin
    return plugin

  def aktifkan_semua(self) -> int:
    """Mengaktifkan seluruh plugin sekaligus, seperti eager activation.

    Cara ini dipakai sebagai pembanding pada Latihan 3, sebab inilah yang
    dihindari Visual Studio Code lewat activation event. Mengembalikan int
    berisi jumlah plugin yang berhasil aktif, sehingga yang gagal terlihat dari
    selisihnya terhadap jumlah manifest.
    """
    jumlah = 0
    for perintah in self.manifes:
      try:
        self.aktifkan(perintah)
        jumlah += 1
      except PluginError:
        pass
    return jumlah

  def jalankan(self, perintah: str, argumen: list[str]) -> str:
    """Melayani satu perintah dari awal sampai teks siap tampil.

    Perintah yang tidak dikenali maupun plugin yang gagal sama-sama dijawab
    dengan teks, bukan dengan error yang naik ke pemanggil. Pilihan itu yang
    membuat satu plugin rusak tidak menjatuhkan aplikasi. Mengembalikan str,
    baik hasil pluginnya maupun pesan penolakannya.
    """
    if perintah not in self.manifes:
      return f"Perintah {perintah} tidak dikenali"
    try:
      plugin = self.aktifkan(perintah)
      return plugin.jalankan(argumen)
    except PluginError as kesalahan:
      return f"Dilewati: {kesalahan}"


def rakit_inti() -> Core:
  """Merangkai core pada satu tempat, agar skrip lain tidak mengulanginya.

  Skrip pengukuran dan skrip unit test memakai fungsi yang sama, sehingga
  susunan yang diukur persis sama dengan yang dijalankan. Mengembalikan objek
  Core yang manifestnya sudah terbaca dan siap menerima perintah.
  """
  inti = Core()
  inti.temukan()
  return inti


if __name__ == "__main__":
  inti = rakit_inti()
  jumlah_argumen = len(sys.argv)
  if jumlah_argumen < 2 or sys.argv[1] == "daftar":
    jumlah_manifes = len(inti.manifes)
    print(f"Plugin terpasang: {jumlah_manifes}")
    # Keluarannya: Plugin terpasang: 4
    for nama_perintah, keterangan in inti.daftar_perintah():
      print(f"  {nama_perintah:<10} {keterangan}")
    jumlah_aktif = len(inti.plugin_aktif)
    print(f"Plugin yang sudah aktif: {jumlah_aktif}")
    # Keluarannya: Plugin yang sudah aktif: 0
  else:
    perintah = sys.argv[1]
    argumen = sys.argv[2:]
    hasil = inti.jalankan(perintah, argumen)
    print(hasil)
