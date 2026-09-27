"""Contract yang wajib dipenuhi setiap plugin, beserta bentuk manifest-nya.

Contract inilah yang disebut extension point pada Eclipse dan contribution point
pada Visual Studio Code. Core menuliskannya, plugin yang memenuhinya, dan core
tidak pernah menyebut nama satu plugin pun.

Manifest disimpan sebagai file JSON terpisah agar core dapat membaca daftar
perintah tanpa mengimpor modul pluginnya. Pemisahan itu yang memungkinkan
lazy activation. Isi manifest menunjuk modul beserta nama kelasnya, sama seperti
kunci mainclass pada plugin.properties di contoh Java.

Cara menjalankan: file ini diimpor, bukan dijalankan langsung.
"""

from typing import Protocol

# Kunci yang wajib ada pada setiap file manifest.
KUNCI_MANIFES = ("nama", "perintah", "keterangan", "modul", "kelas")


class Plugin(Protocol):
  """Satu kemampuan yang disumbangkan sebuah plugin kepada core.

  Konstruktornya menerima core, sehingga plugin dapat memanggil kemampuan yang
  disediakan core maupun kemampuan plugin lain. Core sendiri tidak pernah
  menyebut nama kelas ini, sebab nama itu dibaca dari manifest.
  """

  def __init__(self, inti: object) -> None:
    """Menerima core sebagai satu-satunya ketergantungan sebuah plugin."""

  def jalankan(self, argumen: list[str]) -> str:
    """Menjalankan kemampuannya lalu mengembalikan teks siap tampil."""
