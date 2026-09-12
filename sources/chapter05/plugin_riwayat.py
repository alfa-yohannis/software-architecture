"""Plugin yang mencatat lalu menampilkan riwayat konversi.

Plugin ini ditambahkan belakangan pada Latihan 1, dan penambahannya tidak
menyentuh satu baris pun di inti.py. Riwayatnya disimpan di dalam memori,
sehingga hilang ketika proses berakhir.

Cara menjalankan: python inti.py riwayat
"""

import domain

RIWAYAT = []
CONTOH_AWAL = [("USD", "IDR", 100.0), ("EUR", "IDR", 50.0)]


def catat(kode_asal, kode_tujuan, nominal):
  """Menyimpan satu konversi ke dalam riwayat."""
  RIWAYAT.append((kode_asal, kode_tujuan, nominal))


def jalankan(argumen):
  """Menampilkan riwayat konversi, diisi contoh bila masih kosong."""
  if not RIWAYAT:
    for kode_asal, kode_tujuan, nominal in CONTOH_AWAL:
      catat(kode_asal, kode_tujuan, nominal)
  baris = []
  for kode_asal, kode_tujuan, nominal in RIWAYAT:
    hasil = domain.hitung_konversi(kode_asal, kode_tujuan, nominal)
    baris.append(f"{nominal:,.2f} {kode_asal} -> {hasil:,.2f} {kode_tujuan}")
  return "\n".join(baris)
