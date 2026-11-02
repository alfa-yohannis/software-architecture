# Bab 15: Capstone Project

Berkas pendukung Bab 15. Seluruh skrip di sini mengukur **keadaan awal** sistem
Exim sebelum satu baris pun diubah, dan seluruhnya hanya memakai pustaka
standar Python.

Sistem yang dikerjakan: <https://github.com/alfa-yohannis/exim>, berjalan di
<https://exim.ayolearn.stream/>.

## Menyiapkan repositori

```bash
git clone https://github.com/alfa-yohannis/exim.git
cd sources/chapter15
python ukur_kopling.py exim/app
```

Kloning cukup sekali. Tidak ada kebergantungan yang perlu dipasang, sebab
ketiga skrip pengukuran hanya membaca kode sumbernya atau menjalankan salinan
satu tahap yang berdiri sendiri.

## Daftar berkas

| Berkas | Kegunaannya |
|---|---|
| `ukur_kopling.py` | Menghitung baris, *fan-out*, dan *fan-in* tiap modul pada satu paket Python |
| `ukur_titik_sentuh.py` | Menghitung baris dan modul yang menyebut satu penanda, misalnya kode bahasa atau nama negara |
| `tahap_penggabungan.py` | Salinan tahap penggabungan peringkat milik Exim, agar dapat diukur tanpa memasang model |
| `ukur_penggabungan.py` | Mengukur lama penggabungan peringkat pada beberapa jumlah kandidat |
| `sebaran.py` | Median, persentil ke-95, dan nilai terbesar, dipakai bersama skrip pengukuran |

## Pemetaan judul ke berkas pengukuran

| Judul | Yang diukur | Berkas yang dipakai |
|---|---|---|
| 4, 5, 14, 18 | Kopling antar modul dan arah ketergantungannya | `ukur_kopling.py` |
| 1, 2, 18, 20 | Titik sentuh satu penambahan, pada kode maupun berkas antarmuka | `ukur_titik_sentuh.py` |
| 8, 9 | Lama satu tahap pada jalur panas | `tahap_penggabungan.py`, `ukur_penggabungan.py`, `sebaran.py` |

## Keluaran yang menjadi acuan

Angka di bawah berasal dari repositori Exim pada saat bab ini ditulis. Hasil
tiap mahasiswa akan berbeda menurut versi repositori dan mesinnya, sehingga
yang dilaporkan pola perbandingannya, bukan angka persisnya.

```
python ukur_kopling.py exim/app
# Jumlah modul        : 23
# Jumlah baris        : 9884
# Jumlah ketergantungan: 63
# Fan-in terbesar     : config, 18 modul mengimpornya
# Fan-out terbesar    : server, mengimpor 12 modul

python ukur_titik_sentuh.py exim/app '"id"' '"en"' '"vi"'
# Berkas tersentuh    : 2
# Baris tersentuh     : 27

python ukur_titik_sentuh.py exim/app Vietnam Indonesia
# Berkas tersentuh    : 8
# Baris tersentuh     : 72

python ukur_titik_sentuh.py exim/app is_admin
# Berkas tersentuh    : 2
# Baris tersentuh     : 4

python ukur_penggabungan.py
#  Kandidat masuk  Kandidat keluar   Median us    P95 us   Terbesar us
#             100               85       19.17     21.49         45.87
#             400              340       73.45     89.22        129.09
```

## Pekerjaan kelompok

Tiap kelompok membuat satu *branch* pada repositori Exim dengan pola
`capstone/<nomor-kelompok>-<judul-pendek>`. Isi *branch*-nya:

| Jalur | Isinya |
|---|---|
| `app/` | Perubahan kode pada modul yang menjadi sasaran |
| `tests/` | Pengujian yang membuktikan perilakunya tidak berubah |
| `capstone/ukur/` | Skrip pengukuran beserta keluarannya apa adanya |
| `capstone/makalah/` | Naskah LaTeX berbahasa Indonesia dan terjemahannya |
| `capstone/README.md` | Judul, anggota kelompok, dan cara menjalankan pengukurannya |

Pengukuran keadaan awal di-*commit* sebelum perubahan kode dimulai.
Pengumpulan pada pertemuan terakhir, yaitu menurut jadwal Ujian Akhir Semester.
