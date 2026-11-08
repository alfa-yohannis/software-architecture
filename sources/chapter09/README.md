# Sumber Bab 9: Event-Driven Architecture

Satu alur kerja kecil yang dikerjakan tiga kali dengan susunan berbeda. Alurnya
selalu sama, yaitu satu request konversi kurs dicatat, diperiksa, lalu
diberitahukan. Yang berbeda hanya cara *message*-nya disampaikan.

Susunan pertama adalah panggilan berantai langsung, tanpa event sama sekali,
dan menjadi titik nol pengukuran. Susunan kedua adalah topologi broker, yaitu
setiap pelanggan berlangganan sendiri lalu menerbitkan event lanjutannya.
Susunan ketiga adalah topologi mediator, yaitu satu pengatur memegang urutan
langkah lalu memanggil tiap pemroses bergantian.

Brokernya dibuat dari `queue.Queue` dan `threading` pada pustaka standar
Python. Tidak ada Kafka, tidak ada Docker, dan tidak ada layanan luar, sehingga
seluruh latihan berjalan pada satu laptop.

| *File* | Kegunaan |
| --- | --- |
| `domain.py` | Objek `Request`, tabel kurs, batas tinjauan, dan tanda selesai |
| `pemroses.py` | Pencatat, Pemeriksa, Pemberitahu, ditambah dua pemeriksa uji |
| `sinkron.py` | Susunan pembanding tanpa event, pemanggilan berantai langsung |
| `broker.py` | Topologi broker beserta penyalur event dan ketiga pelanggannya |
| `mediator.py` | Topologi mediator beserta antrean perintah dan antrean balasan |
| `audit.py` | `PencatatAudit`, pelanggan baru yang disisipkan pada Latihan 3 |
| `varian_audit/` | Salinan ketiga susunan sesudah pencatat audit disisipkan |
| `ukur_latensi.py` | Dua ratus putaran, membandingkan latensi dan jumlah *message* |
| `uji_ketahanan.py` | Satu pemroses gagal, lalu satu pemroses lambat |
| `ukur_perubahan.py` | Menghitung *file* dan baris yang berubah pada ketiga susunan |

Venv disiapkan sekali dengan `bash sources/siapkan_venv.sh` dari akar
repositori, lalu diaktifkan dengan `source .venv/bin/activate`. Bab ini hanya
memakai pustaka standar Python, sehingga tidak ada pemasangan tambahan.

Seluruh skrip dijalankan dari direktori ini. Mulai dengan menjalankan ketiga
susunan berurutan, sehingga terlihat bahwa hasilnya sama dan jumlah *message*-nya
berbeda:

```bash
python sinkron.py
python broker.py
python mediator.py
```

*File* di dalam `varian_audit/` dijalankan sebagai modul dari direktori ini,
misalnya `python -m varian_audit.broker`, sebab *file* itu mengimpor `domain`
dan `pemroses` yang berada satu tingkat di atasnya.

| Latihan | Masalah yang disasar | *File* yang dipakai |
| --- | --- | --- |
| 1 | Latensi dan jumlah *message* susunan sinkron dibanding susunan event | `ukur_latensi.py` |
| 2 | Nasib request ketika satu pemroses gagal atau lambat | `uji_ketahanan.py`, `pemroses.py` |
| 3 | Biaya menambah satu pelanggan baru | `ukur_perubahan.py`, `audit.py`, `varian_audit/` |

## Langkah eksperimen 1: *latency cost*

Yang diukur: latensi ujung ke ujung, waktu penerbit kembali, dan jumlah *message*
pada ketiga susunan, dua ratus putaran berselang-seling.

1. Jalankan pengukurannya. Satu penjalanan penuh selesai di bawah satu detik.

   ```bash
   python ukur_latensi.py
   # Keluarannya, tabel pertama dan bagian perbandingan broker:
   # Susunan       Median  Persentil-95  Terbesar   Kembali Message  Tuntas
   # sinkron       0.0053        0.0066    0.0105    0.0049     0.0     200
   # broker        0.0333        0.0505    0.0937    0.0024     3.0     200
   # mediator      0.0498        0.0622    0.1430    0.0024     7.0     200
   # Range ujung ke ujung sinkron  : 0.0057 ms
   #   selisih median              : 0.0280 ms
   #   range sinkron dibagi selisih: 0.2 kali
   #   putaran sinkron lebih cepat : 200 dari 200
   ```

2. Bandingkan median ketiganya. Susunan sinkron paling cepat, sebab setiap
   *message* yang masuk antrean harus membangunkan *thread* lain, dan pembangunan
   itu lebih mahal daripada pekerjaan yang diangkutnya.
3. Bandingkan selisih median dengan *range* jalur sinkron. Selisih terhadap
   broker 0,0280 ms, yaitu 4,9 kali *range*-nya, sehingga selisih itu dapat
   disebut ada.
4. Perhatikan kolom kembali. Susunan berbasis event justru lebih cepat, namun
   selisihnya lebih kecil daripada *range*, sehingga yang dipakai pencacahan
   per putaran, yaitu 199 dari 200 pada broker dan 200 dari 200 pada mediator.
5. Ubah `JUMLAH_PERMINTAAN` menjadi lima ratus, jalankan ulang, lalu catat
   perubahan persentil ke-95 dan nilai terbesarnya. Kembalikan nilainya sesudah
   dicatat.

## Langkah eksperimen 2: *failure containment*

Yang diukur: nasib seratus request ketika pemeriksa menolak setiap
request kelipatan lima, lalu ketika pemeriksa menahan lima milidetik.

1. Jalankan kedua skenarionya.

   ```bash
   python uji_ketahanan.py
   # Keluarannya, tabel skenario satu:
   # Susunan     Tuntas  Tercatat  Diberitahu   Error  Berhenti
   # sinkron          4         5           4       0         5
   # broker          80       100          80      20     tidak
   # mediator        80       100          80      20     tidak
   # Keluarannya, tabel skenario dua:
   # Yang diukur          sinkron    broker  mediator
   # Penerbit kembali       513.1       0.1       0.1
   # Antrean terdalam           0       100       100
   # Seluruh tercatat       513.4       1.3     543.9
   # Seluruh tuntas         513.5     512.0     548.6
   # Request tuntas           100       100       100
   ```

2. Buka `pemroses.py`, lalu tunjukkan baris pada `PemeriksaGagal` yang
   menentukan request mana yang ditolak.
3. Bandingkan ketiga contoh catatan *error*-nya. Broker menyebut topik beserta
   nomor request, sedangkan mediator menyebut langkah yang putus beserta
   sisa langkahnya.
4. Perhatikan kolom seluruh tercatat pada skenario kedua, yaitu 1,3 ms pada
   broker melawan 543,9 ms pada mediator. Mediator menangani satu request
   pada satu waktu, sehingga pengaturnya menjadi leher botol.
5. Naikkan `JEDA_LAMBAT` menjadi lima puluh milidetik, jalankan ulang, lalu
   catat perubahan antrean terdalam dan waktu penerbit kembali. Kembalikan
   nilainya sesudah dicatat.

## Langkah eksperimen 3: *change cost*

Yang diukur: *file* dan baris yang berubah ketika satu pelanggan baru
disisipkan, beserta jumlah *message* sebelum dan sesudahnya.

1. Jalankan penghitungannya.

   ```bash
   python ukur_perubahan.py
   # Keluarannya, tabel dan jejak langkah broker:
   # Susunan    File Baris tambah Baris hapus Message sebelum Message sesudah
   # sinkron       1            6           3             0.0             0.0
   # broker        1            3           0             3.0             4.0
   # mediator      1            3           1             7.0             9.0
   # Jejak langkah broker    : ['pencatat', 'pemeriksa', 'pemberitahu', 'audit']
   ```

2. Bandingkan `broker.py` dengan `varian_audit/broker.py`. Baris barunya hanya
   masuk ke bagian perakitan, sebab pelanggan baru cukup berlangganan pada
   topik yang sudah ada.
3. Bandingkan `sinkron.py` dengan `varian_audit/sinkron.py`. Baris barunya
   masuk ke badan `kirim`, yaitu alur bisnis yang dijalankan pada setiap
   request.
4. Jalankan ulang beberapa kali, lalu catat jejak langkah brokernya. Dua belas
   kali penjalanan menghasilkan tiga bentuk, yaitu `audit` di urutan pertama
   delapan kali, di urutan kedua dua kali, dan di urutan terakhir dua kali.
   Sebabnya, pencatat audit berlangganan pada topik yang sama dengan pencatat
   biasa.

## Menghasilkan ulang diagram

Kedua diagram UML dibuat dari *file* `.puml` di `diagram/`, dan hasilnya
tersimpan sebagai PDF di `figures/`.

```bash
bash sources/chapter09/diagram/buat_diagram.sh
pdffonts figures/kelas-event.pdf
# Keluarannya memuat TitilliumWeb-Regular dan TitilliumWeb-Bold
```
