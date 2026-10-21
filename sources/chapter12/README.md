# Sumber Bab 12: Orchestration-Driven SOA

Satu alur kerja bisnis yang sama dijalankan dengan dua cara. Cara pertama
memakai mesin orkestrasi yang memegang seluruh urutan langkah, dan layanannya
tidak saling mengenal. Cara kedua tidak memakai mesin sama sekali, sehingga
setiap layanan memanggil penerusnya sendiri dan urutannya tersebar.

Alur kerja utamanya adalah pemesanan valuta asing dengan enam langkah, yaitu
periksa nasabah, ambil kurs, potong saldo, catat transaksi, buat bukti, dan
catat audit. Empat alur kerja lain memakai ulang layanan yang sama, sehingga
akibat mengubah satu layanan dapat dihitung.

Ketujuh layanan dikelompokkan menurut taksonomi orchestration-driven SOA.
Lapisan business service diwakili `DEFINISI_ALUR` pada `orkestrator.py`, yang
hanya berisi urutan langkah tanpa satu baris aturan bisnis pun.

| Layanan | Lapisan | Dipakai |
| --- | --- | --- |
| `nasabah` | enterprise | 4 dari 5 alur kerja |
| `kurs` | enterprise | 3 dari 5 alur kerja |
| `batas` | enterprise | 2 dari 5 alur kerja |
| `saldo` | enterprise | 3 dari 5 alur kerja |
| `transaksi` | enterprise | 4 dari 5 alur kerja |
| `bukti` | application | 1 dari 5 alur kerja |
| `audit` | infrastructure | 5 dari 5 alur kerja |

| Berkas | Kegunaan |
| --- | --- |
| `konfigurasi.py` | Alamat, nomor port, dan lapisan taksonomi setiap layanan |
| `data.py` | Data milik tiap layanan beserta pencacah permintaan HTTP |
| `langkah.py` | Tujuh fungsi langkah bisnis, dipakai kedua versi |
| `layanan.py` | Pabrik layanan pasif versi orkestrasi, tanpa pengetahuan urutan |
| `orkestrator.py` | Mesin orkestrasi beserta kelima definisi alur kerja |
| `berantai/pembantu.py` | Pabrik bersama layanan versi tanpa orkestrasi |
| `berantai/nasabah.py` | Layanan nasabah, memegang `BERIKUTNYA = "kurs"` |
| `berantai/kurs.py` | Layanan kurs, memegang `BERIKUTNYA = "saldo"` |
| `berantai/saldo.py` | Layanan saldo, memegang `BERIKUTNYA = "transaksi"` |
| `berantai/transaksi.py` | Layanan transaksi, memegang `BERIKUTNYA = "bukti"` |
| `berantai/bukti.py` | Layanan bukti, memegang `BERIKUTNYA = "audit"` |
| `berantai/audit.py` | Layanan audit, ujung rantai dengan `BERIKUTNYA = None` |
| `server.py` | Menyalakan dan mematikan seluruh layanan pada utasnya |
| `klien.py` | Pemanggil kedua versi dari sisi luar beserta permintaan contoh |
| `ukur_lompatan.py` | Dua ratus alur kerja kedua versi, latensi dan lompatan |
| `ukur_perubahan.py` | Biaya menyisipkan satu langkah baru ke tengah alur kerja |
| `ukur_pemakaian.py` | Pemakaian ulang layanan beserta akibat mengubah salah satunya |
| `uji_kegagalan.py` | Mematikan satu layanan di tengah alur kerja lalu memulihkannya |
| `sesudah/` | Salinan berkas sesudah langkah baru disisipkan, bahan pembanding |
| `diagram/` | Sumber PlantUML beserta skrip pembuat PDF ke `figures/` |

Empat belas server dinyalakan sekaligus, yaitu mesin orkestrasi, tujuh layanan
pasif, dan enam layanan berantai. Seluruhnya berjalan sebagai utas di dalam
satu proses Python agar cukup satu perintah, sedangkan pemanggilan antar
layanan tetap lewat HTTP pada port yang berbeda. Portnya berada di rentang
7120 sampai 7137.

Venv disiapkan sekali dengan `bash sources/siapkan_venv.sh` dari akar
repositori, lalu diaktifkan dengan `source .venv/bin/activate`. Bab ini memakai
Flask dan requests, keduanya sudah tercantum pada `sources/requirements.txt`.

Seluruh skrip dijalankan dari direktori ini. Mulai dengan `python klien.py`
untuk melihat kedua versi menghasilkan bukti yang sama.

| Latihan | Masalah yang disasar | Berkas yang dipakai |
| --- | --- | --- |
| 1 | Tambahan latensi dan lompatan akibat mesin orkestrasi | `ukur_lompatan.py` |
| 2 | Biaya menyisipkan satu langkah ke tengah alur kerja | `ukur_perubahan.py`, `sesudah/` |
| 3 | Akibat mengubah layanan yang dipakai banyak alur kerja | `ukur_pemakaian.py` |

Direktori `sesudah/` bukan kode yang dijalankan, melainkan keadaan tersimpan
sesudah langkah pemeriksaan batas harian disisipkan ke tengah alur kerja
`pesan-valas`. Skrip `ukur_perubahan.py` membandingkannya dengan keadaan
sekarang memakai `difflib`, lalu memasang definisi alur kerja yang baru sekali
untuk membuktikan bahwa hasil suntingannya benar-benar berjalan.
