# Sumber Bab 9: Event-Driven Architecture

Satu alur kerja kecil yang dikerjakan tiga kali dengan susunan berbeda. Alurnya
selalu sama, yaitu satu permintaan konversi kurs dicatat, diperiksa, lalu
diberitahukan. Yang berbeda hanya cara pesannya disampaikan.

Susunan pertama adalah panggilan berantai langsung, tanpa event sama sekali,
dan menjadi titik nol pengukuran. Susunan kedua adalah topologi broker, yaitu
setiap pelanggan berlangganan sendiri lalu menerbitkan event lanjutannya.
Susunan ketiga adalah topologi mediator, yaitu satu pengatur memegang urutan
langkah lalu memanggil tiap pemroses bergantian.

Brokernya dibuat dari `queue.Queue` dan `threading` pada pustaka standar
Python. Tidak ada Kafka, tidak ada Docker, dan tidak ada layanan luar, sehingga
seluruh latihan berjalan pada satu laptop.

| Berkas | Kegunaan |
| --- | --- |
| `domain.py` | Objek `Permintaan`, tabel kurs, batas tinjauan, dan tanda selesai |
| `pemroses.py` | Pencatat, Pemeriksa, Pemberitahu, ditambah dua pemeriksa uji |
| `sinkron.py` | Susunan pembanding tanpa event, pemanggilan berantai langsung |
| `broker.py` | Topologi broker beserta penyalur event dan ketiga pelanggannya |
| `mediator.py` | Topologi mediator beserta antrean perintah dan antrean balasan |
| `audit.py` | `PencatatAudit`, pelanggan baru yang disisipkan pada Latihan 3 |
| `varian_audit/` | Salinan ketiga susunan sesudah pencatat audit disisipkan |
| `ukur_latensi.py` | Dua ratus putaran, membandingkan latensi dan jumlah pesan |
| `uji_ketahanan.py` | Satu pemroses gagal, lalu satu pemroses lambat |
| `ukur_perubahan.py` | Menghitung berkas dan baris yang berubah pada ketiga susunan |

Venv disiapkan sekali dengan `bash sources/siapkan_venv.sh` dari akar
repositori, lalu diaktifkan dengan `source .venv/bin/activate`. Bab ini hanya
memakai pustaka standar Python, sehingga tidak ada pemasangan tambahan.

Seluruh skrip dijalankan dari direktori ini. Mulai dengan menjalankan ketiga
susunan berurutan, sehingga terlihat bahwa hasilnya sama dan jumlah pesannya
berbeda:

```bash
python sinkron.py
python broker.py
python mediator.py
```

Berkas di dalam `varian_audit/` dijalankan sebagai modul dari direktori ini,
misalnya `python -m varian_audit.broker`, sebab berkas itu mengimpor `domain`
dan `pemroses` yang berada satu tingkat di atasnya.

| Latihan | Masalah yang disasar | Berkas yang dipakai |
| --- | --- | --- |
| 1 | Latensi dan jumlah pesan susunan sinkron dibanding susunan event | `ukur_latensi.py` |
| 2 | Nasib permintaan ketika satu pemroses gagal atau lambat | `uji_ketahanan.py`, `pemroses.py` |
| 3 | Biaya menambah satu pelanggan baru | `ukur_perubahan.py`, `audit.py`, `varian_audit/` |

## Langkah eksperimen 1: *latency cost*

Yang diukur: latensi ujung ke ujung, waktu penerbit kembali, dan jumlah pesan
pada ketiga susunan, dua ratus putaran berselang-seling.

1. Jalankan pengukurannya. Satu penjalanan penuh selesai di bawah satu detik.

   ```bash
   python ukur_latensi.py
   # Keluarannya: sinkron   0.0065 ms  p95 0.0108  terbesar 0.0230  pesan 0
   #              broker    0.0361 ms  p95 0.0600  terbesar 0.0730  pesan 3
   #              mediator  0.0544 ms  p95 0.0725  terbesar 0.1129  pesan 7
   #              Range ujung ke ujung sinkron : 0.0177 ms
   #              putaran sinkron lebih cepat  : 200 dari 200
   ```

2. Bandingkan median ketiganya. Susunan sinkron paling cepat, sebab setiap
   pesan yang masuk antrean harus membangunkan *thread* lain, dan pembangunan
   itu lebih mahal daripada pekerjaan yang diangkutnya.
3. Bandingkan selisih median dengan *range* jalur sinkron. Selisih terhadap
   broker 0,0296 ms, yaitu 1,7 kali *range*-nya, sehingga selisih itu dapat
   disebut ada.
4. Perhatikan kolom kembali. Susunan berbasis event justru lebih cepat, namun
   selisihnya lebih kecil daripada *range*, sehingga yang dipakai pencacahan
   per putaran, yaitu 199 dari 200.
5. Ubah `JUMLAH_PERMINTAAN` menjadi lima ratus, jalankan ulang, lalu catat
   perubahan persentil ke-95 dan nilai terbesarnya. Kembalikan nilainya sesudah
   dicatat.

## Langkah eksperimen 2: *failure containment*

Yang diukur: nasib seratus permintaan ketika pemeriksa menolak setiap
permintaan kelipatan lima, lalu ketika pemeriksa menahan lima milidetik.

1. Jalankan kedua skenarionya.

   ```bash
   python uji_ketahanan.py
   # Keluarannya: sinkron   tuntas   4  tercatat   5  berhenti pada 5
   #              broker    tuntas  80  tercatat 100  berhenti tidak
   #              mediator  tuntas  80  tercatat 100  berhenti tidak
   #              sinkron   penerbit kembali 517.6 ms  antrean   0
   #              broker    penerbit kembali   0.4 ms  antrean 100
   ```

2. Buka `pemroses.py`, lalu tunjukkan baris pada `PemeriksaGagal` yang
   menentukan permintaan mana yang ditolak.
3. Bandingkan ketiga contoh catatan galatnya. Broker menyebut topik beserta
   nomor permintaan, sedangkan mediator menyebut langkah yang putus beserta
   sisa langkahnya.
4. Perhatikan kolom seluruh tercatat pada skenario kedua, yaitu 1,9 ms pada
   broker melawan 543,7 ms pada mediator. Mediator menangani satu permintaan
   pada satu waktu, sehingga pengaturnya menjadi leher botol.
5. Naikkan `JEDA_LAMBAT` menjadi lima puluh milidetik, jalankan ulang, lalu
   catat perubahan antrean terdalam dan waktu penerbit kembali. Kembalikan
   nilainya sesudah dicatat.

## Langkah eksperimen 3: *change cost*

Yang diukur: berkas dan baris yang berubah ketika satu pelanggan baru
disisipkan, beserta jumlah pesan sebelum dan sesudahnya.

1. Jalankan penghitungannya.

   ```bash
   python ukur_perubahan.py
   # Keluarannya: sinkron   tambah 6  hapus 3  pesan 0.0 lalu 0.0
   #              broker    tambah 3  hapus 0  pesan 3.0 lalu 4.0
   #              mediator  tambah 3  hapus 1  pesan 7.0 lalu 9.0
   #              Jejak broker: ['audit', 'pencatat', 'pemeriksa', 'pemberitahu']
   ```

2. Bandingkan `broker.py` dengan `varian_audit/broker.py`. Baris barunya hanya
   masuk ke bagian perakitan, sebab pelanggan baru cukup berlangganan pada
   topik yang sudah ada.
3. Bandingkan `sinkron.py` dengan `varian_audit/sinkron.py`. Baris barunya
   masuk ke badan `kirim`, yaitu alur bisnis yang dijalankan pada setiap
   permintaan.
4. Jalankan ulang beberapa kali, lalu catat jejak langkah brokernya. Dua belas
   kali penjalanan menghasilkan tiga bentuk, yaitu `audit` di urutan pertama
   delapan kali, di urutan terakhir tiga kali, dan di urutan kedua satu kali.
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

Direktori `event-driven-architecture/` dan `java-example/` adalah bahan
pembanding lintas bahasa yang memakai broker sungguhan. Keduanya tidak dipakai
pada latihan dan tidak membutuhkan venv.
