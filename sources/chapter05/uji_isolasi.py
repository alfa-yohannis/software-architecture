"""Membandingkan nasib aplikasi ketika satu plugin rusak, dengan dan tanpa
pembungkus galat.

Plugin rusak sengaja gagal saat diimpor. Pada jalur berpelindung, inti mencatat
galatnya lalu melanjutkan. Pada jalur tanpa pelindung, galat yang sama
menghentikan seluruh proses, dan itulah yang dibuktikan angka pada latihan.

Cara menjalankan: python uji_isolasi.py
"""

import importlib

import inti as modul_inti

PERINTAH_UJI = ["konversi", "kurs", "riwayat", "rusak"]
ARGUMEN_UJI = {"konversi": ["USD", "IDR", "100"]}


def jalur_berpelindung():
  """Menjalankan seluruh perintah lewat inti, yang membungkus setiap galat."""
  inti = modul_inti.rakit_inti()
  berhasil, gagal = 0, 0
  for perintah in PERINTAH_UJI:
    hasil = inti.jalankan(perintah, ARGUMEN_UJI.get(perintah, []))
    if hasil.startswith("Dilewati:"):
      gagal += 1
    else:
      berhasil += 1
  return berhasil, gagal


def jalur_tanpa_pelindung():
  """Mengimpor setiap modul plugin langsung, tanpa membungkus galatnya.

  Pemanggilan dihentikan pada kegagalan pertama, persis seperti aplikasi yang
  mengaktifkan seluruh plugin di awal tanpa penjagaan.
  """
  inti = modul_inti.rakit_inti()
  berhasil = 0
  for perintah in PERINTAH_UJI:
    modul = inti.manifes[perintah]["modul"]
    try:
      importlib.import_module(modul)
    except Exception as kesalahan:
      return berhasil, f"{modul}: {kesalahan}"
    berhasil += 1
  return berhasil, None


if __name__ == "__main__":
  berhasil, gagal = jalur_berpelindung()
  print(f"Dengan pelindung  : {berhasil} perintah jalan, {gagal} dilewati")
  # Keluarannya: Dengan pelindung  : 3 perintah jalan, 1 dilewati
  sampai, penyebab = jalur_tanpa_pelindung()
  print(f"Tanpa pelindung   : {sampai} modul terimpor, lalu berhenti")
  # Keluarannya: Tanpa pelindung   : 3 modul terimpor, lalu berhenti
  print(f"Penyebab berhenti : {penyebab}")
