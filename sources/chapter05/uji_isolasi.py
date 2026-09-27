"""Mengukur error isolation, yaitu nasib aplikasi ketika satu plugin rusak.

Plugin rusak sengaja gagal saat diimpor. Pada jalur dengan error handler, core
mencatat error-nya lalu melanjutkan. Pada jalur tanpa error handler, error yang
sama
menghentikan seluruh proses, dan itulah yang dibuktikan angka pada latihan.

Setiap panggilan ditulis satu per satu, bukan disarangkan menjadi a(b(c())),
agar nilai antaranya terlihat saat latihan.

Cara menjalankan: python uji_isolasi.py
"""

import importlib

import inti as modul_inti

PERINTAH_UJI = ["konversi", "kurs", "riwayat", "rusak"]
ARGUMEN_UJI = {"konversi": ["USD", "IDR", "100"]}


def jalur_dengan_error_handler():
  """Menjalankan seluruh perintah lewat core, yang menangkap setiap error.

  Mengembalikan dua int, yaitu jumlah perintah yang jalan dan jumlah yang
  dilewati.
  """
  inti = modul_inti.rakit_inti()
  berhasil, gagal = 0, 0
  for perintah in PERINTAH_UJI:
    argumen = ARGUMEN_UJI.get(perintah, [])
    hasil = inti.jalankan(perintah, argumen)
    dilewati = hasil.startswith("Dilewati:")
    if dilewati:
      gagal += 1
    else:
      berhasil += 1
  return berhasil, gagal


def jalur_tanpa_error_handler():
  """Mengaktifkan setiap plugin langsung, tanpa error handler di depannya.

  Pemanggilan dihentikan pada kegagalan pertama, persis seperti aplikasi yang
  memakai eager activation tanpa penjagaan. Mengembalikan jumlah modul yang
  sempat terimpor beserta penyebab berhentinya, atau None bila tidak berhenti.
  """
  inti = modul_inti.rakit_inti()
  berhasil = 0
  for perintah in PERINTAH_UJI:
    manifes = inti.manifes[perintah]
    try:
      modul = importlib.import_module(manifes["modul"])
      kelas = getattr(modul, manifes["kelas"])
      kelas(inti)
    except Exception as kesalahan:
      penyebab = f"{manifes['modul']}: {kesalahan}"
      return berhasil, penyebab
    berhasil += 1
  return berhasil, None


if __name__ == "__main__":
  berhasil, gagal = jalur_dengan_error_handler()
  print(f"Dengan error handler : {berhasil} perintah jalan, {gagal} dilewati")
  # Keluarannya: Dengan error handler : 3 perintah jalan, 1 dilewati
  sampai, penyebab = jalur_tanpa_error_handler()
  print(f"Tanpa error handler  : {sampai} modul terimpor, lalu berhenti")
  # Keluarannya: Tanpa error handler  : 3 modul terimpor, lalu berhenti
  print(f"Penyebab berhenti    : {penyebab}")
