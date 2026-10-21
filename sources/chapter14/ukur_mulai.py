"""Mengukur latensi mulai dingin dan mulai hangat secara terpisah.

Setiap fungsi dipanggil dua ratus kali. Sebelum setiap pemanggilan kelima,
penjalan sengaja didiamkan melewati batas diamnya, sehingga contoh fungsinya
dilepas dan pemanggilan berikutnya benar-benar membayar fase Init. Sisanya
jatuh pada contoh yang masih hangat.

Batas diamnya dipendekkan menjadi dua puluh milidetik agar pengukuran selesai
dalam hitungan detik. Perilaku yang diukur tetap sama dengan perilaku penjalan
pada pemakaian biasa, yaitu contoh yang diam terlalu lama akan dilepas.

Dua fungsi diukur berdampingan. Fungsi kurs mewakili persiapan ringan,
sedangkan fungsi pajak mewakili persiapan berat berupa tabel dua ratus ribu
baris. Perbandingan keduanya dipakai pada Latihan 1 dan Latihan 2.

Cara menjalankan: python ukur_mulai.py
"""

import math
import statistics
import time

import penjalan as modul_penjalan

JUMLAH_PANGGILAN = 200
# Satu dari lima pemanggilan didahului diam, sehingga sekitar dua puluh persen
# pemanggilan kebagian mulai dingin.
SETIAP_BERAPA_DINGIN = 5
BATAS_DIAM_UKUR = 0.02
DIAM_PAKSA_DETIK = 0.03
PUTARAN_PER_LAPORAN = 50
PERSENTIL = 95

MUATAN = {
  "kurs": {"asal": "USD", "tujuan": "IDR", "nominal": 100.0},
  "pajak": {"penghasilan": 120_000_000.0},
}
FUNGSI_DIUKUR = ("kurs", "pajak")


def persentil(nilai: list[float], bagian: int = PERSENTIL) -> float:
  """Mengembalikan float nilai pada persentil yang diminta, cara peringkat.

  Cara peringkat dipilih, yaitu nilai diurutkan lalu diambil pada peringkat
  hasil pembulatan ke atas. Cara itu tidak mengarang nilai antara dua
  pengamatan, sehingga angka yang dilaporkan benar-benar pernah terukur.
  """
  urut = sorted(nilai)
  peringkat = max(1, math.ceil(bagian / 100 * len(urut)))
  return urut[peringkat - 1]


class PembandingMulai:
  """Pengukur latensi kedua keadaan mulai pada satu penjalan fungsi."""

  def __init__(self, jumlah_panggilan: int = JUMLAH_PANGGILAN) -> None:
    """Menyiapkan penjalan berbatas diam pendek beserta jumlah panggilannya.

    Batas contohnya dibiarkan bawaan, sebab pengukuran ini berjalan satu per
    satu, sehingga tidak pernah ada dua peristiwa yang berebut contoh.
    """
    self.jumlah_panggilan = jumlah_panggilan
    self.penjalan = modul_penjalan.rakit_penjalan(batas_diam=BATAS_DIAM_UKUR)

  def jalankan_satu_fungsi(self, peristiwa: str):
    """Memanggil satu fungsi berulang kali lalu memisahkan kedua kelompoknya.

    Mengembalikan tuple berisi dua list, yaitu lama pemanggilan dingin dan lama
    pemanggilan hangat, keduanya dalam milidetik.
    """
    dingin, hangat = [], []
    self.penjalan.turunkan_ke_nol()
    mulai = time.perf_counter()
    print(f"Mengukur fungsi {peristiwa} sebanyak {self.jumlah_panggilan} "
          f"panggilan.", flush=True)
    for nomor in range(1, self.jumlah_panggilan + 1):
      if nomor % SETIAP_BERAPA_DINGIN == 1:
        time.sleep(DIAM_PAKSA_DETIK)
      hasil = self.penjalan.panggil(peristiwa, MUATAN[peristiwa])
      if hasil.dingin:
        dingin.append(hasil.lama_total())
      else:
        hangat.append(hasil.lama_total())
      if nomor % PUTARAN_PER_LAPORAN == 0:
        print(f"  panggilan {nomor:3d}/{self.jumlah_panggilan}"
              f"  dingin {len(dingin):3d}"
              f"  hangat {len(hangat):3d}"
              f"  lewat {time.perf_counter() - mulai:5.1f} detik", flush=True)
    print(f"Selesai dalam {time.perf_counter() - mulai:.1f} detik.\n")
    return dingin, hangat

  def cetak_ringkasan(self, peristiwa: str, dingin: list, hangat: list) -> None:
    """Mencetak sebaran kedua kelompok beserta takaran ragamnya.

    Yang dicetak bukan hanya median, melainkan juga persentil ke-95 dan nilai
    terbesar, sebab gejala antrean dan gangguan mesin hanya muncul pada nilai
    terbesar. Baris terakhir menakar selisihnya terhadap range kelompok hangat.
    """
    median_dingin = statistics.median(dingin)
    median_hangat = statistics.median(hangat)
    selisih = median_dingin - median_hangat
    range_hangat = max(hangat) - min(hangat)
    range_dingin = max(dingin) - min(dingin)
    melebihi = sum(1 for satu in dingin if satu > max(hangat))
    print(f"Fungsi                       : {peristiwa}")
    print(f"Panggilan                    : {len(dingin) + len(hangat)}")
    print(f"Mulai dingin                 : {len(dingin)}")
    print(f"Mulai hangat                 : {len(hangat)}")
    print(f"Median mulai dingin          : {median_dingin:.4f} ms")
    print(f"Persentil ke-95 mulai dingin : {persentil(dingin):.4f} ms")
    print(f"Terbesar mulai dingin        : {max(dingin):.4f} ms")
    print(f"Median mulai hangat          : {median_hangat:.4f} ms")
    print(f"Persentil ke-95 mulai hangat : {persentil(hangat):.4f} ms")
    print(f"Terbesar mulai hangat        : {max(hangat):.4f} ms")
    print(f"Selisih median               : {selisih:.4f} ms")
    print(f"Mulai dingin lebih lambat    : {median_dingin / median_hangat:.1f} kali")
    print(f"Range dalam kelompok hangat  : {range_hangat:.4f} ms")
    print(f"Range dalam kelompok dingin  : {range_dingin:.4f} ms")
    print(f"Range dibagi selisih         : {range_hangat / selisih:.4f} kali")
    print(f"Dingin melebihi hangat terbesar : {melebihi} dari {len(dingin)}")
    print()


if __name__ == "__main__":
  pembanding = PembandingMulai()
  for nama_fungsi in FUNGSI_DIUKUR:
    hasil_dingin, hasil_hangat = pembanding.jalankan_satu_fungsi(nama_fungsi)
    pembanding.cetak_ringkasan(nama_fungsi, hasil_dingin, hasil_hangat)
  # Keluarannya: Mulai dingin lebih lambat    : 23819.7 kali
