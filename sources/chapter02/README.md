# Sumber Bab 2: Layered Architecture

Satu basis kode dipakai untuk tiga latihan yang menyasar tiga masalah berbeda,
yaitu lapisan yang tidak bekerja, arah ketergantungan yang dilanggar, dan biaya
waktu setiap lompatan antar lapisan.

Aplikasi melayani dua permintaan yang membaca tabel yang sama, tetapi tuntutan
bisnisnya berbeda:

- **Kurs referensi** diterbitkan untuk umum, meniru JISDOR yang diumumkan Bank
  Indonesia setiap hari kerja. Tidak ada tuntutan bisnis yang berlaku.
- **Kurs jual** adalah kurs referensi ditambah margin. Margin bersifat
  komersial, sehingga lapisan bisnis menuntut autentikasi dan otorisasi.

Perbedaan itulah yang membuat satu jalan pintas dapat dibenarkan sedangkan
jalan pintas lainnya tidak.

| Berkas | Kegunaan |
| --- | --- |
| `basis_data.py` | Membuat tabel kurs berisi nilai referensi dan margin, lalu mengisinya |
| `autentikasi.py` | Memeriksa token pemanggil dan peran yang dimilikinya |
| `aplikasi_tertutup.py` | Empat lapisan tertutup, setiap lapisan hanya memanggil lapisan di bawahnya |
| `aplikasi_terbuka.py` | Lapisan presentasi memanggil lapisan persistensi langsung untuk kedua permintaan |
| `periksa_lapisan.py` | Melaporkan fungsi penerus, pelanggaran arah, dan jumlah fungsi per lapisan |
| `ukur_lapisan.py` | Menjalankan seratus putaran, lalu melaporkan jalur mana yang menang |

Seluruh skrip dijalankan dari direktori ini. Jalankan `python basis_data.py`
lebih dahulu agar berkas `kurs.db` terbentuk.

| Latihan | Masalah yang disasar | Berkas yang dipakai |
| --- | --- | --- |
| 1 | Lapisan yang hanya meneruskan panggilan | `periksa_lapisan.py` |
| 2 | Arah ketergantungan yang dilanggar, dan akibatnya bagi keamanan | `periksa_lapisan.py`, kedua aplikasi |
| 3 | Biaya waktu pemeriksaan yang dituntut lapisan bisnis | `ukur_lapisan.py` |
