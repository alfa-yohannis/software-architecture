# Sumber Bab 14: Serverless

Satu penjalan fungsi kecil yang memuat modul fungsi ketika event-nya datang,
menyimpan objeknya selama masih *warm*, lalu melepasnya sesudah diam melewati
batas. Perilaku itu meniru tiga fase daur hidup AWS Lambda, yaitu `Init`,
`Invoke`, dan `Shutdown`, beserta kemampuan *scale to zero*. Pembandingnya sebuah
layanan yang hidup terus dan menyiapkan seluruh penangannya sekali di awal.

Seluruh *file* berjalan di satu laptop dengan pustaka standar Python saja. Tidak
ada akun awan, tidak ada Docker, dan tidak ada layanan luar yang dibutuhkan.

Ketiga fungsi berada di direktori `fungsi/`, masing-masing sebagai satu modul
beserta satu *file* manifes. Manifes disimpan terpisah dari modulnya agar
penjalan dapat membaca daftar event tanpa mengimpor kodenya, dan pemisahan
itulah yang membuat *scale to zero* mungkin. *Key* `memori_mb` pada manifes meniru
pengaturan memori per fungsi pada Lambda, lalu dipakai untuk menghitung gigabita
detik.

| *File* | Kegunaan |
| --- | --- |
| `kontrak.py` | Kontrak `Fungsi` beserta kunci wajib manifesnya |
| `domain.py` | Tabel kurs dan lapisan tarif pajak, dipakai bersama ketiga fungsi |
| `pendaftar.py` | Registri manifes, membaca daftar event tanpa mengimpor modul |
| `penjalan.py` | Penjalan fungsi, mengurus fase Init, Invoke, Shutdown, dan kolam contoh |
| `layanan_hidup.py` | Pembanding yang hidup terus dan menyebut ketiga nama fungsinya |
| `fungsi/fungsi_kurs.py` | Kelas `FungsiKurs`, event `kurs`, persiapan ringan |
| `fungsi/fungsi_pesanan.py` | Kelas `FungsiPesanan`, event `pesanan`, state hanya hidup selama *warm* |
| `fungsi/fungsi_pajak.py` | Kelas `FungsiPajak`, event `pajak`, menyusun tabel 200.001 baris saat Init |
| `ukur_mulai.py` | Dua ratus panggilan per fungsi, memisahkan latensi *cold start* dari *warm start* |
| `ukur_sumber_daya.py` | Memori dan waktu saat menganggur, lalu hitungan gigabita detik |
| `ukur_lonjakan.py` | Dua belas request serentak, mencatat contoh yang dibuat dan yang menunggu |
| `ukur_perubahan.py` | Biaya menambah satu fungsi baru pada kedua jalur, dihitung sebagai *file* dan baris |
| `diagram/kelas-serverless.puml` | Diagram kelas penjalan, pendaftar, dan ketiga fungsinya |
| `diagram/sekuens-serverless.puml` | Diagram urutan satu *cold start* dibanding satu *warm start* |
| `diagram/buat_diagram.sh` | Menghasilkan kedua diagram menjadi PDF di `figures/` |

Venv disiapkan sekali dengan `bash sources/siapkan_venv.sh` dari akar
repositori, lalu diaktifkan dengan `source .venv/bin/activate`. Langkah
lengkapnya ada di `sources/README.md`.

Seluruh skrip dijalankan dari direktori ini. Mulai dengan `python penjalan.py`
untuk melihat satu contoh fungsi lahir, dipakai ulang, lalu dilepas kembali.

| Latihan | Masalah yang disasar | *File* yang dipakai |
| --- | --- | --- |
| 1 | *Cold start cost* ditakar terhadap ragam pengukurannya | `ukur_mulai.py`, `fungsi/fungsi_kurs.py` |
| 2 | *Idle cost* beserta titik impas gigabita detiknya | `ukur_sumber_daya.py`, `fungsi/fungsi_pajak.py` |
| 3 | *Concurrency limit* ketika request-nya datang serentak | `ukur_lonjakan.py`, `layanan_hidup.py` |

## Langkah eksperimen 1: *cold start cost*

Yang diukur: latensi pemanggilan yang harus membuat contohnya lebih dahulu
dibanding pemanggilan yang menemukan contoh siap pakai, dua ratus panggilan
per fungsi.

1. Jalankan pengukurannya. Setiap panggilan kelima sengaja dibuat menjadi
   *cold start*.

   ```bash
   python ukur_mulai.py
   # Keluarannya pada fungsi pajak:
   #   Median cold start            : 120.5837 ms
   #   Median warm start            : 0.0059 ms
   #   Cold start lebih lambat      : 20554.8 kali
   #   Range dibagi selisih         : 0.0004 kali
   #   Melebihi warm start terbesar : 40 dari 40
   ```

2. Bandingkan kedua fungsi. Fungsi kurs yang persiapannya ringan membayar
   0,2414 ms, sedangkan fungsi pajak yang menyusun 200.001 baris tabel membayar
   120,5837 ms.
3. Perhatikan median *warm start* kedua fungsi, yaitu 0,0027 ms dan 0,0059 ms.
   Selisihnya jauh lebih kecil daripada *range* kelompoknya, sebab persiapan
   yang berat sudah dibayar pada fase Init, sehingga penangan hanya membaca
   satu baris dict.
4. Ubah `LANGKAH_TABEL` pada `fungsi/fungsi_pajak.py` dari 1.000 menjadi 100,
   jalankan ulang, lalu catat median *cold start*-nya. Kembalikan nilainya
   sesudah dicatat.

## Langkah eksperimen 2: *idle cost*

Yang diukur: memori dan waktu prosesor saat diam, lalu tagihan gigabita detik
pada beban 720 request per jam.

1. Jalankan pengukurannya.

   ```bash
   python ukur_sumber_daya.py
   # Keluarannya: Memori penjalan saat nol      : 16.0 KiB
   #              Memori layanan saat menganggur: 21179.3 KiB
   #              Gigabita detik cold start     : 20.88
   #              Gigabita detik layanan hidup  : 1800.00
   #              Titik impas bila cold start   : 62,069 request per jam
   ```

2. Bandingkan baris memori saat nol dengan memori layanan saat menganggur.
   Selisihnya 1.324 kali, dan sebabnya nol modul fungsi melawan tiga modul
   fungsi.
3. Perhatikan baris *request* pertama sesudah diam, yaitu 114,8584 ms pada
   penjalan melawan 0,0090 ms pada layanan. Itulah harga *scale to zero*.
4. Ubah `memori_mb` pada `fungsi/fungsi_pajak.json` dari 256 menjadi 512,
   jalankan ulang, lalu catat perubahan gigabita detik dan titik impasnya.
   Kembalikan nilainya sesudah dicatat.

## Langkah eksperimen 3: *concurrency limit*

Yang diukur: nasib dua belas request serentak ketika batas contohnya empat,
diulang sepuluh putaran pada tiga keadaan.

1. Jalankan percobaannya.

   ```bash
   python ukur_lonjakan.py
   # Keluarannya: Contoh fungsi dibuat          : 40
   #              Request menunggu           : 80
   #              Median latensi                : 696.9689 ms
   #              Median latensi, kolam hangat  : 0.0127 ms
   ```

2. Bandingkan ketiga keadaannya. Kolam kosong membuat empat contoh per
   lonjakan dan menyisakan delapan request menunggu, sedangkan kolam hangat
   tidak membuat satu contoh baru pun.
3. Naikkan `BATAS_CONTOH` pada `penjalan.py` dari 4 menjadi 12, jalankan ulang,
   lalu catat request yang menunggu beserta median latensinya.
4. Kembalikan batasnya menjadi 4, lalu naikkan `JUMLAH_SERENTAK` pada
   `ukur_lonjakan.py` dari 12 menjadi 24 dan catat median latensinya.
   Kembalikan nilainya sesudah dicatat.

## Menghasilkan ulang diagram

Kedua diagram UML dibuat dari *file* `.puml` di `diagram/`, dan hasilnya
tersimpan sebagai PDF di `figures/`.

```bash
bash sources/chapter14/diagram/buat_diagram.sh
pdffonts figures/kelas-serverless.pdf
# Keluarannya memuat TitilliumWeb-Regular dan TitilliumWeb-Bold
```

Skrip `ukur_perubahan.py` dipakai di luar ketiga latihan, yaitu untuk
memperlihatkan bahwa penjalan tidak menyebut satu nama fungsi pun, sedangkan
layanan hidup menyebutnya pada dua baris untuk setiap fungsi.
