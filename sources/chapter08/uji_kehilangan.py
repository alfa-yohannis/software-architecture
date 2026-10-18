"""Menghitung transaksi yang lenyap ketika satu processing unit mati mendadak.

Beban yang sama dijalankan dua kali, sekali memakai versi basis data dan sekali
memakai versi ruang. Di tengah jalan satu unit dimatikan dengan SIGKILL, tanpa
kesempatan menyelamatkan apa pun. Sesudah unit yang tersisa menghabiskan tugas,
baris pada tabel hasil dihitung, lalu dibandingkan dengan jumlah tugas yang
dibagikan.

Versi basis data kehilangan paling banyak satu tugas, sebab setiap tugas sudah
di-commit sebelum tugas berikutnya dimulai. Versi ruang kehilangan seisi
penyangga unit itu, sebab hasilnya belum sempat dikirim ke ruang. Selisih itulah
harga yang dibayar oleh susunan berbasis ruang.

Cara menjalankan: python uji_kehilangan.py
"""

import statistics

import domain
import unit

PENGULANGAN = 5
UNIT_DIPAKAI = 4
# Beban dibuat lebih ringan daripada beban pengukuran hasil, sebab yang dicari
# di sini bukan kecepatan melainkan jumlah tugas yang lenyap.
TUGAS_DIPAKAI = 600
# Bagian beban yang sudah dibagikan ketika satu unit dimatikan. Titik matinya
# diikat pada kemajuan beban, bukan pada jam dinding, sehingga percobaan ini
# jatuh pada tempat yang sama di mesin cepat maupun mesin lambat.
BAGIAN_MEMATIKAN = 0.5
LEBAR_KOLOM = (10, 26, 26)
VERSI = (
  ("basis data", unit.jalankan_versi_basis_data),
  ("ruang", unit.jalankan_versi_ruang),
)


def coba_satu_putaran(fungsi) -> dict:
  """Menjalankan satu beban penuh sambil mematikan satu unit di tengah jalan.

  Mengembalikan dict berisi tugas tersimpan, tugas hilang, dan transaksi yang
  ikut hilang bersamanya.
  """
  ringkasan = fungsi(UNIT_DIPAKAI, TUGAS_DIPAKAI,
                     bagian_mematikan=BAGIAN_MEMATIKAN)
  return {
    "tugas_tersimpan": ringkasan["tugas_tersimpan"],
    "tugas_hilang": ringkasan["tugas_hilang"],
    "transaksi_hilang": ringkasan["tugas_hilang"] * domain.TRANSAKSI_PER_TUGAS,
  }


def baris_tabel(kolom: tuple) -> str:
  """Menyusun satu baris laporan dengan lebar kolom yang tetap.

  Mengembalikan str berisi satu baris siap cetak.
  """
  return "".join(f"{str(isi):>{lebar}}" for isi, lebar in zip(kolom, LEBAR_KOLOM))


def jalankan_percobaan() -> dict:
  """Mengulang percobaan mematikan unit beberapa kali untuk kedua versi.

  Satu putaran tidak cukup, sebab yang hilang bergantung pada seberapa penuh
  penyangga unit ketika ia mati. Mengembalikan dict berisi daftar tugas hilang
  per versi.
  """
  hasil = {nama: [] for nama, _ in VERSI}
  for nama_versi, fungsi in VERSI:
    for _ in range(PENGULANGAN):
      hasil[nama_versi].append(coba_satu_putaran(fungsi)["tugas_hilang"])
  return hasil


if __name__ == "__main__":
  print(f"Beban          : {TUGAS_DIPAKAI} tugas, "
        f"{domain.TRANSAKSI_PER_TUGAS} transaksi per tugas")
  print(f"Processing unit: {UNIT_DIPAKAI}, satu dimatikan pada "
        f"{BAGIAN_MEMATIKAN:.0%} beban")
  print(f"Penyangga unit : {unit.UKURAN_KELOMPOK} hasil sebelum dikirim")
  print()
  laporan = jalankan_percobaan()
  print(baris_tabel(("Putaran", "Hilang, versi basis data",
                     "Hilang, versi ruang")))
  for nomor in range(PENGULANGAN):
    print(baris_tabel((nomor + 1, laporan["basis data"][nomor],
                       laporan["ruang"][nomor])))
  print()
  for nama in ("basis data", "ruang"):
    daftar = laporan[nama]
    tengah = statistics.median(daftar)
    print(f"Median tugas hilang, versi {nama:<11}: {tengah:.0f} tugas "
          f"({tengah * domain.TRANSAKSI_PER_TUGAS:,.0f} transaksi)")
    print(f"Range tugas hilang, versi {nama:<12}: "
          f"{min(daftar)} sampai {max(daftar)} tugas")
