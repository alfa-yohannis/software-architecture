# Sumber Bab 13: Microservices

Satu domain kecil, yaitu penukaran valuta asing di sebuah bank, ditulis dua
kali. Versi monolit adalah satu proses dengan satu berkas basis data yang
memuat tiga tabel. Versi mikroservis adalah empat proses, yaitu tiga layanan
yang masing-masing memegang berkas basis datanya sendiri, ditambah satu gerbang
yang tidak memegang basis data sama sekali.

Isi datanya sama persis, sebab monolit memakai objek `Tabel` yang sama dengan
ketiga layanan. Aturan bisnisnya juga sama, yaitu penyamaran nomor rekening,
penyaringan pesanan berstatus batal, dan penambahan margin pada kurs dasar.
Yang berbeda hanya batas datanya, dan akibat dari batas itulah yang diukur.

Batas tersebut punya satu aturan keras. Sebuah layanan hanya boleh membuka
berkas basis datanya sendiri, sehingga tidak ada satu kueri pun yang menyentuh
dua berkas sekaligus. Laporan gabungan karena itu disusun di dalam kode gerbang,
bukan lewat `JOIN`.

| Berkas | Kegunaan |
| --- | --- |
| `alamat.py` | Porta dan alamat seluruh proses, dipakai bersama semua skrip |
| `basis_data.py` | Kelas `BasisDataLayanan` dan `Tabel`, plus laporan pemetaan berkas ke pemiliknya |
| `layanan_nasabah.py` | Layanan nasabah, pemilik tunggal `data/nasabah.db` |
| `layanan_pesanan.py` | Layanan pesanan, pemilik tunggal `data/pesanan.db` |
| `layanan_kurs.py` | Layanan kurs, pemilik tunggal `data/kurs.db` |
| `gerbang.py` | Gerbang tanpa basis data, menyusun laporan gabungan di dalam kode |
| `monolit.py` | Satu proses dengan satu berkas `data/monolit.db` berisi tiga tabel |
| `penjalan.py` | Menyalakan dan mematikan seluruh proses lewat `subprocess` |
| `ukur_latensi.py` | Dua ratus putaran, membandingkan latensi dan jumlah lompatan kedua versi |
| `ukur_laporan.py` | Membandingkan penggabungan di dalam kode dengan `JOIN`, beserta baris kodenya |
| `uji_kegagalan.py` | Mematikan layanan kurs, lalu mencatat permintaan mana yang masih dilayani |
| `ukur_rilis.py` | Menjalankan ulang layanan kurs sambil lalu lintas mengalir |
| `diagram/` | Sumber PlantUML diagram kelas dan diagram urutan beserta skrip pembuatnya |

Venv disiapkan sekali dengan `bash sources/siapkan_venv.sh` dari akar
repositori, lalu diaktifkan dengan `source .venv/bin/activate`. Bab ini memakai
Flask dan requests, keduanya sudah tercantum pada `sources/requirements.txt`.

Seluruh skrip dijalankan dari direktori ini. Mulai dengan `python basis_data.py`
untuk menyiapkan keempat berkas basis data sekaligus melihat pemetaannya:

```
layanan_nasabah  data/nasabah.db   1 tabel, 3 baris
layanan_pesanan  data/pesanan.db   1 tabel, 6 baris
layanan_kurs     data/kurs.db      1 tabel, 3 baris
monolit          data/monolit.db   3 tabel, 12 baris
```

Kedua versi dapat dinyalakan sendiri untuk dicoba dengan `curl`:

```bash
python penjalan.py mikroservis   # gerbang di porta 5310
python penjalan.py monolit       # monolit di porta 5300
```

Skrip pengukuran menyalakan dan mematikan prosesnya sendiri, sehingga tidak
perlu ada proses yang sudah hidup lebih dahulu. Porta 5300 dan 5310 sampai 5313
harus kosong ketika skripnya dijalankan.

| Latihan | Masalah yang disasar | Berkas yang dipakai |
| --- | --- | --- |
| 1 | Latensi dan jumlah lompatan permintaan gabungan | `ukur_latensi.py`, `gerbang.py`, `monolit.py` |
| 2 | Harga penggabungan data dari dua basis data terpisah | `ukur_laporan.py`, `gerbang.py` |
| 3 | Rilis satu layanan dibanding rilis seluruh monolit | `ukur_rilis.py`, `uji_kegagalan.py` |

Diagram dihasilkan ulang dengan `bash sources/chapter13/diagram/buat_diagram.sh`,
dan berkas PDF-nya tersimpan di `figures/`.

Direktori `java-example/` dan `lama/` berisi bahan bab ini pada versi terdahulu.
Keduanya disimpan sebagai pembanding dan tidak dipakai pada ketiga latihan.
