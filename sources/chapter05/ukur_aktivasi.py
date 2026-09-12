"""Membandingkan waktu siap antara aktivasi lambat dan aktivasi awal.

Aktivasi lambat hanya membaca manifes, sedangkan aktivasi awal mengimpor
seluruh modul plugin sekaligus. Visual Studio Code memilih cara pertama, dan
bab ini mengukur selisihnya pada aplikasi sekecil apa pun.

Pengukuran diulang seratus putaran, sebab satu putaran tidak cukup untuk
menyimpulkan apa pun. Cache impor Python dibersihkan pada setiap putaran, agar
kedua jalur menghadapi keadaan yang sama.

Cara menjalankan: python ukur_aktivasi.py
"""

import statistics
import sys
import time

import inti as modul_inti

JUMLAH_PUTARAN = 100
MILIDETIK = 1000.0
# Kemajuan dicetak setiap sepuluh putaran, agar jalannya pengukuran terlihat.
PUTARAN_PER_LAPORAN = 10


class PembandingAktivasi:
  """Pengukur waktu siap kedua jalur aktivasi pada inti yang sama."""

  def __init__(self, jumlah_putaran=JUMLAH_PUTARAN):
    self.jumlah_putaran = jumlah_putaran
    self.nama_modul = []

  def kumpulkan_nama_modul(self):
    """Mencatat nama modul setiap plugin, dipakai untuk membersihkan cache."""
    inti = modul_inti.rakit_inti()
    self.nama_modul = [m["modul"] for m in inti.manifes.values()]
    return self.nama_modul

  def bersihkan_cache(self):
    """Mengeluarkan modul plugin dari cache impor Python.

    Tanpa langkah ini, putaran kedua dan seterusnya hanya membaca cache,
    sehingga aktivasi awal terlihat jauh lebih murah daripada sebenarnya.
    """
    for nama in self.nama_modul:
      sys.modules.pop(nama, None)

  def ukur_lambat(self):
    """Mengukur waktu membaca manifes saja, tanpa satu pun impor."""
    self.bersihkan_cache()
    mulai = time.perf_counter()
    modul_inti.rakit_inti()
    return (time.perf_counter() - mulai) * MILIDETIK

  def ukur_awal(self):
    """Mengukur waktu membaca manifes lalu mengimpor seluruh modulnya."""
    self.bersihkan_cache()
    mulai = time.perf_counter()
    inti = modul_inti.rakit_inti()
    inti.aktifkan_semua()
    return (time.perf_counter() - mulai) * MILIDETIK

  def laporkan_kemajuan(self, nomor, lambat, awal, mulai):
    """Mencetak satu baris kemajuan beserta perkiraan sisa waktunya."""
    lewat = time.perf_counter() - mulai
    sisa = lewat / nomor * (self.jumlah_putaran - nomor)
    print(f"  putaran {nomor:3d}/{self.jumlah_putaran}"
          f"  lambat {statistics.median(lambat):.4f} ms"
          f"  awal {statistics.median(awal):.4f} ms"
          f"  sisa sekitar {sisa:3.0f} detik", flush=True)

  def jalankan_putaran(self):
    """Menjalankan kedua jalur bergantian sebanyak putaran yang diminta."""
    lambat, awal = [], []
    mulai = time.perf_counter()
    print(f"Menjalankan {self.jumlah_putaran} putaran untuk kedua jalur.",
          flush=True)
    for nomor in range(1, self.jumlah_putaran + 1):
      lambat.append(self.ukur_lambat())
      awal.append(self.ukur_awal())
      if nomor % PUTARAN_PER_LAPORAN == 0:
        self.laporkan_kemajuan(nomor, lambat, awal, mulai)
    print(f"Selesai dalam {time.perf_counter() - mulai:.0f} detik.\n")
    return lambat, awal

  def cetak_ringkasan(self, lambat, awal):
    """Mencetak median, range, dan pencacahan kemenangan kedua jalur."""
    median_lambat = statistics.median(lambat)
    median_awal = statistics.median(awal)
    selisih = median_awal - median_lambat
    range_lambat = max(lambat) - min(lambat)
    range_awal = max(awal) - min(awal)
    lipat = range_lambat / selisih if selisih else 0.0
    menang = sum(1 for a, b in zip(lambat, awal) if a < b)

    print(f"Putaran                      : {self.jumlah_putaran}")
    print(f"Median aktivasi lambat       : {median_lambat:.4f} ms")
    print(f"Median aktivasi awal         : {median_awal:.4f} ms")
    print(f"Selisih median antar jalur   : {selisih:.4f} ms")
    print(f"Aktivasi awal lebih lambat   : {median_awal / median_lambat:.1f} kali")
    print(f"Range dalam jalur lambat     : {range_lambat:.4f} ms")
    print(f"Range dalam jalur awal       : {range_awal:.4f} ms")
    print(f"Range dibagi selisih         : {lipat:.1f} kali (lambat)")
    print(f"Putaran lambat lebih cepat   : {menang} dari {self.jumlah_putaran}")


if __name__ == "__main__":
  pembanding = PembandingAktivasi()
  pembanding.kumpulkan_nama_modul()
  hasil_lambat, hasil_awal = pembanding.jalankan_putaran()
  pembanding.cetak_ringkasan(hasil_lambat, hasil_awal)
  # Keluarannya: Putaran lambat lebih cepat   : 100 dari 100
