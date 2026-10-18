"""Perkakas sebaran yang dipakai bersama oleh seluruh skrip pengukuran bab ini.

Rata-rata sengaja tidak disediakan. Yang dilaporkan bab ini adalah median,
persentil ke-95, dan nilai terbesar, sebab gejala antrean dan penghitungan
ulang yang panjang hanya terlihat pada ekor sebarannya.

Cara menjalankan: python sebaran.py
"""

import statistics

PERSENTIL_EKOR = 95


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
    """Mengembalikan float berisi selisih nilai terbesar dan terkecil.

    Angka inilah yang dibandingkan dengan selisih antar versi. Selisih yang
    lebih kecil daripada rentang di dalam satu versi belum dapat disebut ada.
    """
    return self.nilai[-1] - self.nilai[0]

  def baris(self, nama: str, lebar: int = 26) -> str:
    """Menyusun satu baris laporan berisi ketiga angka utama.

    Bentuk barisnya disamakan dengan istilah pada naskah bab, sebab langkah
    latihan menyuruh mahasiswa menyalin baris ini apa adanya. Mengembalikan str
    yang sudah siap dicetak.
    """
    return (f"{nama:<{lebar}}: median {self.median():8.4f} ms"
            f"  p95 {self.persentil():8.4f} ms"
            f"  terbesar {self.terbesar():8.4f} ms")


if __name__ == "__main__":
  contoh = Sebaran([1.0, 2.0, 3.0, 4.0, 100.0])
  print(contoh.baris("Contoh lima nilai"))
  # Keluarannya: Contoh lima nilai         : median   3.0000 ms  p95 100.0000 ms
  #   terbesar 100.0000 ms
  print(f"Rentang: {contoh.rentang():.4f} ms")
  # Keluarannya: Rentang: 99.0000 ms
