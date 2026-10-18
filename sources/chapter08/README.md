# Sumber Bab 8: Space-Based Architecture

Satu aplikasi pemroses setoran valuta asing, dibuat dalam dua versi dengan
domain yang sama persis. Pada versi basis data, setiap *processing unit* membaca
kurs dan menyimpan hasil ke SQLite pada setiap tugas, sehingga berkas basis data
berada di jalur setiap permintaan. Pada versi ruang, unit membaca kurs dari grid
memorinya sendiri lalu menumpuk hasil di penyangga lokal, dan penulis data yang
memindahkannya ke SQLite di luar jalur permintaan.

*Processing unit* berjalan sebagai proses, bukan thread, sebab penafsir Python
bawaan masih memakai satu kunci global sehingga thread tidak benar-benar
berjalan berbarengan. Ruang bersama dititipkan ke satu proses middleware, lalu
dipakai seluruh unit lewat proksi.

| Berkas | Kegunaan |
| --- | --- |
| `domain.py` | Tabel kurs, kelas `Tugas`, dan fungsi hitung yang dipakai kedua versi |
| `ruang.py` | *Tuple space* dengan operasi `tulis`, `ambil`, dan `baca` ala Linda |
| `layanan_ruang.py` | Proses middleware yang memegang ruang bersama dan meminjamkannya lewat proksi |
| `basis_data.py` | Berkas SQLite beserta skema tabel kurs dan tabel hasil |
| `unit.py` | `UnitBasisData`, `UnitRuang`, `PenulisData`, beserta penjalan beban kedua versi |
| `ukur_hasil.py` | Menaikkan jumlah unit lalu membandingkan hasil per detik dan sebaran latensi |
| `ukur_basi.py` | Menghitung *stale read* pada beberapa *replication lag* |
| `uji_kehilangan.py` | Mematikan satu unit di tengah beban lalu menghitung tugas yang lenyap |
| `diagram/kelas-ruang.puml` | Diagram kelas kedua versi, unit, ruang, dan penulis data |
| `diagram/sekuens-ruang.puml` | Diagram urutan satu tugas yang sama pada kedua versi |
| `diagram/buat_diagram.sh` | Menghasilkan ulang kedua diagram menjadi PDF di `figures/` |

Venv disiapkan sekali dengan `bash sources/siapkan_venv.sh` dari akar
repositori, lalu diaktifkan dengan `source .venv/bin/activate`. Langkah
lengkapnya ada di `sources/README.md`. Bab ini hanya memakai pustaka standar
Python.

Seluruh skrip dijalankan dari direktori ini. Mulai dengan `python unit.py ruang
4` untuk menjalankan satu beban penuh memakai empat unit, lalu `python unit.py
basis 4` sebagai pembandingnya. Berkas `kurs.db` dibentuk ulang setiap kali
beban dijalankan, sehingga tidak perlu dibersihkan sendiri.

Skrip yang menyalakan proses wajib memanggil penjalannya dari dalam `if
__name__ == "__main__":`. Python 3.14 memakai forkserver sebagai cara baku
menyalakan proses anak, dan cara itu mengimpor ulang modul utama di setiap anak.

| Latihan | Masalah yang disasar | Berkas yang dipakai |
| --- | --- | --- |
| 1 | *Throughput scaling*, hasil per detik ketika *processing unit* ditambah | `ukur_hasil.py`, `unit.py` |
| 2 | *Stale read* akibat *replication lag* | `ukur_basi.py`, `ruang.py` |
| 3 | *Data loss*, transaksi yang lenyap ketika satu unit mati | `uji_kehilangan.py`, `unit.py` |

## Langkah eksperimen 1: *throughput scaling*

Yang diukur: tugas per detik kedua versi ketika jumlah *processing unit*
dinaikkan dari satu menjadi delapan, lima putaran tiap susunan.

1. Jalankan pengukurannya. Satu penjalanan penuh memakan beberapa menit.

   ```bash
   python ukur_hasil.py
   # Keluarannya: 1 basis data   319.1 tugas/detik  median 3.118 ms  terbesar   24.359 ms
   #              4 basis data   244.3 tugas/detik  median 4.153 ms  terbesar 1835.463 ms
   #              1 ruang       1307.7 tugas/detik  median 0.625 ms  terbesar    2.026 ms
   #              4 ruang       3594.1 tugas/detik  median 0.719 ms  terbesar    3.817 ms
   #              Ruang berbanding basis data pada 4 unit : 14.7 kali
   ```

2. Bandingkan kolom tugas per detik pada versi basis data. Angkanya tidak naik
   walaupun unitnya ditambah, sebab seluruh unit mengantre pada satu *file*.
3. Bandingkan kolom terbesar pada versi basis data, yaitu 24,359 ms pada satu
   unit melawan 1835,463 ms pada empat unit. Lonjakan itulah tanda antrean, dan
   median menyembunyikannya.
4. Ubah `JUMLAH_UNIT` pada `ukur_hasil.py` menjadi memuat 16, jalankan ulang,
   lalu catat apakah hasilnya masih naik. Kembalikan nilainya sesudah dicatat.

## Langkah eksperimen 2: *stale read*

Yang diukur: berapa bagian pembacaan kurs yang memakai nilai kedaluwarsa pada
beberapa *replication lag*.

1. Jalankan pengukurannya.

   ```bash
   python ukur_basi.py
   # Keluarannya:   0 ms  11048 pembacaan      0 stale read   0.0%
   #               10 ms  11029 pembacaan   1034 stale read   9.4%
   #               25 ms  11046 pembacaan   2519 stale read  22.8%
   #               50 ms  11067 pembacaan   1052 stale read   9.5%
   #              200 ms  11056 pembacaan   8564 stale read  77.5%
   ```

2. Perhatikan baris 50 ms. Bagian basinya lebih kecil daripada baris 25 ms,
   sebab jedanya sama persis dengan jarak terbit kurs, sehingga penyegaran
   selalu tiba sesaat sesudah kurs baru terbit.
3. Ubah `JEDA_PEMBARUAN` dari 0,05 menjadi 0,02 detik, jalankan ulang, lalu
   catat perubahan bagian basinya. Kembalikan nilainya sesudah dicatat.

## Langkah eksperimen 3: *data loss*

Yang diukur: berapa tugas yang lenyap ketika satu unit dimatikan dengan SIGKILL
pada separuh beban.

1. Jalankan percobaannya.

   ```bash
   python uji_kehilangan.py
   # Keluarannya: Median tugas hilang, versi basis data : 1 tugas (3,000 transaksi)
   #              Median tugas hilang, versi ruang      : 28 tugas (84,000 transaksi)
   #              Range tugas hilang, versi ruang       : 15 sampai 41 tugas
   ```

2. Buka `unit.py`, lalu tunjukkan baris yang menentukan kapan penyangga
   dikirim, yaitu `UKURAN_KELOMPOK` beserta `JEDA_KIRIM`.
3. Ubah `UKURAN_KELOMPOK` dari 50 menjadi 1, jalankan ulang, lalu catat tugas
   yang hilang. Satu kali percobaan nyata turun menjadi 1 tugas pada kelima
   putaran, sama dengan versi basis data.
4. Jalankan `python ukur_hasil.py` dengan ukuran kelompok satu itu, lalu catat
   hasilnya pada empat unit. Satu kali percobaan nyata menghasilkan 3366,2 tugas
   per detik, sedangkan ukuran kelompok lima puluh menghasilkan 3594,1.
   Kembalikan nilainya sesudah dicatat.

## Menghasilkan ulang diagram

Kedua diagram UML dibuat dari *file* `.puml` di `diagram/`, dan hasilnya
tersimpan sebagai PDF di `figures/`.

```bash
bash sources/chapter08/diagram/buat_diagram.sh
pdffonts figures/kelas-ruang.pdf
# Keluarannya memuat TitilliumWeb-Regular dan TitilliumWeb-Bold
```

Contoh Java pada `java-example/` dan contoh Rust pada `rust-example/` adalah
kode lama yang disimpan sebagai pembanding lintas bahasa. Keduanya tidak dipakai
pada latihan.
