"""Kontrak yang wajib dipenuhi setiap fungsi tanpa server pada bab ini.

Penjalan fungsi hanya mengenal bentuk pemanggilan di file ini, bukan nama
satu fungsi pun. Kontraknya sengaja sempit, yaitu konstruktor tanpa argumen
ditambah satu metode penangan. Pembagian itu meniru AWS Lambda, yaitu kode di
luar penangan dijalankan sekali pada fase Init, sedangkan penangan dipanggil
pada setiap fase Invoke.

Manifes disimpan sebagai file JavaScript Object Notation (JSON) yang terpisah
dari modulnya, sehingga penjalan dapat membaca daftar event tanpa mengimpor
kode fungsinya. Kunci memori_mb meniru pengaturan memori per fungsi pada Lambda,
dan angkanya dipakai skrip ukur_sumber_daya.py untuk menghitung gigabita detik.

Cara menjalankan: file ini diimpor, bukan dijalankan langsung.
"""

from typing import Protocol

# Key yang wajib ada pada setiap file manifes fungsi.
KUNCI_MANIFES = ("nama", "event", "keterangan", "modul", "kelas", "memori_mb")


class Fungsi(Protocol):
  """Satu kemampuan kecil yang dimuat penjalan ketika event-nya datang."""

  def __init__(self) -> None:
    """Menyiapkan seluruh bahan yang dipakai berulang oleh penangan.

    Seluruh persiapan yang mahal diletakkan di sini, bukan di dalam tangani,
    sebab konstruktor hanya dijalankan sekali pada fase Init. Akibatnya,
    persiapan yang berat menjadi biaya cold start, dan sama sekali tidak
    terasa pada pemanggilan hangat.
    """

  def tangani(self, event: dict) -> dict:
    """Melayani satu event lalu mengembalikan dict berisi hasilnya.

    Kembaliannya berupa dict agar penjalan dapat menyerahkannya apa adanya
    tanpa mengetahui isi fungsinya. Kunci di dalam dict ditentukan masing-masing
    fungsi, sebab penjalan tidak pernah membacanya.
    """
