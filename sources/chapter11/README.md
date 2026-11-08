# Sumber Bab 11: Service-Based Architecture

Satu aplikasi kecil dengan tiga bidang domain, yaitu kurs, pemesanan, dan
penagihan, ditulis dalam dua versi yang perilaku luarnya sama persis. Versi
monolit menaruh ketiga bidang di dalam satu proses. Versi service-based
memecahnya menjadi tiga layanan domain di *port* yang berbeda, ditambah satu
gerbang antarmuka.

Kedua versi memakai *file* basis data yang sama, yaitu `layanan.db`. Basis data
bersama itulah ciri utama service-based architecture, sekaligus yang
membedakannya dari mikroservis yang basis datanya terpisah per layanan.

| *File* | Kegunaan |
| --- | --- |
| `alamat.py` | Nomor *port* kedua versi beserta batas waktu panggilannya |
| `kesalahan.py` | Tiga jenis kesalahan yang dipakai bersama seluruh bidang |
| `basis_data.py` | Skema dan data awal ketiga tabel di dalam satu *file* SQLite |
| `domain_kurs.py` | Bidang kurs, membaca tabel kurs |
| `domain_pemesanan.py` | Bidang pemesanan, pemilik tabel pesanan |
| `domain_penagihan.py` | Bidang penagihan, menghitung tagihan dan membaca tabel pesanan |
| `sarana.py` | Pemetaan jenis kesalahan menjadi kode status HTTP |
| `monolit.py` | Versi monolit, ketiga bidang di dalam satu proses, *port* 8000 |
| `gerbang.py` | Gerbang antarmuka versi service-based, *port* 8100 |
| `layanan_kurs.py` | Layanan domain kurs, *port* 8101 |
| `layanan_pemesanan.py` | Layanan domain pemesanan, *port* 8102 |
| `layanan_penagihan.py` | Layanan domain penagihan, *port* 8103 |
| `jalankan_layanan.py` | Menyalakan dan mematikan kedua versi lewat modul subprocess |
| `ukur_latensi.py` | 150 putaran, melaporkan median, persentil ke-95, dan terbesar |
| `uji_kegagalan.py` | Mematikan satu layanan lalu mencacah *request* yang selamat |
| `biaya_perubahan.py` | Menghitung *file*, baris, dan proses ulang dua jenis perubahan |
| `diagram/` | Sumber PlantUML diagram kelas dan diagram urutan |

Venv disiapkan sekali dengan `bash sources/siapkan_venv.sh` dari akar
repositori, lalu diaktifkan dengan `source .venv/bin/activate`. Bab ini memakai
Flask dan requests, yang sudah tercantum di `sources/requirements.txt`.

Seluruh skrip dijalankan dari direktori ini. Urutan penyiapannya:

```bash
python basis_data.py
python jalankan_layanan.py
```

Perintah kedua menyalakan kelima proses, mencoba empat jenis *request* pada
kedua versi, lalu mematikan seluruhnya. Untuk membiarkan kelimanya hidup dan
mencobanya sendiri dengan `curl`, jalankan `python jalankan_layanan.py hidup`.

*File* `layanan.db` tidak ikut dilacak Git, sebab isinya dihasilkan ulang oleh
`python basis_data.py`. Skrip pengukuran juga menyiapkannya ulang sebelum
mulai, sehingga latihan selalu berangkat dari keadaan yang sama.

| Latihan | Masalah yang disasar | *File* yang dipakai |
| --- | --- | --- |
| 1 | Tambahan latensi akibat *hop* jaringan | `ukur_latensi.py` |
| 2 | Request yang selamat ketika satu layanan mati | `uji_kegagalan.py` |
| 3 | Biaya mengubah skema basis data bersama | `biaya_perubahan.py` |

Skrip `biaya_perubahan.py` tidak menyentuh *file* sumber sama sekali.
Perubahannya diterapkan pada salinan di dalam memori, diperiksa dengan
`compile`, lalu dibandingkan memakai `difflib`. Jumlah proses yang harus
dijalankan ulang dihitung dari pernyataan `import` tiap proses memakai `ast`,
sehingga *file* yang dimuat lebih dari satu proses ikut terlihat.

## Langkah eksperimen 1: *hop* jaringan

Yang diukur: waktu tanggap *request* terbitkan tagihan pada kedua versi,
seratus lima puluh putaran berselang-seling.

1. Jalankan pengukurannya. Skripnya menyalakan kelima proses sendiri, lalu
   mematikannya kembali sesudah selesai.

   ```bash
   python ukur_latensi.py
   # Keluarannya: Median monolit                : 30.01 ms
   #              Median service-based          : 34.70 ms
   #              Range dibagi selisih          : 4.49 kali
   #              Putaran monolit lebih cepat   : 140 dari 150
   #              Hop monolit                   : 1
   #              Hop service-based             : 4
   ```

2. Bandingkan selisih mediannya, yaitu 4,68 ms, dengan *range*-nya. *Range*-nya
   4,49 kali selisih itu, sehingga menurut ukuran Bab 2 selisihnya belum dapat
   disebut ada.
3. Baca pencacahan per putarannya. Monolit lebih cepat pada 140 dari 150
   putaran, jauh di atas 75, yaitu angka yang diharapkan bila kedua versi sama
   cepat. Angka ini berubah antarpenjalanan, dan penjalanan kedua pada mesin
   yang sama mencatat 125 dari 150.
4. Buka `gerbang.py`, lalu hitung berapa kali fungsi `minta` dipanggil pada
   jalur terbitkan tagihan. Bandingkan hitungan itu dengan angka *hop* yang
   dilaporkan skripnya.

## Langkah eksperimen 2: satu layanan mati

Yang diukur: berapa dari empat jenis *request* yang masih terlayani ketika
bidang kurs dimatikan, lalu ketika *file* basis data bersama dikunci.

1. Jalankan percobaannya.

   ```bash
   python uji_kegagalan.py
   # Keluarannya: Seluruh proses hidup           4 dari 4    4 dari 4
   #              Bidang kurs dimatikan          0 dari 4    2 dari 4
   #              Basis data bersama dikunci     0 dari 4    0 dari 4
   #                Service-based                baca pesanan, baca tagihan
   ```

2. Bandingkan baris bidang kurs dimatikan. Versi monolit kehilangan keempat
   *request* sekaligus, sebab bidang kurs tidak punya proses sendiri. Versi
   service-based masih melayani baca pesanan dan baca tagihan.
3. Perhatikan baris basis data bersama dikunci. Kedua versi sama-sama nol dari
   empat, sebab titik kegagalannya pindah ke *file* `layanan.db` yang dipakai
   bersama.
4. Ubah `LAYANAN_DIMATIKAN` menjadi `"pemesanan"`, jalankan ulang, lalu catat
   perubahan angkanya. Kembalikan nilainya sesudah dicatat.

## Langkah eksperimen 3: perubahan skema bersama

Yang diukur: *file*, baris, dan proses yang harus dijalankan ulang pada dua
perubahan, yaitu fitur di dalam satu bidang dan penggantian nama satu kolom
pada tabel yang dipakai dua bidang.

1. Jalankan penghitungannya.

   ```bash
   python biaya_perubahan.py
   # Keluarannya pada perubahan 1:
   #   Service-based  file 2   baris 23   proses ulang 1 dari 4
   # Keluarannya pada perubahan 2:
   #   Service-based  file 3   baris 16   proses ulang 3 dari 4
   #   Proses ulang   : kurs, pemesanan, penagihan
   ```

2. Bandingkan jumlah *file* dan baris yang berubah. Angkanya sama pada kedua
   versi, sehingga pembedanya hanya kolom proses ulang.
3. Perhatikan daftar proses ulang pada perubahan kedua. Layanan kurs ikut
   dijalankan ulang, padahal bidang kurs tidak membaca tabel pesanan.
4. Terapkan perubahan kedua sungguhan pada *file* sumbernya, jalankan
   `python basis_data.py` lalu `python jalankan_layanan.py`, dan catat apa yang
   terjadi bila hanya satu dari ketiga *file* yang diubah. Kembalikan kodenya
   sesudah dicatat.

## Menghasilkan ulang diagram

Kedua diagram UML dibuat dari *file* `.puml` di `diagram/`, dan hasilnya
tersimpan sebagai PDF di `figures/`.

```bash
bash sources/chapter11/diagram/buat_diagram.sh
pdffonts figures/kelas-layanan.pdf
# Keluarannya memuat TitilliumWeb-Regular dan TitilliumWeb-Bold
```
