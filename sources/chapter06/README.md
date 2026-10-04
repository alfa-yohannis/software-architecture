# Sumber Bab 6: Pipeline dan Pipe-and-Filter

Satu *pipeline* pengolah gambar yang menyeragamkan *file* dari sumber yang
beragam. *Stage*-nya menyeragamkan mode warna, memperkecil ke lebar tetap,
menempelkan tanda air, lalu menyimpan sebagai JPEG dengan kualitas tetap.

Penempelan tanda air sekaligus menjadi contoh *merge*, sebab dua gambar disatukan
menjadi satu lewat *alpha channel*. Penyimpanan ke beberapa resolusi sekaligus
menjadi contoh *fan-out*, sebab satu kali pembacaan sumber melayani tiga keluaran
dengan pengaturan berbeda.

| Berkas | Kegunaan |
| --- | --- |
| `unduh_gambar.py` | Mengunduh 60 foto contoh ke `masukan/`, dijalankan sekali di awal |
| `buat_gambar.py` | Cadangan tanpa jaringan, menghasilkan gambar sintetis seukuran serupa |
| `buat_tanda_air.py` | Membuat `tanda_air.png` yang di-*merge* dengan setiap keluaran |
| `penyaring.py` | Kelima *filter*, sebagai fungsi generator dan kelas yang dapat dipanggil |
| `pipa.py` | *Pipe* penyambung *stage*, `Counter` per *stage*, dan kedua cara pemrosesan |
| `percabangan.py` | *Fan-out* tiga resolusi dari satu kali pembacaan, lalu laporannya di-*merge* |
| `periksa_pipa.py` | *Automated check*, melaporkan *filter* yang menyebut tetangganya |
| `uji_susun_ulang.py` | Seratus putaran, membandingkan dua urutan *stage* yang sah menurut *contract* |
| `ukur_aliran.py` | Seratus putaran, membandingkan *streaming* dengan *batch* beserta puncak RSS |
| `diagram/kelas-pipa.puml` | Sumber *class diagram*, hasilnya `figures/kelas-pipa.pdf` |
| `diagram/sekuens-percabangan.puml` | Sumber *sequence diagram*, hasilnya `figures/sekuens-percabangan.pdf` |
| `diagram/buat_diagram.sh` | Menghasilkan ulang kedua PDF diagram lewat SVG |

Venv disiapkan sekali dengan `bash sources/siapkan_venv.sh` dari akar
repositori, lalu diaktifkan dengan `source .venv/bin/activate`. Bab ini memakai
Pillow, yang sudah tercantum di `sources/requirements.txt`.

Seluruh skrip dijalankan dari direktori ini. Urutan penyiapannya:

```bash
python unduh_gambar.py
python buat_tanda_air.py
python pipa.py
```

Direktori `masukan/`, `keluaran/`, dan *file* `tanda_air.png` tidak ikut dilacak
Git, sebab isinya dihasilkan ulang oleh skrip di atas.

| Latihan | Masalah yang disasar | Berkas yang dipakai |
| --- | --- | --- |
| 1 | *Filter independence*, menambah *stage* tanpa menyentuh *filter* lain | `periksa_pipa.py`, `penyaring.py` |
| 2 | *Stage reordering*, akibat menukar dua *stage* yang sah ditukar | `uji_susun_ulang.py` |
| 3 | *First output latency* beserta puncak RSS, *streaming* dibanding *batch* | `ukur_aliran.py` |

## Langkah eksperimen 1: *filter independence*

Yang dibuktikan: tidak satu pun *filter* menyebut nama *filter* lain, sehingga
menambah *stage* tidak mengubah satu baris pun di dalam *filter* yang sudah ada.

1. Jalankan *automated check*-nya, lalu catat keempat angkanya.

   ```bash
   python periksa_pipa.py
   # Keluarannya: Filter ditemukan      : 5
   #              Filter menyebut filter: 0 {}
   #              Baris filter          : 96
   #              Baris pipe            : 109
   ```

2. Jalankan `python pipa.py hitung`, lalu catat jumlah gambar yang diteruskan
   setiap *stage*.

   ```bash
   python pipa.py hitung
   # Keluarannya: ubah_mode    meneruskan 60 gambar
   #              Resize       meneruskan 60 gambar
   #              Watermark    meneruskan 60 gambar
   #              SaveJpeg     meneruskan 60 gambar
   #              Keluaran akhir: 60 file
   ```

3. Tambahkan satu *filter* baru yang memutar gambar, misalnya kelas `Rotate` di
   `penyaring.py`, lalu sisipkan ke dalam `susunan_baku` pada `pipa.py`.
4. Jalankan ulang kedua perintah di atas, lalu catat berapa *filter* lama yang
   perlu disunting. Satu kali percobaan nyata menghasilkan `Filter ditemukan`
   6, `Filter menyebut filter` tetap 0, baris *filter* naik dari 96 menjadi 110,
   dan baris *pipe* dari 109 menjadi 110. Tidak satu pun *filter* lama disunting,
   sebab yang bertambah hanya satu kelas baru di `penyaring.py` dan satu baris
   di `pipa.py`.

## Langkah eksperimen 2: *stage reordering*

Yang dibuktikan: menukar dua *stage* yang sah menurut *contract* tidak
menghasilkan *file* yang sama, walaupun selisih waktunya tenggelam di dalam
ragam pengukuran.

1. Jalankan pembandingnya. Baris kemajuan tercetak setiap dua puluh putaran.

   ```bash
   python uji_susun_ulang.py
   # Keluarannya: Median urutan Resize dahulu    : 0.5835 detik
   #              Median urutan Watermark dahulu : 0.6054 detik
   #              Selisih median                 : 0.0237 detik
   #              Range urutan Resize            : 0.3660 detik
   #              Range urutan Watermark         : 0.4160 detik
   #              Range dibagi selisih           : 16.7 kali
   #              Putaran Resize lebih cepat     : 88 dari 100
   #              Sidik urutan Resize            : 315e279c7f1377fb
   #              Sidik urutan Watermark         : 28cdebf18196279b
   #              File sama persis               : False
   ```

2. Bandingkan baris *range* dengan baris selisih. Selisih baru layak disebut ada
   bila *range*-nya lebih kecil, dan di sini *range*-nya 17 kali selisihnya.
3. Buka satu *file* keluaran dari `keluaran/urut_resize` dan satu lagi dari
   `keluaran/urut_watermark`, lalu bandingkan ketajaman tanda airnya dengan mata.
4. Ubah `susunan_baku` pada `pipa.py` sehingga `SaveJpeg` berada sebelum
   `Watermark`, jalankan `python pipa.py`, lalu catat *error*-nya. Satu kali
   percobaan nyata berhenti dengan `ValueError: too many values to unpack
   (expected 2)`. Kembalikan urutannya sesudah dicatat.

## Langkah eksperimen 3: *first output latency*

Yang diukur: waktu sampai *file* pertama selesai ditulis, beserta puncak
Resident Set Size (RSS) proses pada kedua jalur.

1. Jalankan pengukurannya. Baris kemajuan tercetak setiap dua puluh putaran.

   ```bash
   python ukur_aliran.py
   # Keluarannya: Median file pertama streaming : 83.1 ms
   #              Median file pertama batch     : 792.8 ms
   #              Selisih median                : 709.7 ms
   #              Batch lebih lambat            : 9.5 kali
   #              Range dalam jalur streaming   : 126.1 ms
   #              Range dibagi selisih          : 0.18 kali
   #              Putaran streaming lebih cepat : 100 dari 100
   #              Puncak RSS streaming          : 118.4 MiB
   #              Puncak RSS batch              : 576.8 MiB
   ```

2. Bandingkan baris *range* dengan baris selisih. Di sini *range*-nya 0,18 kali
   selisihnya, sehingga selisih waktunya layak disebut ada.
3. Jalankan kedua jalur memori satu per satu, lalu catat angkanya.

   ```bash
   python ukur_aliran.py memori streaming
   # Keluarannya: 118.4
   python ukur_aliran.py memori batch
   # Keluarannya: 576.8
   ```

4. Turunkan `BATAS_MEMORI` dari 60 menjadi 10, jalankan ulang kedua perintah
   `memori` itu, lalu catat perubahannya. Satu kali percobaan nyata turun
   menjadi 40,0 MiB pada jalur *streaming* dan 118,1 MiB pada jalur *batch*,
   sehingga terlihat bahwa biaya memori jalur *batch* tumbuh mengikuti jumlah
   *file*. Kembalikan nilainya sesudah dicatat.

## Menghasilkan ulang diagram

Kedua diagram UML dibuat dari *file* `.puml` di `diagram/`, dan hasilnya
tersimpan sebagai PDF di `figures/`. Perintahnya dijalankan dari direktori mana
pun, dan membutuhkan PlantUML beserta `rsvg-convert`.

```bash
bash sources/chapter06/diagram/buat_diagram.sh
pdffonts figures/kelas-pipa.pdf
# Keluarannya memuat TitilliumWeb-Regular dan TitilliumWeb-Bold
```

Kode lama berbahasa Rust ada di `rust-example/`, dibiarkan sebagai bahan
pembanding lintas bahasa, dan tidak dipakai pada ketiga latihan.
