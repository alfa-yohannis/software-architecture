"""Versi tanpa orkestrasi, yaitu layanan yang memanggil layanan berikutnya sendiri.

Setiap file di dalam paket ini mewakili satu layanan yang dipasang
tersendiri. Perbedaannya dengan versi orkestrasi hanya satu, yaitu adanya
tetapan BERIKUTNYA di puncak file. Tetapan itulah potongan workflow yang
dipegang layanan tersebut.

Karena setiap layanan memegang satu potong urutan, tidak ada satu file pun
yang memuat workflow-nya secara utuh. Menyisipkan satu langkah baru ke tengah
workflow karena itu menuntut penyuntingan layanan yang sudah berjalan.
"""
