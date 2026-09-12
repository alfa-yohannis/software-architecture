"""Mengukur selisih waktu jalur closed dan jalur open pada kurs jual.

Kurs jual dipilih karena di situlah kedua jalur benar-benar berbeda. Jalur
closed menjalankan pemeriksaan autentikasi dan otorisasi yang dituntut lapisan
bisnis, sedangkan jalur open melewatinya.

Satu kali pengukuran tidak cukup untuk menyimpulkan apa pun, sebab selisih
antar kedua jalur sangat kecil. Skrip ini menjalankan seratus putaran. Setiap
putaran mengukur kedua jalur, lalu mencatat jalur mana yang lebih cepat pada
putaran tersebut. Bila kedua jalur sama sering tercatat lebih cepat, selisihnya
tenggelam oleh range pengukuran.

Pengukuran bersifat mengamati, tidak membebani sistem milik pihak lain.

Cara menjalankan: python ukur_lapisan.py
"""

import functools
import statistics
import time

import aplikasi_terbuka
import aplikasi_tertutup
from basis_data import BasisDataKurs

JUMLAH_PUTARAN = 100
PANGGILAN_PER_PUTARAN = 200
MILIDETIK = 1000.0
# Kemajuan dicetak setiap sepuluh putaran, sebab seluruh pengukuran memakan
# waktu puluhan detik dan tanpa keluaran apa pun terlihat seperti macet.
PUTARAN_PER_LAPORAN = 10
TOKEN_STAF = "token-andi"


class PengukurJalur:
  """Pembanding waktu dua jalur yang melayani request yang sama.

  Kedua jalur diterima sebagai objek yang dapat dipanggil tanpa argumen,
  sehingga kelas ini tidak perlu tahu lapisan mana saja yang ada di baliknya.
  """

  def __init__(self, jalur_tertutup, jalur_terbuka):
    """Menyimpan kedua jalur yang akan dibandingkan pada setiap putaran."""
    self.jalur_tertutup = jalur_tertutup
    self.jalur_terbuka = jalur_terbuka

  def ukur_sekali(self, jalur, panggilan):
    """Menjalankan satu jalur berulang kali lalu mengembalikan waktu mediannya.

    Median dipakai, bukan rata-rata, agar satu panggilan yang tersendat tidak
    menggeser hasil seluruh putaran.
    """
    waktu = []
    for _ in range(panggilan):
      mulai = time.perf_counter()
      jalur()
      waktu.append((time.perf_counter() - mulai) * MILIDETIK)
    return statistics.median(waktu)

  def laporkan_kemajuan(self, nomor, jumlah_putaran, tertutup, terbuka, mulai):
    """Mencetak satu baris kemajuan beserta perkiraan sisa waktunya.

    Median sementara ikut dicetak agar terlihat bahwa kedua jalur memang
    berdekatan sejak awal, bukan hanya pada hasil akhirnya.
    """
    lewat = time.perf_counter() - mulai
    sisa = lewat / nomor * (jumlah_putaran - nomor)
    print(f"  putaran {nomor:3d}/{jumlah_putaran}"
          f"  closed {statistics.median(tertutup):.4f} ms"
          f"  open {statistics.median(terbuka):.4f} ms"
          f"  sisa sekitar {sisa:3.0f} detik", flush=True)

  def jalankan_putaran(self, jumlah_putaran):
    """Menjalankan kedua jalur bergantian sebanyak putaran yang diminta.

    Kedua jalur diukur di dalam putaran yang sama agar keduanya menghadapi
    keadaan mesin yang serupa.
    """
    tertutup, terbuka = [], []
    mulai = time.perf_counter()
    print(f"Menjalankan {jumlah_putaran} putaran, setiap putaran"
          f" {PANGGILAN_PER_PUTARAN} panggilan untuk masing-masing jalur.",
          flush=True)
    for nomor in range(1, jumlah_putaran + 1):
      tertutup.append(self.ukur_sekali(self.jalur_tertutup,
                                       PANGGILAN_PER_PUTARAN))
      terbuka.append(self.ukur_sekali(self.jalur_terbuka,
                                      PANGGILAN_PER_PUTARAN))
      if nomor % PUTARAN_PER_LAPORAN == 0:
        self.laporkan_kemajuan(nomor, jumlah_putaran, tertutup, terbuka, mulai)
    print(f"Selesai dalam {time.perf_counter() - mulai:.0f} detik.\n")
    return tertutup, terbuka

  def laporkan(self, tertutup, terbuka):
    """Mencetak ringkasan seluruh putaran beserta pembanding range-nya.

    Dua baris terakhir adalah inti laporan. Baris range dibagi selisih
    menyatakan berapa kali range di dalam satu jalur lebih besar daripada
    selisih antar kedua jalur. Baris terakhir menyatakan pada berapa putaran
    jalur open layer tercatat lebih cepat, dan angka lima puluh menjadi
    pembandingnya sebab itulah nilai yang muncul bila kedua jalur sama cepat.
    """
    terbuka_lebih_cepat = sum(1 for a, b in zip(tertutup, terbuka) if b < a)
    range_tertutup = max(tertutup) - min(tertutup)
    range_terbuka = max(terbuka) - min(terbuka)
    median_tertutup = statistics.median(tertutup)
    median_terbuka = statistics.median(terbuka)
    selisih_median = median_terbuka - median_tertutup
    besar_selisih = abs(selisih_median)
    lipat_tertutup = range_tertutup / besar_selisih if besar_selisih else 0.0
    lipat_terbuka = range_terbuka / besar_selisih if besar_selisih else 0.0

    print(f"Putaran                      : {len(tertutup)}")
    print(f"Median jalur closed layer    : {median_tertutup:.4f} ms")
    print(f"Median jalur open layer      : {median_terbuka:.4f} ms")
    print(f"Selisih median antar jalur   : {selisih_median:+.4f} ms")
    print(f"Range dalam jalur closed     : {range_tertutup:.4f} ms")
    print(f"Range dalam jalur open       : {range_terbuka:.4f} ms")
    print(f"Range dibagi selisih         : {lipat_tertutup:.0f} kali (closed),"
          f" {lipat_terbuka:.0f} kali (open)")
    print(f"Putaran open lebih cepat     : {terbuka_lebih_cepat}"
          f" dari {len(tertutup)}, seimbang bila 50")


if __name__ == "__main__":
  print("Menyiapkan basis data dan merangkai kedua jalur.", flush=True)
  BasisDataKurs().siapkan()
  antarmuka_tertutup = aplikasi_tertutup.rakit_antarmuka()
  antarmuka_terbuka = aplikasi_terbuka.rakit_antarmuka()
  pengukur = PengukurJalur(
    functools.partial(antarmuka_tertutup.tampilkan_kurs_jual, TOKEN_STAF),
    antarmuka_terbuka.tampilkan_kurs_jual,
  )
  pengukur.laporkan(*pengukur.jalankan_putaran(JUMLAH_PUTARAN))
  # Keluarannya: Putaran open lebih cepat     : 48 dari 100, seimbang bila 50
