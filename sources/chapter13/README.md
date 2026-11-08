# Sumber Bab 13: Microservices

Satu domain kecil, yaitu penukaran valuta asing di sebuah bank, ditulis dua
kali. Versi monolit adalah satu proses dengan satu *file* basis data yang
memuat tiga tabel. Versi mikroservis adalah empat proses, yaitu tiga layanan
yang masing-masing memegang *file* basis datanya sendiri, ditambah satu gerbang
yang tidak memegang basis data sama sekali.

Isi datanya sama persis, sebab monolit memakai objek `Tabel` yang sama dengan
ketiga layanan. Aturan bisnisnya juga sama, yaitu penyamaran nomor rekening,
penyaringan pesanan berstatus batal, dan penambahan margin pada kurs dasar.
Yang berbeda hanya batas datanya, dan akibat dari batas itulah yang diukur.

Batas tersebut punya satu aturan keras. Sebuah layanan hanya boleh membuka
*file* basis datanya sendiri, sehingga tidak ada satu kueri pun yang menyentuh
dua *file* sekaligus. Laporan gabungan karena itu disusun di dalam kode gerbang,
bukan lewat `JOIN`.

| *File* | Kegunaan |
| --- | --- |
| `alamat.py` | *Port* dan alamat seluruh proses, dipakai bersama semua skrip |
| `basis_data.py` | Kelas `BasisDataLayanan` dan `Tabel`, plus laporan pemetaan *file* ke pemiliknya |
| `layanan_nasabah.py` | Layanan nasabah, pemilik tunggal `data/nasabah.db` |
| `layanan_pesanan.py` | Layanan pesanan, pemilik tunggal `data/pesanan.db` |
| `layanan_kurs.py` | Layanan kurs, pemilik tunggal `data/kurs.db` |
| `gerbang.py` | Gerbang tanpa basis data, menyusun laporan gabungan di dalam kode |
| `monolit.py` | Satu proses dengan satu *file* `data/monolit.db` berisi tiga tabel |
| `penjalan.py` | Menyalakan dan mematikan seluruh proses lewat `subprocess` |
| `ukur_latensi.py` | Dua ratus putaran, membandingkan latensi dan jumlah *hop* kedua versi |
| `ukur_laporan.py` | Membandingkan penggabungan di dalam kode dengan `JOIN`, beserta baris kodenya |
| `uji_kegagalan.py` | Mematikan layanan kurs, lalu mencatat *request* mana yang masih dilayani |
| `ukur_rilis.py` | Menjalankan ulang layanan kurs sambil lalu lintas mengalir |
| `diagram/` | Sumber PlantUML diagram kelas dan diagram urutan beserta skrip pembuatnya |

Venv disiapkan sekali dengan `bash sources/siapkan_venv.sh` dari akar
repositori, lalu diaktifkan dengan `source .venv/bin/activate`. Bab ini memakai
Flask dan requests, keduanya sudah tercantum pada `sources/requirements.txt`.

Seluruh skrip dijalankan dari direktori ini. Mulai dengan `python basis_data.py`
untuk menyiapkan keempat *file* basis data sekaligus melihat pemetaannya:

```
layanan_nasabah  data/nasabah.db   1 tabel, 3 baris
layanan_pesanan  data/pesanan.db   1 tabel, 6 baris
layanan_kurs     data/kurs.db      1 tabel, 3 baris
monolit          data/monolit.db   3 tabel, 12 baris
```

Kedua versi dapat dinyalakan sendiri untuk dicoba dengan `curl`:

```bash
python penjalan.py mikroservis   # gerbang di port 5310
python penjalan.py monolit       # monolit di port 5300
```

Skrip pengukuran menyalakan dan mematikan prosesnya sendiri, sehingga tidak
perlu ada proses yang sudah hidup lebih dahulu. *Port* 5300 dan 5310 sampai 5313
harus kosong ketika skripnya dijalankan.

| Latihan | Masalah yang disasar | *File* yang dipakai |
| --- | --- | --- |
| 1 | Latensi dan jumlah *hop* *request* gabungan | `ukur_latensi.py`, `gerbang.py`, `monolit.py` |
| 2 | Harga penggabungan data dari dua basis data terpisah | `ukur_laporan.py`, `gerbang.py` |
| 3 | Rilis satu layanan dibanding rilis seluruh monolit | `ukur_rilis.py`, `uji_kegagalan.py` |

## Langkah eksperimen 1: latensi dan jumlah *hop*

Yang diukur: latensi *request* yang menyentuh satu sumber data dan *request*
yang menyentuh tiga sumber data, dua ratus putaran pada kedua versi.

1. Jalankan pengukurannya. Skripnya menyalakan kedua versi sendiri, lalu
   mematikannya sesudah selesai.

   ```bash
   python ukur_latensi.py
   # Keluarannya:
   # Versi        Request     Median      p95  Terbesar       Hop
   # monolit      nasabah       1.60     1.85      2.16         1
   # monolit      laporan       1.62     1.83      2.02         1
   # mikroservis  nasabah       3.00     3.30      3.57         2
   # mikroservis  laporan       7.77     8.43      9.18         5
   ```

2. Bandingkan kedua jalur mikroservis. Jalur laporan menempuh lima *hop* dan
   jalur nasabah dua, sehingga biayanya mengikuti jumlah *hop*, bukan jumlah
   layanan yang terpasang.
3. Buka `gerbang.py`, lalu temukan baris yang menghitung *key* `lompatan` pada
   fungsi `susun_laporan`.
4. Nyalakan versi mikroservis dengan `python penjalan.py mikroservis`, lalu
   dari terminal lain panggil `http://127.0.0.1:5310/laporan/N-002` dan catat
   jumlah *hop*-nya. Nasabah tersebut hanya memiliki satu pesanan dalam satu
   mata uang. Hentikan penjalannya dengan Ctrl+C sesudah dicatat.

## Langkah eksperimen 2: harga penggabungan

Yang diukur: waktu, baris kode penggabung, dan jumlah *request* jaringan untuk
laporan yang sama, disusun lewat satu kueri SQL dan lewat tiga panggilan HTTP.

1. Jalankan pengukurannya.

   ```bash
   python ukur_laporan.py
   # Keluarannya: Median laporan monolit            : 1.63 ms
   #              Median laporan mikroservis        : 7.53 ms
   #              Putaran monolit lebih cepat       : 200 dari 200
   #              Baris kode penggabung monolit     : 26
   #              Baris kode penggabung mikroservis : 44
   #              Request jaringan mikroservis      : 5
   #              Isi kedua laporan sama            : True
   ```

2. Bandingkan `KUERI_LAPORAN` pada `monolit.py` dengan `susun_laporan` pada
   `gerbang.py`. Klausa `JOIN` pada kueri itu digantikan `kumpulkan_kurs` dan
   `gabungkan_baris` di dalam kode.
3. Tambahkan satu pesanan bermata uang JPY untuk nasabah N-001 pada `ISI_AWAL`
   di `layanan_pesanan.py`, lalu tambahkan barisnya pada `ISI_AWAL` di
   `layanan_kurs.py`.
4. Jalankan ulang `python basis_data.py` lalu `python ukur_laporan.py`, lalu
   catat perubahan jumlah *request* jaringannya. Kembalikan kedua *file* sesudah
   dicatat.

## Langkah eksperimen 3: rilis satu layanan

Yang diukur: *request* yang tidak terlayani penuh selama satu layanan dirilis
ulang, dibanding rilis ulang seluruh monolit.

1. Matikan layanan kurs, lalu catat berapa jenis *request* yang masih
   terlayani.

   ```bash
   python uji_kegagalan.py
   # Keluarannya: Terlayani sesudah kurs mati, monolit     : 0 dari 3
   #              Terlayani sesudah kurs mati, mikroservis : 2 dari 3
   ```

2. Jalankan pengukuran rilisnya. Skripnya mengulang rilis tujuh kali pada tiap
   baris.

   ```bash
   python ukur_rilis.py
   # Keluarannya:
   # Versi        Jalur      Penuh  Sebagian  Gagal Tidak penuh  Padam ms  Terbesar
   # monolit      nasabah      193         0      7           7       198       225
   # monolit      laporan      193         0      7           7       196       207
   # mikroservis  nasabah      200         0      0           0       186       232
   # mikroservis  laporan      191         9      0           9       237       247
   ```

3. Bandingkan kolom gagal dan kolom sebagian. Pada mikroservis, laporan yang
   kehilangan kursnya tetap keluar sebagian, sedangkan jalur nasabah tidak
   tersentuh sama sekali.
4. Ubah `gabungkan_baris` pada `gerbang.py` sehingga melempar *error* ketika
   kursnya bernilai `None`, jalankan ulang kedua skrip, lalu catat perubahan
   golongan pada baris laporan. Kembalikan kodenya sesudah dicatat.

## Menghasilkan ulang diagram

Kedua diagram UML dibuat dari *file* `.puml` di `diagram/`, dan hasilnya
tersimpan sebagai PDF di `figures/`.

```bash
bash sources/chapter13/diagram/buat_diagram.sh
pdffonts figures/kelas-mikroservis.pdf
# Keluarannya memuat TitilliumWeb-Regular dan TitilliumWeb-Bold
```

Direktori `java-example/` dan `lama/` berisi bahan bab ini pada versi terdahulu.
Keduanya disimpan sebagai pembanding dan tidak dipakai pada ketiga latihan.
