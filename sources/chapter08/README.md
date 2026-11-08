# Sumber Bab 8: Space-Based Architecture

Satu aplikasi pengisian rencana studi, dibuat dalam dua versi dengan aturan
bisnis yang sama persis. Setiap *request* berisi satu mahasiswa yang membaca
atau mengambil kuota satu kelas, dan kuota tidak boleh menjadi minus.

Pada versi basis data, setiap *processing unit* menjalankan satu transaksi
SQLite untuk setiap *request*, sehingga basis data berada di jalur setiap
*request*. Pada versi *space*, unit membaca dan mengubah sisa kuota di grid
memorinya sendiri, menitipkan perubahannya ke *data pump*, lalu *data writer*
yang menuliskannya ke SQLite di luar jalur *request*.

| *File* | Kegunaan |
| --- | --- |
| `domain.py` | Enam kelas beserta kuotanya, bentuk `Request`, dan aturan kuota tidak boleh minus |
| `basis_data.py` | `BasisData`, *system of record* di SQLite sekaligus jalur versi basis data |
| `grid.py` | `DataGrid` dan `SaluranReplikasi`, salinan kuota di memori unit beserta replikasinya |
| `middleware.py` | `MessagingGrid`, `Pencatat`, dan `DeploymentManager` |
| `pompa.py` | `DataPump` dan `DataWriter`, penulisan ke basis data di luar jalur *request* |
| `unit.py` | `ProcessingUnit` dan `UnitBasisData`, beserta jejak satu *request* |
| `sebaran.py` | Median, persentil ke-95, dan nilai terbesar bagi seluruh skrip pengukuran |
| `ukur_commit.py` | Harga satu *commit* SQLite pada pengaturan `FULL` dan `NORMAL` |
| `ukur_hasil.py` | *Throughput scaling* kedua versi pada satu sampai tujuh unit |
| `ukur_stale_read.py` | *Stale read* pada enam *replication lag* dan dua laju perubahan |
| `ukur_tabrakan.py` | *Data collision* nyata dibanding taksiran N × (UR² / S) × RL |
| `uji_kehilangan.py` | *Data loss* ketika satu dari empat unit dimatikan pada separuh beban |
| `diagram/` | Sumber PlantUML diagram kelas dan diagram urutan beserta skrip pembuat PDF |

Venv disiapkan sekali dengan `bash sources/siapkan_venv.sh` dari akar
repositori, lalu diaktifkan dengan `source .venv/bin/activate`. Bab ini hanya
memakai pustaka standar Python.

Seluruh skrip dijalankan dari direktori ini. Mulai dengan `python unit.py`
untuk melihat jejak satu *request* dari mahasiswa menekan simpan sampai
barisnya tersimpan. *File* `krs.db` dibentuk ulang oleh setiap skrip, sehingga
tidak perlu dibersihkan sendiri.

*Processing unit* pada `ukur_hasil.py` berjalan sebagai proses, bukan thread,
sebab penafsir Python bawaan masih memakai satu kunci global sehingga thread
tidak benar-benar berjalan berbarengan. Setiap unit dikunci pada satu prosesor
sendiri. Skrip yang menyalakan proses wajib memanggil penjalannya dari dalam
`if __name__ == "__main__":`, sebab Python 3.14 memakai forkserver sebagai cara
baku menyalakan proses anak.

| Latihan | Masalah yang disasar | *File* yang dipakai |
| --- | --- | --- |
| 1 | *Throughput scaling*, hasil per detik ketika unit ditambah | `ukur_hasil.py`, `unit.py` |
| 2 | *Stale read* dan *data collision* akibat *replication lag* | `ukur_stale_read.py`, `ukur_tabrakan.py`, `grid.py` |
| 3 | *Data loss*, jawaban yang lenyap ketika satu unit mati | `uji_kehilangan.py`, `unit.py` |

## Langkah eksperimen 1: *throughput scaling*

Yang diukur: *request* dijawab per detik dan tersimpan per detik kedua versi
ketika jumlah *processing unit* dinaikkan dari satu menjadi tujuh, sepuluh
putaran tiap keadaan, pada dua campuran beban.

1. Jalankan pengukurannya. Satu penjalanan penuh memakan sekitar dua menit.

   ```bash
   python ukur_hasil.py
   # Keluarannya, sebagian tabel beban seluruhnya mengambil:
   # Unit Keadaan                Dijawab/detik  Tersimpan/detik  Lama jawab ms
   #    1 basis data                    9194.9           9194.9          130.5
   #    1 space                        23450.0          14755.4           51.2
   #    7 basis data                    9872.9           9872.9          121.5
   #    7 space                        14674.6           9909.4           81.8
   #    7 space replikator             36404.5          10788.9           33.0
   ```

2. Bandingkan kolom dijawab per detik versi basis data. Angkanya hampir tidak
   naik walaupun unitnya ditambah, sebab seluruh unit berebut satu kunci tulis.
3. Bandingkan versi `space` dengan `space tanpa replikasi`. Pada dua unit atau
   lebih, replikasi yang dikirim unit sendiri membuatnya 2,7 sampai 3,2 kali
   lebih lambat, sedangkan `space replikator` naik sampai 36.404,5 per detik
   pada tujuh unit.
4. Perhatikan kolom tersimpan per detik versi `space`. Angkanya berkisar
   sepuluh sampai lima belas ribu baris per detik berapa pun jumlah unitnya,
   sebab penulisnya hanya satu *data writer*.

## Langkah eksperimen 2: *stale read* dan *data collision*

Yang diukur: selisih kuota yang terbaca unit lain selama *replication lag*,
lalu tabrakan nyata dibanding taksiran rumus Richards dan Ford.

1. Jalankan kedua pengukurannya.

   ```bash
   python ukur_stale_read.py
   # Keluarannya, baris lag 100 ms pada jam pembukaan:
   #    100        910        479     100.0 %            48.0        49
   python ukur_tabrakan.py
   # Keluarannya, baris keadaan acuan:
   # acuan       5    100   50   200.0       800.0     222.0     400.0
   ```

2. Bandingkan selisih median pada lag 100 ms untuk kedua laju perubahan, yaitu
   48 kuota pada jam pembukaan dan 2 kuota pada hari biasa.
3. Perhatikan keadaan laju 400. Laju naik 1,97 kali, sedangkan tabrakan naik
   dari 222,0 menjadi 686,0 per detik, yaitu 3,1 kali.
4. Naikkan `LAJU_PERUBAHAN` pada `ukur_tabrakan.py` menjadi 800, jalankan
   ulang, lalu periksa apakah tabrakannya naik sekitar empat kali. Kembalikan
   nilainya sesudah dicatat.

## Langkah eksperimen 3: *data loss*

Yang diukur: *request* yang sudah dijawab lalu lenyap ketika satu dari empat
unit dimatikan pada separuh beban, sepuluh putaran tiap keadaan.

1. Jalankan percobaannya.

   ```bash
   python uji_kehilangan.py
   # Keluarannya, bagian bawah laporan:
   #                                   Basis data   Penyangga 1  Penyangga 50
   # Median hilang, request                   0.0           0.0          30.0
   # Terbesar hilang, request                   0             0            45
   # Putaran yang kehilangan            0 dari 10     0 dari 10    10 dari 10
   # Kiriman ke data pump, median               -          3000            61
   ```

2. Bandingkan kolom penyangga 50 dengan isi penyangga pada setiap putaran.
   Keduanya selalu sama, sebab yang lenyap persis isi penyangga unit yang mati.
3. Perhatikan harga penyangga 1, yaitu 3.000 kiriman alih-alih 61 dan waktu
   prosesor 1.211,5 ms alih-alih 1.012,7 ms.
4. Ubah `UKURAN_PENYANGGA_DICOBA` menjadi `(1, 10)`, jalankan ulang, lalu catat
   kehilangan beserta kirimannya. Kembalikan nilainya sesudah dicatat.

## Menghasilkan ulang diagram

Kedua diagram UML dibuat dari *file* `.puml` di `diagram/`, dan hasilnya
tersimpan sebagai PDF di `figures/`.

```bash
bash sources/chapter08/diagram/buat_diagram.sh
pdffonts figures/kelas-ruang.pdf
# Keluarannya memuat TitilliumWeb-Regular dan TitilliumWeb-Bold
```

Skrip `ukur_commit.py` tidak dipakai latihan mana pun. Skrip itu menjelaskan
mengapa `basis_data.py` memakai `synchronous=NORMAL`, yaitu satu *commit*
`FULL` memakan 9,3575 ms pada mesin pengukuran bab ini, sedangkan `NORMAL`
hanya 0,0091 ms.

Contoh Java pada `java-example/` dan contoh Rust pada `rust-example/` adalah
kode lama yang disimpan sebagai pembanding lintas bahasa. Keduanya tidak dipakai
pada latihan.
