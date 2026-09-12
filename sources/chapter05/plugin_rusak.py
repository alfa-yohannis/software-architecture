"""Plugin yang sengaja gagal saat diimpor, dipakai pada Latihan 2.

Galatnya dibuat terjadi pada tingkat modul, sehingga kegagalannya muncul saat
impor, bukan saat fungsinya dipanggil. Kegagalan seperti inilah yang paling
berbahaya, sebab pada aktivasi awal satu berkas rusak dapat menghentikan
seluruh aplikasi.

Cara menjalankan: python inti.py rusak
"""

import domain

# Baris berikut sengaja dibiarkan salah. Pasangan mata uang ini tidak ada di
# dalam tabel, sehingga pembacaannya gagal saat modul diimpor.
KURS_TIDAK_ADA = domain.KURS[("JPY", "IDR")]


def jalankan(argumen):
  """Tidak pernah tercapai, sebab modulnya gagal lebih dahulu."""
  return "Plugin ini seharusnya tidak pernah berjalan"
