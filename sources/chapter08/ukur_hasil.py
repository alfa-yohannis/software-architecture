"""Membandingkan hasil kedua versi aplikasi ketika processing unit ditambah.

Beban yang sama dijalankan dengan satu, dua, empat, lalu delapan unit, sekali
memakai versi basis data dan sekali memakai versi ruang. Yang dilaporkan bukan
hanya rata-rata, melainkan median, persentil ke-95, dan nilai terbesar, sebab
gejala antrean hanya kelihatan pada ekor sebarannya.

Setiap susunan diulang beberapa putaran, lalu hasil per detiknya diambil
mediannya. Latensi seluruh putaran digabung, sehingga sebarannya dihitung dari
ribuan tugas, bukan dari satu tugas yang kebetulan terpilih.

Susunan dijalankan berselang-seling, yaitu seluruh susunan dicoba sekali lebih
dahulu sebelum putaran berikutnya dimulai. Bila seluruh putaran satu susunan
dijalankan berurutan, satu kesibukan sesaat di luar percobaan akan menimpa satu
susunan saja, lalu terbaca seolah-olah susunan itu yang buruk.

Cara menjalankan: python ukur_hasil.py
"""

import statistics

import domain
import unit

JUMLAH_UNIT = (1, 2, 4, 8)
PUTARAN = 5
# Beban pemanasan sebelum pengukuran dimulai. Putaran pertama selalu lebih
# lambat sebab berkas basis data dan modul Python belum berada di cache sistem.
TUGAS_PEMANASAN = 100
LEBAR_KOLOM = (6, 13, 13, 17, 12, 16, 14)
VERSI = (
  ("basis data", unit.jalankan_versi_basis_data),
  ("ruang", unit.jalankan_versi_ruang),
)


def persentil(daftar_terurut: list[float], bagian: float) -> float:
  """Mengambil nilai pada persentil tertentu dari daftar yang sudah terurut.

  Cara terdekat dipakai, bukan interpolasi, sebab yang dicari adalah satu tugas
  nyata yang benar-benar selambat itu. Mengembalikan float berisi latensi dalam
  milidetik.
  """
  if not daftar_terurut:
    return 0.0
  letak = min(int(bagian * len(daftar_terurut)), len(daftar_terurut) - 1)
  return daftar_terurut[letak]


def kumpulkan_seluruh_putaran() -> dict:
  """Menjalankan seluruh susunan sebanyak PUTARAN kali secara berselang-seling.

  Urutan luarnya putaran dan urutan dalamnya susunan, sehingga kesibukan di luar
  percobaan tersebar merata ke semua susunan. Mengembalikan dict dengan pasangan
  nama versi dan jumlah unit sebagai kunci, berisi daftar hasil per detik dan
  daftar latensi mentah.
  """
  kumpulan = {(nama, jumlah): {"hasil": [], "latensi": []}
              for nama, _ in VERSI for jumlah in JUMLAH_UNIT}
  for putaran in range(PUTARAN):
    print(f"  putaran {putaran + 1} dari {PUTARAN}")
    for nama_versi, fungsi in VERSI:
      for jumlah_unit in JUMLAH_UNIT:
        ringkasan = fungsi(jumlah_unit)
        catatan = kumpulan[(nama_versi, jumlah_unit)]
        catatan["hasil"].append(ringkasan["tugas_selesai"] / ringkasan["detik"])
        catatan["latensi"].extend(ringkasan["latensi"])
  return kumpulan


def rangkum_satu_susunan(catatan: dict) -> dict:
  """Merangkum seluruh putaran satu susunan menjadi satu baris laporan.

  Hasil per detik diambil mediannya antar putaran, sedangkan latensi digabung
  dari seluruh putaran. Mengembalikan dict berisi tugas per detik, transaksi per
  detik, median, persentil ke-95, dan latensi terbesar.
  """
  latensi = sorted(catatan["latensi"])
  tugas_per_detik = statistics.median(catatan["hasil"])
  return {
    "tugas_per_detik": tugas_per_detik,
    "transaksi_per_detik": tugas_per_detik * domain.TRANSAKSI_PER_TUGAS,
    "median": statistics.median(latensi),
    "persentil95": persentil(latensi, 0.95),
    "terbesar": max(latensi),
    "contoh": len(latensi),
  }


def baris_tabel(kolom: tuple) -> str:
  """Menyusun satu baris laporan dengan lebar kolom yang tetap.

  Lebar yang tetap membuat angka pada kolom yang sama mudah dibandingkan dengan
  mata. Mengembalikan str berisi satu baris siap cetak.
  """
  return "".join(f"{str(isi):>{lebar}}" for isi, lebar in zip(kolom, LEBAR_KOLOM))


def jalankan_pengukuran() -> dict:
  """Menjalankan seluruh susunan lalu mencetak laporannya baris demi baris.

  Mengembalikan dict berpasangan nama versi dan jumlah unit sebagai kunci, berisi
  ringkasan setiap susunan.
  """
  print(f"Beban          : {unit.JUMLAH_TUGAS} tugas, "
        f"{domain.TRANSAKSI_PER_TUGAS} transaksi per tugas")
  print(f"Putaran        : {PUTARAN} kali tiap susunan, berselang-seling")
  kumpulan = kumpulkan_seluruh_putaran()
  print()
  print(baris_tabel(("Unit", "Versi", "Tugas/detik", "Transaksi/detik",
                     "Median ms", "Persentil-95 ms", "Terbesar ms")))
  seluruh = {}
  for nama_versi, _ in VERSI:
    for jumlah_unit in JUMLAH_UNIT:
      hasil = rangkum_satu_susunan(kumpulan[(nama_versi, jumlah_unit)])
      seluruh[(nama_versi, jumlah_unit)] = hasil
      print(baris_tabel((
        jumlah_unit, nama_versi,
        f"{hasil['tugas_per_detik']:.1f}",
        f"{hasil['transaksi_per_detik']:,.0f}",
        f"{hasil['median']:.3f}",
        f"{hasil['persentil95']:.3f}",
        f"{hasil['terbesar']:.3f}")))
  return seluruh


if __name__ == "__main__":
  unit.jalankan_versi_ruang(2, TUGAS_PEMANASAN)
  laporan = jalankan_pengukuran()
  print()
  for jumlah in JUMLAH_UNIT:
    pembilang = laporan[("ruang", jumlah)]["tugas_per_detik"]
    penyebut = laporan[("basis data", jumlah)]["tugas_per_detik"]
    print(f"Ruang berbanding basis data pada {jumlah} unit : "
          f"{pembilang / penyebut:.1f} kali")
