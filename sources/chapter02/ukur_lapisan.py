"""Mengukur selisih waktu jalur tertutup dan jalur terbuka pada kurs jual.

Kurs jual dipilih karena di situlah kedua jalur benar-benar berbeda. Jalur
tertutup menjalankan pemeriksaan autentikasi dan otorisasi yang dituntut
lapisan bisnis, sedangkan jalur terbuka melewatinya.

Satu kali pengukuran tidak cukup untuk menyimpulkan apa pun, sebab selisih
antar kedua jalur sangat kecil. Skrip ini menjalankan seratus putaran. Setiap
putaran mengukur kedua jalur, lalu mencatat jalur mana yang lebih cepat pada
putaran tersebut. Bila kedua jalur menang dalam jumlah yang hampir seimbang,
selisihnya tenggelam oleh ragam pengukuran.

Pengukuran bersifat mengamati, tidak membebani sistem milik pihak lain.

Cara menjalankan: python ukur_lapisan.py
"""

import statistics
import time

import aplikasi_terbuka
import aplikasi_tertutup
import basis_data

JUMLAH_PUTARAN = 100
PANGGILAN_PER_PUTARAN = 200
MILIDETIK = 1000.0
TOKEN_STAF = "token-andi"


def ukur_sekali(fungsi, panggilan):
  """Menjalankan sebuah fungsi berulang kali lalu mengembalikan waktu mediannya.

  Median dipakai, bukan rata-rata, agar satu panggilan yang tersendat tidak
  menggeser hasil seluruh putaran.
  """
  waktu = []
  for _ in range(panggilan):
    mulai = time.perf_counter()
    fungsi()
    waktu.append((time.perf_counter() - mulai) * MILIDETIK)
  return statistics.median(waktu)


def jalankan_putaran(jumlah_putaran):
  """Menjalankan kedua jalur bergantian sebanyak jumlah putaran yang diminta.

  Kedua jalur diukur di dalam putaran yang sama agar keduanya menghadapi
  keadaan mesin yang serupa.
  """
  tertutup, terbuka = [], []
  for _ in range(jumlah_putaran):
    jalur_tertutup = lambda: aplikasi_tertutup.tampilkan_kurs_jual(TOKEN_STAF)
    tertutup.append(ukur_sekali(jalur_tertutup, PANGGILAN_PER_PUTARAN))
    terbuka.append(ukur_sekali(aplikasi_terbuka.tampilkan_kurs_jual,
                               PANGGILAN_PER_PUTARAN))
  return tertutup, terbuka


def laporkan(tertutup, terbuka):
  """Mencetak ringkasan seluruh putaran beserta jumlah kemenangan tiap jalur."""
  menang_terbuka = sum(1 for a, b in zip(tertutup, terbuka) if b < a)
  ragam_tertutup = max(tertutup) - min(tertutup)
  ragam_terbuka = max(terbuka) - min(terbuka)
  selisih_median = statistics.median(terbuka) - statistics.median(tertutup)

  print(f"Putaran                    : {len(tertutup)}")
  print(f"Median jalur tertutup      : {statistics.median(tertutup):.4f} ms")
  print(f"Median jalur terbuka       : {statistics.median(terbuka):.4f} ms")
  print(f"Selisih median             : {selisih_median:+.4f} ms")
  print(f"Ragam dalam jalur tertutup : {ragam_tertutup:.4f} ms")
  print(f"Ragam dalam jalur terbuka  : {ragam_terbuka:.4f} ms")
  print(f"Putaran dimenangkan terbuka: {menang_terbuka} dari {len(tertutup)}")


if __name__ == "__main__":
  basis_data.siapkan_basis_data()
  laporkan(*jalankan_putaran(JUMLAH_PUTARAN))
  # Keluarannya: Putaran dimenangkan terbuka: 91 dari 100
