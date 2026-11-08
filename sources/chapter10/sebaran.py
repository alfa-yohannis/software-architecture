"""Perkakas sebaran yang dipakai bersama oleh seluruh skrip pengukuran bab ini.

Rata-rata sengaja tidak disediakan. Yang dilaporkan bab ini adalah median,
persentil ke-95, dan nilai terbesar, sebab gejala antrean dan penghitungan
ulang yang panjang hanya terlihat pada ekor sebarannya.

Cara menjalankan: python sebaran.py
"""

import statistics

PERSENTIL_EKOR = 95
# Lebar kolom tabel sebaran. Tabelnya dibuat sempit agar barisnya muat pada
# listing modul tanpa terpotong.
LEBAR_ANGKA = 10
LEBAR_PERSENTIL = 14


class Sebaran:
  """Ringkasan satu deret hasil pengukuran waktu beserta ekornya."""

  def __init__(self, nilai: list[float]) -> None:
    """Mengurutkan salinan nilainya sekali, agar persentil tidak mengurut ulang.

    Daftar aslinya tidak disentuh, sebab skrip pemanggil masih memakainya untuk
    mencacah putaran yang lebih cepat.
    """
    self.nilai = sorted(nilai)
    self.jumlah = len(self.nilai)

  def median(self) -> float:
    """Mengembalikan float berisi nilai tengah, yaitu wakil keadaan biasa."""
    return statistics.median(self.nilai)

  def persentil(self, bagian: int = PERSENTIL_EKOR) -> float:
    """Menghitung persentil dengan cara memilih nilai terdekat.

    Cara ini dipilih daripada penyisipan, sebab angka yang dilaporkan menjadi
    angka yang benar-benar pernah terukur. Mengembalikan float berisi nilai
    pada kedudukan tersebut.
    """
    kedudukan = min(self.jumlah - 1, int(round(bagian / 100 * self.jumlah)) - 1)
    return self.nilai[max(0, kedudukan)]

  def terbesar(self) -> float:
    """Mengembalikan float berisi nilai terbesar, yaitu putaran paling buruk."""
    return self.nilai[-1]

  def rentang(self) -> float:
    """Mengembalikan float berisi range, yaitu nilai terbesar dikurangi terkecil.

    Angka inilah yang dibandingkan dengan selisih antar versi. Selisih yang
    lebih kecil daripada range di dalam satu versi belum dapat disebut ada.
    """
    return self.nilai[-1] - self.nilai[0]

  def baris(self, nama: str, lebar: int = 26) -> str:
    """Menyusun satu baris tabel berisi ketiga angka utama dalam milidetik.

    Lebar kolomnya mengikuti kepala_tabel, sehingga angkanya selalu lurus di
    bawah judul kolomnya. Langkah latihan menyuruh mahasiswa menyalin baris ini
    apa adanya. Mengembalikan str yang sudah siap dicetak.
    """
    median = self.median()
    persentil = self.persentil()
    terbesar = self.terbesar()
    return (f"{nama:<{lebar}}{median:>{LEBAR_ANGKA}.4f}"
            f"{persentil:>{LEBAR_PERSENTIL}.4f}{terbesar:>{LEBAR_ANGKA}.4f}")


def kepala_tabel(judul: str, lebar: int = 26) -> str:
  """Menyusun baris judul bagi tabel yang barisnya dibuat Sebaran.baris.

  Judul kolomnya memakai istilah yang sama dengan tabel pada naskah bab,
  sehingga baris yang disalin langsung cocok dengan lembar isiannya.
  Mengembalikan str yang sudah siap dicetak.
  """
  return (f"{judul:<{lebar}}{'Median':>{LEBAR_ANGKA}}"
          f"{'Persentil-95':>{LEBAR_PERSENTIL}}{'Terbesar':>{LEBAR_ANGKA}}")


if __name__ == "__main__":
  contoh = Sebaran([1.0, 2.0, 3.0, 4.0, 100.0])
  kepala = kepala_tabel("Dalam milidetik")
  baris_contoh = contoh.baris("Contoh lima nilai")
  range_contoh = contoh.rentang()
  print(kepala)
  print(baris_contoh)
  # Keluarannya: Contoh lima nilai             3.0000      100.0000  100.0000
  print(f"Range: {range_contoh:.4f} ms")
  # Keluarannya: Range: 99.0000 ms
