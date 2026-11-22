# Sumber Bab 12: Orchestration-Driven SOA

Satu *workflow* bisnis yang sama dijalankan dengan dua cara. Cara pertama
memakai *orchestration engine* yang memegang seluruh urutan langkah, dan layanannya
tidak saling mengenal. Cara kedua tidak memakai *engine* sama sekali, sehingga
setiap layanan memanggil layanan berikutnya sendiri dan urutannya tersebar.

*Workflow* utamanya adalah pemesanan valuta asing dengan enam langkah, yaitu
periksa nasabah, ambil kurs, potong saldo, catat transaksi, buat bukti, dan
catat audit. Empat *workflow* lain memakai ulang layanan yang sama, sehingga
akibat mengubah satu layanan dapat dihitung.

Ketujuh layanan dikelompokkan menurut taksonomi orchestration-driven SOA.
*Layer* business service diwakili `DEFINISI_ALUR` pada `orkestrator.py`, yang
hanya berisi urutan langkah tanpa satu baris aturan bisnis pun.

| Layanan | *Layer* | Dipakai |
| --- | --- | --- |
| `nasabah` | enterprise | 4 dari 5 *workflow* |
| `kurs` | enterprise | 3 dari 5 *workflow* |
| `batas` | enterprise | 2 dari 5 *workflow* |
| `saldo` | enterprise | 3 dari 5 *workflow* |
| `transaksi` | enterprise | 4 dari 5 *workflow* |
| `bukti` | application | 1 dari 5 *workflow* |
| `audit` | infrastructure | 5 dari 5 *workflow* |

| *File* | Kegunaan |
| --- | --- |
| `konfigurasi.py` | Alamat, nomor *port*, dan *layer* taksonomi setiap layanan |
| `data.py` | Data milik tiap layanan beserta pencacah *request* HTTP |
| `langkah.py` | Tujuh fungsi langkah bisnis, dipakai kedua versi |
| `layanan.py` | Pabrik layanan pasif versi orkestrasi, tanpa pengetahuan urutan |
| `orkestrator.py` | *Orchestration engine* beserta kelima definisi *workflow* |
| `berantai/pembantu.py` | Pabrik bersama layanan versi tanpa orkestrasi |
| `berantai/nasabah.py` | Layanan nasabah, memegang `BERIKUTNYA = "kurs"` |
| `berantai/kurs.py` | Layanan kurs, memegang `BERIKUTNYA = "saldo"` |
| `berantai/saldo.py` | Layanan saldo, memegang `BERIKUTNYA = "transaksi"` |
| `berantai/transaksi.py` | Layanan transaksi, memegang `BERIKUTNYA = "bukti"` |
| `berantai/bukti.py` | Layanan bukti, memegang `BERIKUTNYA = "audit"` |
| `berantai/audit.py` | Layanan audit, ujung rantai dengan `BERIKUTNYA = None` |
| `server.py` | Menyalakan dan mematikan seluruh layanan pada utasnya |
| `klien.py` | Pemanggil kedua versi dari sisi luar beserta *request* contoh |
| `ukur_lompatan.py` | Dua ratus *workflow* kedua versi, latensi dan *hop* |
| `ukur_perubahan.py` | *Change cost* menyisipkan satu langkah ke tengah *workflow* |
| `ukur_pemakaian.py` | *Reuse* layanan beserta akibat mengubah salah satunya |
| `uji_kegagalan.py` | Mematikan satu layanan di tengah *workflow* lalu memulihkannya |
| `sesudah/` | Salinan *file* sesudah langkah baru disisipkan, bahan pembanding |
| `diagram/` | Sumber PlantUML beserta skrip pembuat PDF ke `figures/` |

Empat belas server dinyalakan sekaligus, yaitu *orchestration engine*, tujuh layanan
pasif, dan enam layanan berantai. Seluruhnya berjalan sebagai utas di dalam
satu proses Python agar cukup satu perintah, sedangkan pemanggilan antar
layanan tetap lewat HTTP pada *port* yang berbeda. *Port*-nya berada di rentang
7120 sampai 7137.

Venv disiapkan sekali dengan `bash sources/siapkan_venv.sh` dari akar
repositori, lalu diaktifkan dengan `source .venv/bin/activate`. Bab ini memakai
Flask dan requests, keduanya sudah tercantum pada `sources/requirements.txt`.

Seluruh skrip dijalankan dari direktori ini. Mulai dengan `python klien.py`
untuk melihat kedua versi menghasilkan bukti yang sama.

| Latihan | Masalah yang disasar | *File* yang dipakai |
| --- | --- | --- |
| 1 | Tambahan latensi dan *hop* akibat *orchestration engine* | `ukur_lompatan.py` |
| 2 | *Change cost* menyisipkan satu langkah | `ukur_perubahan.py`, `sesudah/` |
| 3 | Akibat mengubah layanan yang dipakai banyak *workflow* | `ukur_pemakaian.py` |

Direktori `sesudah/` bukan kode yang dijalankan, melainkan salinan kode
sesudah langkah pemeriksaan batas harian disisipkan ke tengah *workflow*
`pesan-valas`. Skrip `ukur_perubahan.py` membandingkannya dengan kode
sekarang memakai `difflib`, lalu memasang definisi *workflow* yang baru sekali
untuk membuktikan bahwa hasil suntingannya benar-benar berjalan.

## Langkah eksperimen 1: *hop* dan latensi

Yang diukur: latensi satu *workflow* pemesanan valuta asing pada kedua versi,
dua ratus putaran, beserta jumlah *hop* HTTP per *workflow*.

1. Jalankan `python klien.py`, lalu pastikan kedua versi menghasilkan bukti
   yang sama. Angka *hop*-nya tujuh pada orkestrasi dan enam pada versi
   berantai.
2. Jalankan pengukurannya. Skripnya mencetak baris kemajuan setiap empat puluh
   putaran.

   ```bash
   python ukur_lompatan.py
   # Keluarannya: Median orkestrasi            : 8.366 ms
   #              Median berantai              : 7.888 ms
   #              Range dibagi selisih         : 7.7 kali
   #              Hop orkestrasi               : 7 per workflow
   #              Hop berantai                 : 6 per workflow
   #              Putaran berantai lebih cepat : 142 dari 200
   ```

3. Bagi median berantai dengan enam *hop*-nya, lalu bandingkan hasilnya dengan
   selisih median, yaitu 0,478 ms.
4. Perhatikan baris `Range dibagi selisih`. *Range*-nya 7,7 kali selisih,
   sehingga yang dipakai untuk menyimpulkan adalah pencacahan per putaran,
   yaitu 142 dari 200.
5. Ubah `JUMLAH_PUTARAN` menjadi 50, jalankan ulang, lalu catat perubahan pada
   baris pencacahan putaran. Kembalikan nilainya sesudah dicatat.

## Langkah eksperimen 2: menyisipkan satu langkah

Yang diukur: *file* dan baris yang berubah ketika langkah pemeriksaan batas
harian disisipkan ke tengah *workflow* `pesan-valas`.

1. Jalankan penghitungannya.

   ```bash
   python ukur_perubahan.py
   # Keluarannya: File disunting orkestrasi    : 1
   #              File disunting berantai      : 3
   #              Baris berubah orkestrasi     : 2 (1 tambah, 1 hapus)
   #              Baris berubah berantai       : 25 (24 tambah, 1 hapus)
   #              Layanan lama ikut disunting  : 0 lawan 1
   #              Tempat urutan langkah ditulis: 1 lawan 6
   ```

2. Bandingkan `orkestrator.py` dengan salinannya di `sesudah/`. Pada versi
   orkestrasi, urutan langkahnya tertulis di satu tempat saja.
3. Buka `berantai/kurs.py`, lalu tunjukkan baris `BERIKUTNYA` yang ikut
   disunting. Itulah layanan lama yang harus dipasang ulang.
4. Sisipkan sendiri satu langkah `audit` kedua ke tengah *workflow*
   `tukar-poin` pada `DEFINISI_ALUR`, jalankan
   `python ukur_pemakaian.py`, lalu catat berapa *file* layanan yang tersentuh.

## Langkah eksperimen 3: layanan yang dipakai banyak *workflow*

Yang diukur: berapa dari lima *workflow* yang harus diuji ulang ketika satu
layanan diubah.

1. Jalankan penghitungannya.

   ```bash
   python ukur_pemakaian.py
   # Keluarannya: Workflow pemakai kurs        : 3 dari 5
   #              Berubah lewat antarmuka      : 3 dari 5
   #              Berubah lewat data bersama   : 1 dari 5
   #              Workflow wajib diuji ulang   : 4 dari 5
   #              Pemakai layanan bukti        : 1 dari 5
   #              Pemakai layanan audit        : 5 dari 5
   ```

2. Buka `orkestrator.py`, lalu hitung sendiri berapa *workflow* yang memanggil
   layanan `kurs`. Hasilnya tiga, padahal empat *workflow* wajib diuji ulang.
3. Ubah `LAYANAN_DIUBAH` menjadi `"bukti"`, jalankan ulang, lalu bandingkan
   jumlah *workflow* yang wajib diuji ulang. Kembalikan nilainya sesudah
   dicatat.
4. Naikkan `MARGIN_BARU` menjadi lima ratus rupiah, jalankan ulang, lalu catat
   apakah jumlah *workflow* yang terdampak ikut berubah.

## Menghasilkan ulang diagram

Kedua diagram UML dibuat dari *file* `.puml` di `diagram/`, dan hasilnya
tersimpan sebagai PDF di `figures/`.

```bash
bash sources/chapter12/diagram/buat_diagram.sh
pdffonts figures/kelas-odsoa.pdf
# Keluarannya memuat TitilliumWeb-Regular dan TitilliumWeb-Bold
```
