# Sumber Bab 1: Pengenalan dan Client-Server

Satu server melayani banyak klien. Server menyimpan tabel kurs dan menjalankan
seluruh perhitungan, sedangkan klien hanya menampilkan jawabannya.

| Berkas | Kegunaan |
| --- | --- |
| `server.py` | Server HTTP yang menyimpan tabel kurs dan menghitung konversi |
| `klien.py` | Klien yang mengirim permintaan lalu menampilkan jawabannya |
| `ukur_latensi.py` | Mengukur waktu bolak-balik satu permintaan |
| `ukur_beban.py` | Menambah jumlah klien serentak secara bertahap, lalu mencatat latensinya |

Jalankan `python server.py` di satu terminal, lalu skrip lainnya di terminal
kedua. Seluruh pengukuran hanya dijalankan terhadap server milik sendiri.

| Latihan | Masalah yang disasar | Berkas yang dipakai |
| --- | --- | --- |
| 1 | Pemisahan tanggung jawab antara klien dan server | `server.py`, `klien.py` |
| 2 | Biaya waktu satu perjalanan bolak-balik | `ukur_latensi.py` |
| 3 | Perilaku server ketika jumlah klien bertambah | `ukur_beban.py` |

Direktori `java/` berisi versi Java dari aplikasi yang sama, yaitu
`currency-server`, `currency-desktop`, dan `currency-mobile`. Versi tersebut
disimpan sebagai bahan pembanding lintas bahasa dan tidak dipakai pada latihan.
