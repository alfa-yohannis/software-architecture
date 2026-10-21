"""Menghitung pemakaian ulang layanan beserta akibat mengubah salah satunya.

Bagian pertama membaca kelima definisi alur kerja, lalu menghitung berapa alur
kerja yang memakai setiap layanan. Perhitungan itu tidak menjalankan apa pun,
sebab jawabannya memang sudah tertulis pada definisi alur kerja.

Bagian kedua membuktikan akibatnya. Margin pada layanan kurs dinaikkan, lalu
kelima alur kerja dijalankan ulang dan hasilnya dibandingkan dengan hasil
sebelumnya. Alur kerja yang hasilnya berubah adalah alur kerja yang wajib diuji
ulang sebelum layanan itu boleh dipasang.

Data dikembalikan ke keadaan awal sebelum setiap rangkaian, agar perbedaan yang
muncul benar-benar berasal dari perubahan layanan, bukan dari saldo yang sudah
berkurang.

Cara menjalankan: python ukur_pemakaian.py
"""

import konfigurasi
import data
import klien
import orkestrator
import server

# Margin tambahan pada layanan kurs, dalam rupiah per satu satuan valuta asing.
MARGIN_BARU = 50.0

LAYANAN_DIUBAH = "kurs"

# Kunci konteks yang dibandingkan antara kedua rangkaian. Kunci inilah yang
# dilihat pemakai, sehingga perubahan pada salah satunya berarti alur kerjanya
# berubah hasilnya.
KUNCI_DIBANDINGKAN = ("rupiah", "kurs_jual", "saldo_sisa", "terpakai_harian",
                      "nomor_transaksi", "bukti")


def jalankan_satu_alur(nama_alur: str) -> dict:
  """Menjalankan satu alur kerja lalu merekam kunci konteks yang penting.

  Mengembalikan dict berisi nilai kunci konteks yang akan dibandingkan.
  """
  hasil, _ = klien.jalankan_orkestrasi(nama_alur)
  konteks = hasil.get("konteks", {})
  return {kunci: konteks[kunci]
          for kunci in KUNCI_DIBANDINGKAN if kunci in konteks}


def rangkaian_berbagi(margin_tambahan: float) -> dict:
  """Menjalankan kelima alur kerja berurutan di atas data yang sama.

  Inilah keadaan sebenarnya pada sistem berjalan, sebab layanan saldo dan
  layanan batas memang menyimpan satu data bersama bagi seluruh alur kerja.
  Mengembalikan dict berisi rekaman hasil kelima alur kerja.
  """
  data.setel_ulang()
  data.setel_margin_tambahan(margin_tambahan)
  return {nama: jalankan_satu_alur(nama)
          for nama in orkestrator.DEFINISI_ALUR}


def rangkaian_terpisah(margin_tambahan: float) -> dict:
  """Menjalankan setiap alur kerja di atas data yang baru disiapkan ulang.

  Rangkaian ini memisahkan dampak yang datang lewat antarmuka layanan kurs
  dari dampak yang datang lewat data bersama. Mengembalikan dict berisi
  rekaman hasil kelima alur kerja.
  """
  rekaman = {}
  for nama_alur in orkestrator.DEFINISI_ALUR:
    data.setel_ulang()
    data.setel_margin_tambahan(margin_tambahan)
    rekaman[nama_alur] = jalankan_satu_alur(nama_alur)
  return rekaman


def cari_alur_berubah(sebelum: dict, sesudah: dict) -> list:
  """Membandingkan kedua rekaman lalu mengumpulkan alur kerja yang berubah.

  Mengembalikan list berisi nama alur kerja yang hasilnya tidak sama lagi.
  """
  return [nama for nama in sebelum if sebelum[nama] != sesudah[nama]]


def cetak_pemakaian() -> dict:
  """Mencetak tabel pemakaian ulang setiap layanan beserta lapisannya.

  Mengembalikan dict dari nama layanan ke jumlah alur kerja pemakainya.
  """
  pemakaian = orkestrator.hitung_pemakaian_layanan()
  jumlah_alur = len(orkestrator.DEFINISI_ALUR)
  print(f"Alur kerja terdaftar         : {jumlah_alur}")
  print(f"Layanan terdaftar            : {len(pemakaian)}")
  print("Pemakaian ulang per layanan  :")
  for nama, jumlah in pemakaian.items():
    print(f"  {nama:<11} {konfigurasi.LAPISAN[nama]:<15} "
          f"{jumlah} dari {jumlah_alur}")
  return pemakaian


def cetak_dampak(pemakaian: dict, berbagi: tuple, terpisah: tuple) -> None:
  """Mencetak akibat mengubah satu layanan terhadap seluruh alur kerja.

  Kedua rangkaian dilaporkan berdampingan, sebab selisihnya memperlihatkan
  alur kerja yang terdampak lewat data bersama, bukan lewat antarmuka layanan
  yang diubah. Tidak mengembalikan nilai.
  """
  jumlah_alur = len(orkestrator.DEFINISI_ALUR)
  langsung = cari_alur_berubah(*terpisah)
  seluruhnya = cari_alur_berubah(*berbagi)
  tidak_langsung = [nama for nama in seluruhnya if nama not in langsung]
  utuh = [nama for nama in berbagi[0] if nama not in seluruhnya]
  pemakai = orkestrator.alur_pemakai(LAYANAN_DIUBAH)
  print(f"Layanan yang diubah          : {LAYANAN_DIUBAH} "
        f"({konfigurasi.LAPISAN[LAYANAN_DIUBAH]})")
  print(f"Alur kerja pemakai kurs      : {len(pemakai)} dari {jumlah_alur}")
  print(f"Berubah lewat antarmuka      : {len(langsung)} dari {jumlah_alur}")
  print(f"Berubah lewat data bersama   : "
        f"{len(tidak_langsung)} dari {jumlah_alur}")
  print(f"Alur kerja wajib diuji ulang : {len(seluruhnya)} dari {jumlah_alur}")
  print(f"Daftar yang diuji ulang      : {', '.join(seluruhnya)}")
  print(f"Alur kerja tidak terdampak   : {', '.join(utuh)}")
  print(f"Pemakai layanan bukti        : "
        f"{pemakaian['bukti']} dari {jumlah_alur}")
  print(f"Pemakai layanan audit        : "
        f"{pemakaian['audit']} dari {jumlah_alur}")
  print(f"Rupiah pesan-valas sebelum   : "
        f"{terpisah[0]['pesan-valas']['rupiah']:,.0f}")
  print(f"Rupiah pesan-valas sesudah   : "
        f"{terpisah[1]['pesan-valas']['rupiah']:,.0f}")


if __name__ == "__main__":
  kumpulan = server.KumpulanLayanan()
  kumpulan.nyalakan_semua()
  try:
    tabel_pemakaian = cetak_pemakaian()
    berbagi_data = (rangkaian_berbagi(0.0), rangkaian_berbagi(MARGIN_BARU))
    data_terpisah = (rangkaian_terpisah(0.0), rangkaian_terpisah(MARGIN_BARU))
    cetak_dampak(tabel_pemakaian, berbagi_data, data_terpisah)
  finally:
    data.setel_ulang()
    kumpulan.matikan_semua()
  # Keluarannya: Alur kerja berubah hasilnya  : 3 dari 5
