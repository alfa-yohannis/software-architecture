"""Kontrak yang wajib dipenuhi setiap plugin, beserta bentuk manifesnya.

Kontrak inilah yang disebut extension point pada Eclipse dan contribution point
pada Visual Studio Code. Inti menuliskannya, plugin yang mengisinya, dan inti
tidak pernah menyebut nama satu plugin pun.

Manifes disimpan sebagai berkas JSON terpisah agar inti dapat membaca daftar
perintah tanpa mengimpor modul pluginnya. Pemisahan itu yang memungkinkan
aktivasi lambat.

Cara menjalankan: berkas ini diimpor, bukan dijalankan langsung.
"""

from typing import Protocol

# Kunci yang wajib ada pada setiap berkas manifes.
KUNCI_MANIFES = ("nama", "perintah", "keterangan", "modul")


class Perintah(Protocol):
  """Satu perintah yang disumbangkan sebuah plugin kepada inti.

  Plugin cukup menyediakan fungsi dengan tanda tangan ini. Inti memanggilnya
  lewat nama perintah yang tercantum di manifes, bukan lewat nama modulnya.
  """

  def __call__(self, argumen: list[str]) -> str:
    """Menjalankan perintah lalu mengembalikan teks yang siap ditampilkan."""
