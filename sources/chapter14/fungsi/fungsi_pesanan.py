"""Fungsi pencatat pemesanan, contoh fungsi yang menyimpan state sementara.

Konstruktornya menyiapkan penampung kosong, dan pemesanan yang tercatat hanya
hidup selama contoh fungsinya hangat. Sifat itu sengaja dibiarkan agar akibat
turun ke nol terlihat, yaitu nomor urut pemesanan kembali ke satu setiap kali
contohnya dilepas.

Cara menjalankan: python penjalan.py pesanan kopi 3
"""

import domain

# Awalan nomor pesanan, dipakai agar nomornya mudah dikenali pada keluaran.
AWALAN_NOMOR = "PSN"
# Mata uang tagihan, dipakai untuk mengubah harga dolar menjadi rupiah.
MATA_UANG_ASAL = "USD"
MATA_UANG_TUJUAN = "IDR"


class FungsiPesanan:
  """Mencatat satu pemesanan lalu mengembalikan nomor dan tagihannya."""

  def __init__(self) -> None:
    """Menyiapkan penampung pemesanan yang hanya hidup selama contoh hangat.

    Penampung ini sengaja tidak disimpan ke berkas, sebab bab ini justru hendak
    memperlihatkan bahwa state yang dititipkan pada contoh fungsi ikut hilang
    ketika contohnya dilepas.
    """
    self.pesanan = []

  def tangani(self, peristiwa: dict) -> dict:
    """Mencatat satu pemesanan beserta tagihannya dalam rupiah.

    Peristiwa wajib memuat kunci barang, jumlah, dan harga_usd. Mengembalikan
    dict berisi nomor pesanan, tagihan rupiah, dan banyaknya pesanan yang masih
    tersimpan pada contoh fungsi ini.
    """
    tagihan = domain.hitung_konversi(
      MATA_UANG_ASAL, MATA_UANG_TUJUAN,
      peristiwa["harga_usd"] * peristiwa["jumlah"])
    nomor = f"{AWALAN_NOMOR}-{len(self.pesanan) + 1:04d}"
    self.pesanan.append((nomor, peristiwa["barang"], tagihan))
    return {
      "nomor": nomor,
      "tagihan_idr": tagihan,
      "tersimpan": len(self.pesanan),
    }
