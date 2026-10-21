"""Kontrak yang wajib dipenuhi setiap fungsi tanpa server pada bab ini.

Penjalan fungsi hanya mengenal bentuk pemanggilan di berkas ini, bukan nama
satu fungsi pun. Kontraknya sengaja sempit, yaitu konstruktor tanpa argumen
ditambah satu metode penangan. Pembagian itu meniru AWS Lambda, yaitu kode di
luar penangan dijalankan sekali pada fase Init, sedangkan penangan dipanggil
pada setiap fase Invoke.

Manifes disimpan sebagai berkas JavaScript Object Notation (JSON) yang terpisah
dari modulnya, sehingga penjalan dapat membaca daftar peristiwa tanpa mengimpor
kode fungsinya. Kunci memori_mb meniru pengaturan memori per fungsi pada Lambda,
dan angkanya dipakai skrip ukur_sumber_daya.py untuk menghitung gigabita detik.

Cara menjalankan: berkas ini diimpor, bukan dijalankan langsung.
"""

from typing import Protocol

# Kunci yang wajib ada pada setiap berkas manifes fungsi.
KUNCI_MANIFES = ("nama", "peristiwa", "keterangan", "modul", "kelas", "memori_mb")


class Fungsi(Protocol):
  """Satu kemampuan kecil yang dimuat penjalan ketika peristiwanya datang."""

  def __init__(self) -> None:
    """Menyiapkan seluruh bahan yang dipakai berulang oleh penangan.

    Seluruh persiapan yang mahal diletakkan di sini, bukan di dalam tangani,
    sebab konstruktor hanya dijalankan sekali pada fase Init. Akibatnya,
    persiapan yang berat menjadi biaya mulai dingin, dan sama sekali tidak
    terasa pada pemanggilan hangat.
    """

  def tangani(self, peristiwa: dict) -> dict:
    """Melayani satu peristiwa lalu mengembalikan dict berisi hasilnya.

    Kembaliannya berupa dict agar penjalan dapat menyerahkannya apa adanya
    tanpa mengetahui isi fungsinya. Kunci di dalam dict ditentukan masing-masing
    fungsi, sebab penjalan tidak pernah membacanya.
    """
