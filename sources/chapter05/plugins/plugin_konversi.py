"""Plugin yang menghitung konversi satu nominal antar mata uang.

Kelas di dalamnya mengisi contract pada kontrak.py. Nama kelas ini tidak pernah
disebut oleh inti.py, sebab core membacanya dari plugin_konversi.json lalu
mengambilnya lewat getattr.

Cara menjalankan: python inti.py konversi USD IDR 100
"""

import domain

JUMLAH_ARGUMEN = 3


class ConversionPlugin:
  """Menyumbangkan perintah konversi kepada core.

  Rujukan ke core disimpan walaupun belum dipakai, sebab contract menuntut
  seluruh plugin menerima core lewat konstruktornya. Keseragaman itu yang
  membuat core dapat membuat objek plugin mana pun dengan cara yang sama.
  """

  def __init__(self, inti) -> None:
    """Menyimpan rujukan core yang diserahkan saat plugin diaktifkan."""
    self.inti = inti

  def jalankan(self, argumen: list[str]) -> str:
    """Mengubah tiga argumen baris perintah menjadi satu baris hasil.

    Error domain ditangkap lalu diubah menjadi teks, sebab plugin tidak boleh
    melempar error mentah kepada core. Mengembalikan str berisi hasil konversi
    atau pesan galatnya.
    """
    jumlah_argumen = len(argumen)
    if jumlah_argumen != JUMLAH_ARGUMEN:
      return "Pemakaian: konversi <asal> <tujuan> <nominal>"
    asal = argumen[0]
    tujuan = argumen[1]
    nominal = float(argumen[2])
    try:
      hasil = domain.hitung_konversi(asal, tujuan, nominal)
    except (ValueError, LookupError) as kesalahan:
      return f"Error: {kesalahan}"
    return f"{nominal:,.2f} {asal} = {hasil:,.2f} {tujuan}"
