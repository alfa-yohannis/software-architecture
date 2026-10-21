"""Bahan bersama ketiga fungsi bab ini, yaitu tabel kurs dan lapisan tarif.

Berkas ini sengaja kecil dan tidak mengenal penjalan maupun layanan hidup.
Isinya hanya data beserta dua fungsi hitung, sehingga bab ini dapat
menitikberatkan daur hidup contoh fungsi, bukan rumus hitungannya.

Lapisan tarifnya mengikuti lapisan Pajak Penghasilan orang pribadi yang berlaku
di Indonesia, yaitu lima lapis dari lima sampai tiga puluh lima persen.
Angkanya dipakai apa adanya agar tabel yang disusun fungsi pajak berisi data
yang benar-benar ada, bukan data rekaan.

Cara menjalankan: berkas ini diimpor, bukan dijalankan langsung.
"""

KURS = {
  ("USD", "IDR"): 16250.0,
  ("EUR", "IDR"): 17600.0,
  ("SGD", "IDR"): 12100.0,
}

# Batas atas setiap lapis beserta tarifnya. Batas terakhir tak terhingga.
LAPISAN_TARIF = (
  (60_000_000, 0.05),
  (250_000_000, 0.15),
  (500_000_000, 0.25),
  (5_000_000_000, 0.30),
  (float("inf"), 0.35),
)


def nilai_kurs(kode_asal: str, kode_tujuan: str):
  """Mengembalikan float kurs satu pasangan, atau None bila tidak terdaftar."""
  return KURS.get((kode_asal, kode_tujuan))


def hitung_konversi(kode_asal: str, kode_tujuan: str, nominal: float) -> float:
  """Mengalikan nominal dengan kursnya, lalu menolak nominal yang tidak wajar.

  Penolakan diletakkan di sini, bukan di penjalan, sebab penjalan tidak boleh
  mengenal aturan domain mana pun. Mengembalikan float berisi hasil konversi,
  dan melempar ValueError atau LookupError bila masukannya tidak dapat dihitung.
  """
  if nominal <= 0:
    raise ValueError("Nominal harus lebih besar dari nol")
  kurs = nilai_kurs(kode_asal, kode_tujuan)
  if kurs is None:
    raise LookupError(f"Kurs {kode_asal} ke {kode_tujuan} tidak tersedia")
  return nominal * kurs


def hitung_pajak(penghasilan: float) -> float:
  """Menjumlahkan pajak setiap lapis sampai penghasilannya habis terbagi.

  Hitungan ini yang dipanggil berulang kali saat fungsi pajak menyusun tabelnya,
  sehingga biayanya menumpuk menjadi biaya mulai dingin yang terukur.
  Mengembalikan float berisi pajak terutang dalam rupiah.
  """
  sisa = penghasilan
  batas_bawah = 0.0
  pajak = 0.0
  for batas_atas, tarif in LAPISAN_TARIF:
    if sisa <= 0:
      break
    lebar = min(sisa, batas_atas - batas_bawah)
    pajak += lebar * tarif
    sisa -= lebar
    batas_bawah = batas_atas
  return pajak
