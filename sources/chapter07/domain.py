"""Tabel kurs yang menjadi isi jaringan beserta daftar kuncinya.

Domainnya sengaja sama dengan Bab 2 dan Bab 4, yaitu pasangan mata uang.
Karena domainnya tidak berubah, yang tersisa untuk dibandingkan pada bab ini
hanya satu hal, yaitu cara sebuah node menemukan nilai kurs yang tidak
dipegangnya sendiri.

Nilainya diambil apa adanya dari Kurs Transaksi Bank Indonesia tanggal 18
September 2026, yaitu nilai tengah antara kurs jual dan kurs beli. Dua
kejanggalan pada tabel itu dibiarkan. Pertama, JPY dikutip per seratus yen,
sedangkan mata uang lain per satu satuan. Kedua, BND dan SGD bernilai sama
persis, sebab kedua mata uang itu memang dipertukarkan pada nilai satu
berbanding satu.

Cara menjalankan: python domain.py
"""

# Nilai tengah Kurs Transaksi Bank Indonesia, 18 September 2026.
KURS = {
  "AED/IDR": 4833.91,
  "AUD/IDR": 12634.82,
  "BND/IDR": 13915.74,
  "CAD/IDR": 12693.87,
  "CHF/IDR": 21509.68,
  "CNH/IDR": 2646.80,
  "CNY/IDR": 2646.62,
  "DKK/IDR": 2724.80,
  "EUR/IDR": 20368.91,
  "GBP/IDR": 23768.61,
  "HKD/IDR": 2262.86,
  "JPY/IDR": 11403.16,
  "KRW/IDR": 12.83,
  "KWD/IDR": 57761.56,
  "LAK/IDR": 0.79,
  "MYR/IDR": 4331.60,
  "NOK/IDR": 1884.90,
  "NZD/IDR": 10181.37,
  "PGK/IDR": 3995.09,
  "PHP/IDR": 282.97,
  "SAR/IDR": 4725.82,
  "SEK/IDR": 1806.00,
  "SGD/IDR": 13915.74,
  "THB/IDR": 532.41,
  "USD/IDR": 17753.00,
  "VND/IDR": 0.69,
}

TANGGAL_KURS = "18 September 2026"
# Bank Indonesia mengutip yen per seratus satuan, bukan per satu satuan.
KUNCI_PER_SERATUS = "JPY/IDR"


def daftar_kunci() -> list[str]:
  """Mengembalikan seluruh kunci kurs berurut, dipakai sebagai bahan lookup.

  Urutannya dibuat tetap agar dua kali penjalanan skrip pengukuran memakai
  bahan yang sama persis.
  """
  return sorted(KURS)


def nilai_kurs(kunci: str):
  """Mengembalikan nilai kurs sebuah pasangan, atau None bila tidak terdaftar.

  Nilai ini yang dititipkan kepada node pemegangnya saat jaringan disusun.
  """
  return KURS.get(kunci)


def satuan_kunci(kunci: str) -> str:
  """Mengembalikan keterangan satuan sebuah kunci, dipakai saat mencetak.

  Keterangannya dibutuhkan sebab satu baris tabel Bank Indonesia memakai satuan
  yang berbeda dari baris lainnya.
  """
  if kunci == KUNCI_PER_SERATUS:
    return "per 100 satuan"
  return "per 1 satuan"


if __name__ == "__main__":
  print(f"Kurs Transaksi Bank Indonesia, {TANGGAL_KURS}")
  print(f"Kunci terdaftar : {len(KURS)}")
  for nama_kunci in daftar_kunci():
    print(f"  {nama_kunci:9s} {nilai_kurs(nama_kunci):12,.2f}"
          f"  {satuan_kunci(nama_kunci)}")
  # Keluarannya: Kunci terdaftar : 26
