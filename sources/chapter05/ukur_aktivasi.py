"""Mengukur activation cost, yaitu selisih startup time kedua cara aktivasi.

Lazy activation hanya membaca manifest, sedangkan eager activation mengimpor
seluruh modul plugin sekaligus. Visual Studio Code memilih cara pertama, dan
bab ini mengukur selisihnya pada aplikasi sekecil apa pun.

Pengukuran diulang seratus putaran, sebab satu putaran tidak cukup untuk
menyimpulkan apa pun. Import cache Python dibersihkan pada setiap putaran, agar
kedua jalur menghadapi keadaan yang sama.

Setiap panggilan ditulis satu per satu, bukan disarangkan menjadi a(b(c())),
agar nilai antaranya terlihat saat latihan.

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
  """Pengukur startup time kedua jalur aktivasi pada core yang sama."""

  def __init__(self, jumlah_putaran: int = JUMLAH_PUTARAN) -> None:
    """Menyimpan jumlah putaran beserta daftar modul yang akan dibersihkan.

    Daftar modulnya dibiarkan kosong lebih dahulu, sebab isinya baru diketahui
    sesudah manifest dibaca.
    """
    self.jumlah_putaran = jumlah_putaran
    self.nama_modul = []

  def kumpulkan_nama_modul(self):
    """Mencatat nama modul setiap plugin, dipakai membersihkan import cache.

    Mengembalikan list berisi nama modul, misalnya plugins.plugin_kurs.
    """
    inti = modul_inti.rakit_inti()
    self.nama_modul = []
    for manifes in inti.manifes.values():
      self.nama_modul.append(manifes["modul"])
    return self.nama_modul

  def bersihkan_cache(self):
    """Mengeluarkan modul plugin dari import cache Python.

    Tanpa langkah ini, putaran kedua dan seterusnya hanya membaca cache,
    sehingga eager activation terlihat jauh lebih murah daripada sebenarnya.
    Tidak mengembalikan apa pun.
    """
    for nama in self.nama_modul:
      sys.modules.pop(nama, None)

  def ukur_lazy(self):
    """Mengukur waktu membaca manifest saja, tanpa satu pun impor.

    Mengembalikan float berisi lama penjalanan dalam milidetik.
    """
    self.bersihkan_cache()
    mulai = time.perf_counter()
    modul_inti.rakit_inti()
    selesai = time.perf_counter()
    return (selesai - mulai) * MILIDETIK

  def ukur_eager(self):
    """Mengukur waktu membaca manifest lalu mengaktifkan seluruh pluginnya.

    Mengembalikan float berisi lama penjalanan dalam milidetik.
    """
    self.bersihkan_cache()
    mulai = time.perf_counter()
    inti = modul_inti.rakit_inti()
    inti.aktifkan_semua()
    selesai = time.perf_counter()
    return (selesai - mulai) * MILIDETIK

  def laporkan_kemajuan(self, nomor, lazy, eager, mulai):
    """Mencetak satu baris kemajuan beserta perkiraan sisa waktunya.

    Tidak mengembalikan apa pun, sebab barisnya hanya menemani penantian.
    """
    sekarang = time.perf_counter()
    lewat = sekarang - mulai
    sisa = lewat / nomor * (self.jumlah_putaran - nomor)
    median_lazy = statistics.median(lazy)
    median_eager = statistics.median(eager)
    print(f"  putaran {nomor:3d}/{self.jumlah_putaran}"
          f"  lazy {median_lazy:.4f} ms"
          f"  eager {median_eager:.4f} ms"
          f"  sisa sekitar {sisa:3.0f} detik", flush=True)

  def jalankan_putaran(self):
    """Menjalankan kedua jalur bergantian sebanyak putaran yang diminta.

    Mengembalikan dua list berisi lama penjalanan tiap putaran, satu untuk
    lazy activation dan satu untuk eager activation.
    """
    lazy, eager = [], []
    mulai = time.perf_counter()
    print(f"Menjalankan {self.jumlah_putaran} putaran untuk kedua jalur.",
          flush=True)
    for nomor in range(1, self.jumlah_putaran + 1):
      lama_lazy = self.ukur_lazy()
      lazy.append(lama_lazy)
      lama_eager = self.ukur_eager()
      eager.append(lama_eager)
      if nomor % PUTARAN_PER_LAPORAN == 0:
        self.laporkan_kemajuan(nomor, lazy, eager, mulai)
    selesai = time.perf_counter()
    lama_seluruhnya = selesai - mulai
    print(f"Selesai dalam {lama_seluruhnya:.0f} detik.\n")
    return lazy, eager

  def cetak_ringkasan(self, lazy, eager):
    """Mencetak median, range, dan pencacahan kemenangan kedua jalur.

    Tidak mengembalikan apa pun, sebab angka inilah yang dicatat mahasiswa.
    """
    median_lazy = statistics.median(lazy)
    median_eager = statistics.median(eager)
    selisih = median_eager - median_lazy
    range_lazy = max(lazy) - min(lazy)
    range_eager = max(eager) - min(eager)
    lipat_lambat = median_eager / median_lazy
    lipat_range = range_lazy / selisih if selisih else 0.0
    menang = 0
    for lama_lazy, lama_eager in zip(lazy, eager):
      if lama_lazy < lama_eager:
        menang += 1

    print(f"Putaran                      : {self.jumlah_putaran}")
    print(f"Median lazy activation       : {median_lazy:.4f} ms")
    print(f"Median eager activation      : {median_eager:.4f} ms")
    print(f"Selisih median antar jalur   : {selisih:.4f} ms")
    print(f"Eager activation lebih lambat: {lipat_lambat:.1f} kali")
    print(f"Range dalam jalur lazy       : {range_lazy:.4f} ms")
    print(f"Range dalam jalur eager      : {range_eager:.4f} ms")
    print(f"Range dibagi selisih         : {lipat_range:.1f} kali (lazy)")
    print(f"Putaran lazy lebih cepat     : {menang} dari {self.jumlah_putaran}")


if __name__ == "__main__":
  pembanding = PembandingAktivasi()
  pembanding.kumpulkan_nama_modul()
  hasil_lazy, hasil_eager = pembanding.jalankan_putaran()
  pembanding.cetak_ringkasan(hasil_lazy, hasil_eager)
  # Keluarannya: Putaran lazy lebih cepat     : 100 dari 100
