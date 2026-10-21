"""Layanan pembanding yang hidup terus dan siap sekali di awal.

Layanan ini menempuh jalan yang berlawanan dengan penjalan fungsi. Seluruh
modul diimpor dan seluruh objek penangan dibuat satu kali saat mulai, lalu
ditahan di dalam memori selama layanannya hidup. Akibatnya tidak pernah ada
mulai dingin sesudah layanannya siap, dan sebagai gantinya memori tetap
terpakai walaupun tidak ada satu pun permintaan.

Perbedaan penting yang kedua terletak pada cara peristiwa disambungkan.
Layanan ini menyebut nama setiap modul dan setiap kelas fungsinya di dalam
kode, persis seperti daftar jalur pada sebuah layanan web. Penyebutan itulah
yang membuat penambahan satu fungsi baru menuntut penyuntingan berkas ini, dan
skrip ukur_perubahan.py menghitung berapa barisnya.

Cara menjalankan:
  python layanan_hidup.py
  python layanan_hidup.py kurs USD IDR 100
"""

import sys
import time

import penjalan as modul_penjalan
from fungsi import fungsi_kurs
from fungsi import fungsi_pajak
from fungsi import fungsi_pesanan

MILIDETIK = 1000.0
# Memori yang dipesan untuk satu proses layanan. Angkanya menampung ketiga
# penangan sekaligus, sehingga lebih besar daripada memori satu fungsi.
MEMORI_LAYANAN_MB = 512


class LayananHidup:
  """Satu proses yang menahan seluruh penangan selama layanannya hidup."""

  def __init__(self) -> None:
    """Menyiapkan daftar penangan yang masih kosong sebelum layanan dimulai.

    Pengisiannya sengaja dipisah ke siapkan, agar lama penyiapannya dapat
    diukur sebagai langkah tersendiri dan dibandingkan dengan lama fase Init
    pada penjalan fungsi.
    """
    self.penangan = {}
    self.siap_pada = None

  def siapkan(self) -> float:
    """Mengimpor dan membuat seluruh penangan sekaligus, satu kali saja.

    Ketiga nama fungsinya ditulis apa adanya di sini, sebab layanan yang hidup
    terus memang memegang daftar jalurnya sendiri. Mengembalikan float berisi
    lama penyiapan dalam milidetik.
    """
    mulai = time.perf_counter()
    self.penangan["kurs"] = fungsi_kurs.FungsiKurs()
    self.penangan["pajak"] = fungsi_pajak.FungsiPajak()
    self.penangan["pesanan"] = fungsi_pesanan.FungsiPesanan()
    self.siap_pada = time.monotonic()
    return (time.perf_counter() - mulai) * MILIDETIK

  def panggil(self, peristiwa: str, muatan: dict):
    """Melayani satu peristiwa dengan penangan yang sudah siap sejak awal.

    Bentuk kembaliannya sengaja sama dengan kembalian penjalan fungsi, yaitu
    objek HasilPanggilan, agar kedua jalur dapat diukur dengan kode yang sama.
    Lama Init dan lama menunggu selalu nol, sebab penangannya tidak pernah
    dibuat ulang dan tidak pernah dibatasi jumlahnya.
    """
    mulai = time.perf_counter()
    isi = self.penangan[peristiwa].tangani(muatan)
    lama_tangani = (time.perf_counter() - mulai) * MILIDETIK
    return modul_penjalan.HasilPanggilan(peristiwa, isi, False, False, 1,
                                         0.0, 0.0, lama_tangani)

  def jumlah_penangan(self) -> int:
    """Mengembalikan int jumlah penangan yang sedang ditahan di dalam memori.

    Angkanya tidak pernah turun selama layanan hidup, dan perbedaan itulah yang
    diukur skrip ukur_sumber_daya.py terhadap penjalan fungsi yang turun ke nol.
    """
    return len(self.penangan)


def rakit_layanan() -> LayananHidup:
  """Membuat layanan lalu menyiapkannya sekaligus, agar pemakainya ringkas.

  Mengembalikan objek LayananHidup yang seluruh penangannya sudah siap dipakai.
  """
  layanan = LayananHidup()
  layanan.siapkan()
  return layanan


if __name__ == "__main__":
  mesin = LayananHidup()
  lama_siap = mesin.siapkan()
  print(f"Penangan disiapkan : {mesin.jumlah_penangan()}")
  # Keluarannya: Penangan disiapkan : 3
  print(f"Lama penyiapan     : {lama_siap:.3f} ms")
  if len(sys.argv) >= 2:
    hasil = mesin.panggil(
      sys.argv[1], modul_penjalan.muatan_contoh(sys.argv[1], sys.argv[2:]))
    print(f"Lama tangani       : {hasil.lama_tangani:.3f} ms")
    print(hasil.isi)
