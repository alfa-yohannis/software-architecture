# Sumber Bab 11: Service-Based Architecture

Satu aplikasi kecil dengan tiga bidang domain, yaitu kurs, pemesanan, dan
penagihan, ditulis dalam dua versi yang perilaku luarnya sama persis. Versi
monolit menaruh ketiga bidang di dalam satu proses. Versi service-based
memecahnya menjadi tiga layanan domain di porta yang berbeda, ditambah satu
gerbang antarmuka.

Kedua versi memakai berkas basis data yang sama, yaitu `layanan.db`. Basis data
bersama itulah ciri utama service-based architecture, sekaligus yang
membedakannya dari mikroservis yang basis datanya terpisah per layanan.

| Berkas | Kegunaan |
| --- | --- |
| `alamat.py` | Nomor porta kedua versi beserta batas waktu panggilannya |
| `kesalahan.py` | Tiga jenis kesalahan yang dipakai bersama seluruh bidang |
| `basis_data.py` | Skema dan data awal ketiga tabel di dalam satu berkas SQLite |
| `domain_kurs.py` | Bidang kurs, membaca tabel kurs |
| `domain_pemesanan.py` | Bidang pemesanan, pemilik tabel pesanan |
| `domain_penagihan.py` | Bidang penagihan, menghitung tagihan dan membaca tabel pesanan |
| `sarana.py` | Pemetaan jenis kesalahan menjadi kode status HTTP |
| `monolit.py` | Versi monolit, ketiga bidang di dalam satu proses, porta 8000 |
| `gerbang.py` | Gerbang antarmuka versi service-based, porta 8100 |
| `layanan_kurs.py` | Layanan domain kurs, porta 8101 |
| `layanan_pemesanan.py` | Layanan domain pemesanan, porta 8102 |
| `layanan_penagihan.py` | Layanan domain penagihan, porta 8103 |
| `jalankan_layanan.py` | Menyalakan dan mematikan kedua versi lewat modul subprocess |
| `ukur_latensi.py` | 150 putaran, melaporkan median, persentil ke-95, dan terbesar |
| `uji_kegagalan.py` | Mematikan satu layanan lalu mencacah permintaan yang selamat |
| `biaya_perubahan.py` | Menghitung berkas, baris, dan proses ulang dua jenis perubahan |
| `diagram/` | Sumber PlantUML diagram kelas dan diagram urutan |

Venv disiapkan sekali dengan `bash sources/siapkan_venv.sh` dari akar
repositori, lalu diaktifkan dengan `source .venv/bin/activate`. Bab ini memakai
Flask dan requests, yang sudah tercantum di `sources/requirements.txt`.

Seluruh skrip dijalankan dari direktori ini. Urutan penyiapannya:

```bash
python basis_data.py
python jalankan_layanan.py
```

Perintah kedua menyalakan kelima proses, mencoba empat jenis permintaan pada
kedua versi, lalu mematikan seluruhnya. Untuk membiarkan kelimanya hidup dan
mencobanya sendiri dengan `curl`, jalankan `python jalankan_layanan.py hidup`.

Berkas `layanan.db` tidak ikut dilacak Git, sebab isinya dihasilkan ulang oleh
`python basis_data.py`. Skrip pengukuran juga menyiapkannya ulang sebelum
mulai, sehingga latihan selalu berangkat dari keadaan yang sama.

| Latihan | Masalah yang disasar | Berkas yang dipakai |
| --- | --- | --- |
| 1 | Tambahan latensi akibat lompatan jaringan | `ukur_latensi.py` |
| 2 | Permintaan yang selamat ketika satu layanan mati | `uji_kegagalan.py` |
| 3 | Biaya mengubah skema basis data bersama | `biaya_perubahan.py` |

Skrip `biaya_perubahan.py` tidak menyentuh berkas sumber sama sekali.
Perubahannya diterapkan pada salinan di dalam memori, diperiksa dengan
`compile`, lalu dibandingkan memakai `difflib`. Jumlah proses yang harus
dijalankan ulang dihitung dari pernyataan `import` tiap proses memakai `ast`,
sehingga berkas yang dimuat lebih dari satu proses ikut terlihat.
