"""Fungsi hitung pajak, contoh fungsi dengan persiapan berat pada fase Init.

Konstruktornya menyusun tabel tarif untuk dua ratus ribu kelipatan penghasilan,
sehingga pencarian saat melayani peristiwa hanya berupa satu kali pembacaan
dict. Susunan itu memindahkan seluruh biaya ke fase Init, dan itulah yang
membuat biaya mulai dinginnya terukur jelas pada Latihan 2.

Tabel sebesar ini bukan hal yang mengada-ada. Dokumentasi AWS Lambda menyebut
kode statis di luar penangan sebagai penyumbang latensi terbesar sebelum fungsi
berjalan, dan penyusunan tabel seperti inilah contoh khasnya.

Cara menjalankan: python penjalan.py pajak 120000000
"""

import domain

# Batas atas tabel yang disusun, yaitu dua ratus juta rupiah setahun.
BATAS_PENGHASILAN = 200_000_000
# Jarak antar baris tabel. Seribu rupiah menghasilkan dua ratus ribu baris.
LANGKAH_TABEL = 1_000


class FungsiPajak:
  """Menghitung pajak terutang lewat tabel yang disusun sekali di awal."""

  def __init__(self) -> None:
    """Menyusun tabel tarif untuk seluruh kelipatan penghasilan sekaligus.

    Penyusunan sengaja diletakkan di konstruktor, sebab di situlah persiapan
    berat pada model tanpa server berada. Akibatnya, pemanggilan pertama pada
    contoh yang baru membayar seluruh penyusunan ini, sedangkan pemanggilan
    berikutnya tidak membayar apa pun.
    """
    self.tabel = {}
    for batas in range(0, BATAS_PENGHASILAN + 1, LANGKAH_TABEL):
      self.tabel[batas] = domain.hitung_pajak(batas)
    self.baris_tabel = len(self.tabel)

  def tangani(self, peristiwa: dict) -> dict:
    """Membaca pajak terutang dari tabel, tanpa menghitung ulang lapisannya.

    Peristiwa wajib memuat kunci penghasilan. Nilainya dibulatkan ke bawah
    mengikuti langkah tabel, sebab tabel hanya menyimpan kelipatannya.
    Mengembalikan dict berisi pajak terutang, tarif efektif, dan jumlah baris
    tabel yang disusun pada fase Init.
    """
    penghasilan = min(peristiwa["penghasilan"], BATAS_PENGHASILAN)
    kunci = int(penghasilan // LANGKAH_TABEL) * LANGKAH_TABEL
    pajak = self.tabel[kunci]
    return {
      "pajak": pajak,
      "tarif_efektif": pajak / penghasilan if penghasilan else 0.0,
      "baris_tabel": self.baris_tabel,
    }
