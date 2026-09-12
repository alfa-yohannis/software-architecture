# Sumber Bab 2: Layered Architecture

Satu basis kode dipakai untuk tiga latihan yang menyasar tiga masalah berbeda,
yaitu kedalaman call stack, arah dependency yang dilanggar, dan
biaya waktu pemeriksaan yang dituntut lapisan bisnis.

Setiap lapisan diwujudkan sebagai satu kelas, dan kolaboratornya diterima lewat
konstruktor. Susunannya digambarkan pada diagram kelas dan diagram urutan di
`diagram/`.

Aplikasi melayani dua request yang membaca tabel yang sama, tetapi tuntutan
bisnisnya berbeda:

- **Kurs dasar** diterbitkan untuk umum, meniru JISDOR yang diumumkan Bank
  Indonesia setiap hari kerja. Tidak ada tuntutan bisnis yang berlaku.
- **Kurs jual** adalah kurs dasar ditambah margin keuntungan bank, yaitu
  harga yang dibayar nasabah ketika membeli valuta asing. Besar keuntungan itu
  bersifat komersial, sehingga lapisan bisnis menuntut autentikasi dan
  otorisasi.

Perbedaan itulah yang membuat satu jalan pintas dapat dibenarkan sedangkan
jalan pintas lainnya tidak.

| Berkas | Kegunaan |
| --- | --- |
| `basis_data.py` | Kelas `BasisDataKurs`, membuat tabel kurs lalu mengisinya |
| `autentikasi.py` | Kelas `PenjagaAkses`, memeriksa token pemanggil dan perannya |
| `aplikasi_tertutup.py` | Empat kelas lapisan tertutup, tiap kelas hanya memegang kelas di bawahnya |
| `aplikasi_terbuka.py` | Tiga kelas, `AntarmukaKurs` memegang `RepositoriKurs` langsung |
| `periksa_lapisan.py` | Kelas `PemeriksaLapisan`, alat bantu opsional untuk memeriksa jawaban Latihan 1 dan 2 sendiri |
| `ukur_lapisan.py` | Kelas `PengukurJalur`, seratus putaran, melaporkan selisih median beserta range-nya |
| `diagram/*.puml` | Sumber PlantUML diagram kelas dan diagram urutan |
| `diagram/buat_diagram.sh` | Menghasilkan ulang kedua diagram menjadi PDF di `figures/` |

Venv disiapkan sekali dengan `bash sources/siapkan_venv.sh` dari akar
repositori, lalu diaktifkan dengan `source .venv/bin/activate`. Langkah
lengkapnya ada di `sources/README.md`.

Seluruh skrip dijalankan dari direktori ini. Jalankan `python basis_data.py`
lebih dahulu agar berkas `kurs.db` terbentuk.

| Latihan | Masalah yang disasar | Berkas yang dipakai |
| --- | --- | --- |
| 1 | Kedalaman call stack sampai `koneksi.execute` | kedua aplikasi, dibaca tanpa dijalankan |
| 2 | Layer violation pada arah dependency, dan akibatnya bagi keamanan | kedua aplikasi, dibaca lalu dijalankan |
| 3 | Biaya waktu pemeriksaan yang dituntut lapisan bisnis | `ukur_lapisan.py` |
