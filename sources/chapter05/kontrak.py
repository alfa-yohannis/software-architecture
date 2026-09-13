"""Kontrak yang wajib dipenuhi setiap plugin, beserta bentuk manifesnya.

Kontrak inilah yang disebut extension point pada Eclipse dan contribution point
pada Visual Studio Code. Inti menuliskannya, plugin yang mengisinya, dan inti
tidak pernah menyebut nama satu plugin pun.

Manifes disimpan sebagai berkas JSON terpisah agar inti dapat membaca daftar
perintah tanpa mengimpor modul pluginnya. Pemisahan itu yang memungkinkan
aktivasi lambat. Isi manifes menunjuk modul beserta nama kelasnya, sama seperti
kunci mainclass pada plugin.properties di contoh Java.

Cara menjalankan: berkas ini diimpor, bukan dijalankan langsung.
"""

from typing import Protocol

# Kunci yang wajib ada pada setiap berkas manifes.
KUNCI_MANIFES = ("nama", "perintah", "keterangan", "modul", "kelas")


class Plugin(Protocol):
  """Satu kemampuan yang disumbangkan sebuah plugin kepada inti.

  Konstruktornya menerima inti, sehingga plugin dapat memanggil kemampuan yang
  disediakan inti maupun kemampuan plugin lain. Inti sendiri tidak pernah
  menyebut nama kelas ini, sebab nama itu dibaca dari manifes.
  """

  def __init__(self, inti: object) -> None:
    """Menerima inti sebagai satu-satunya ketergantungan sebuah plugin."""

  def jalankan(self, argumen: list[str]) -> str:
    """Menjalankan kemampuannya lalu mengembalikan teks siap tampil."""
