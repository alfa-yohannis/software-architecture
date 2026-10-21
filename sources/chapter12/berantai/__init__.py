"""Versi tanpa orkestrasi, yaitu layanan yang memanggil penerusnya sendiri.

Setiap berkas di dalam paket ini mewakili satu layanan yang dipasang
tersendiri. Perbedaannya dengan versi orkestrasi hanya satu, yaitu adanya
tetapan BERIKUTNYA di puncak berkas. Tetapan itulah potongan alur kerja yang
dipegang layanan tersebut.

Karena setiap layanan memegang satu potong urutan, tidak ada satu berkas pun
yang memuat alur kerjanya secara utuh. Menyisipkan satu langkah baru ke tengah
alur kerja karena itu menuntut penyuntingan layanan yang sudah berjalan.
"""
