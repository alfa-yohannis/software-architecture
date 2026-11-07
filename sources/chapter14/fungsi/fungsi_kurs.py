"""Fungsi konversi kurs, contoh fungsi dengan persiapan ringan.

Konstruktornya hanya menyalin tabel kurs, sehingga fase Init-nya hampir tidak
berbiaya. Fungsi inilah yang dipakai sebagai pembanding pada Latihan 1, yaitu
ketika selisih cold start dan warm start ditakar terhadap ragam
pengukurannya sendiri.

Cara menjalankan: python penjalan.py kurs USD IDR 100
"""

import domain


class FungsiKurs:
  """Mengubah nominal satu mata uang menjadi mata uang lain."""

  def __init__(self) -> None:
    """Menyalin tabel kurs sekali saja pada fase Init.

    Penyalinan dilakukan agar contoh fungsi memegang salinannya sendiri, persis
    seperti objek yang dibuat di luar penangan pada AWS Lambda. Biayanya kecil,
    dan kekecilan itulah yang menjadi pembanding fungsi pajak.
    """
    self.kurs = dict(domain.KURS)
    self.jumlah_panggilan = 0

  def tangani(self, event: dict) -> dict:
    """Menghitung satu konversi berdasarkan isi event yang masuk.

    Event wajib memuat kunci asal, tujuan, dan nominal. Mengembalikan dict
    berisi kurs terpakai, hasil konversi, dan nomor urut pemanggilan pada contoh
    fungsi ini, sehingga pemakaian ulang contoh yang hangat terlihat dari
    nomornya.
    """
    self.jumlah_panggilan += 1
    hasil = domain.hitung_konversi(
      event["asal"], event["tujuan"], event["nominal"])
    return {
      "kurs": self.kurs[(event["asal"], event["tujuan"])],
      "hasil": hasil,
      "panggilan_ke": self.jumlah_panggilan,
    }
