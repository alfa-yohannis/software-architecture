"""Plugin yang menghitung konversi satu nominal antar mata uang.

Kelas di dalamnya mengisi kontrak pada kontrak.py. Nama kelas ini tidak pernah
disebut oleh inti.py, sebab inti membacanya dari plugin_konversi.json lalu
mengambilnya lewat getattr.

Cara menjalankan: python inti.py konversi USD IDR 100
"""

import domain

JUMLAH_ARGUMEN = 3


class PluginKonversi:
  """Menyumbangkan perintah konversi kepada inti.

  Rujukan ke inti disimpan walaupun belum dipakai, sebab kontrak menuntut
  seluruh plugin menerima inti lewat konstruktornya. Keseragaman itu yang
  membuat inti dapat membuat objek plugin mana pun dengan cara yang sama.
  """

  def __init__(self, inti) -> None:
    """Menyimpan rujukan inti yang diserahkan saat plugin diaktifkan."""
    self.inti = inti

  def jalankan(self, argumen: list[str]) -> str:
    """Mengubah tiga argumen baris perintah menjadi satu baris hasil.

    Galat domain ditangkap lalu diubah menjadi teks, sebab plugin tidak boleh
    melempar galat mentah kepada inti. Mengembalikan str berisi hasil konversi
    atau pesan galatnya.
    """
    if len(argumen) != JUMLAH_ARGUMEN:
      return "Pemakaian: konversi <asal> <tujuan> <nominal>"
    asal, tujuan, nominal = argumen[0], argumen[1], float(argumen[2])
    try:
      hasil = domain.hitung_konversi(asal, tujuan, nominal)
    except (ValueError, LookupError) as kesalahan:
      return f"Galat: {kesalahan}"
    return f"{nominal:,.2f} {asal} = {hasil:,.2f} {tujuan}"
