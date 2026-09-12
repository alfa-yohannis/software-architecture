"""Plugin yang menghitung konversi satu nominal antar mata uang.

Plugin ini mengisi kontrak pada kontrak.py lewat fungsi jalankan. Nama modul
ini tidak pernah disebut oleh inti.py, sebab inti membacanya dari manifes
plugin_konversi.json.

Cara menjalankan: python inti.py konversi USD IDR 100
"""

import domain

JUMLAH_ARGUMEN = 3


def jalankan(argumen):
  """Mengubah tiga argumen baris perintah menjadi satu baris hasil."""
  if len(argumen) != JUMLAH_ARGUMEN:
    return "Pemakaian: konversi <asal> <tujuan> <nominal>"
  asal, tujuan, nominal = argumen[0], argumen[1], float(argumen[2])
  try:
    hasil = domain.hitung_konversi(asal, tujuan, nominal)
  except (ValueError, LookupError) as kesalahan:
    return f"Galat: {kesalahan}"
  return f"{nominal:,.2f} {asal} = {hasil:,.2f} {tujuan}"
