# Sumber Bab 10: CQRS dan Event Sourcing

Satu domain kecil, yaitu buku besar saldo dompet mahasiswa, ditulis tiga kali
dengan perilaku luar yang sama persis. Ketiganya menerima command yang sama,
menolak command yang sama, dan berakhir pada saldo yang sama. Yang berbeda
hanya cara menyimpannya.

Versi CRUD menimpa satu baris keadaan. Versi CQRS memisahkan write model dari
read model, lalu memperbarui read model lewat projection sesudah setiap command.
Versi event sourcing hanya menyimpan event, menghitung ulang keadaan
sekarang dari event itu, dan memakai snapshot agar penghitungan ulangnya
tidak selalu dimulai dari event pertama.

Seluruh *file* memakai pustaka standar Python, termasuk `sqlite3`, sehingga
tidak ada pemasangan tambahan. *File* basis datanya dibentuk ulang oleh
skripnya sendiri dan tidak ikut dilacak Git.

| *File* | Kegunaan |
| --- | --- |
| `domain.py` | Bentuk command, bentuk ringkasan, aturan bisnis, dan pembangkit command |
| `sebaran.py` | Median, persentil ke-95, nilai terbesar, dan rentang bagi seluruh skrip pengukuran |
| `versi_crud.py` | Satu tabel keadaan, command dan query memakai model yang sama |
| `versi_cqrs.py` | Write model terpisah dari read model, dijembatani projection |
| `versi_event.py` | Hanya event log beserta snapshot, keadaan dihitung ulang |
| `ukur_latensi.py` | Seratus command dan seratus query pada ketiga versi |
| `ukur_penghitungan_ulang.py` | Waktu menyusun ulang read model, dengan dan tanpa snapshot |
| `ukur_penyimpanan.py` | Besar *file* keadaan dibanding besar event log |
| `tanya_riwayat.py` | Dua pertanyaan riwayat yang diajukan kepada ketiga versi |
| `diagram/kelas-cqrs.puml` | Diagram kelas sisi command, event log, projection, dan sisi query |
| `diagram/sekuens-cqrs.puml` | Diagram urutan satu command lalu satu query pada versi CQRS dan CRUD |
| `diagram/buat_diagram.sh` | Menghasilkan ulang kedua diagram menjadi PDF di `figures/` |

Venv disiapkan sekali dengan `bash sources/siapkan_venv.sh` dari akar
repositori, lalu diaktifkan dengan `source .venv/bin/activate`. Langkah
lengkapnya ada di `sources/README.md`.

Seluruh skrip dijalankan dari direktori ini. Mulai dengan `python
versi_event.py` untuk melihat satu dompet berisi sembilan puluh lima event.

| Latihan | Masalah yang disasar | *File* yang dipakai |
| --- | --- | --- |
| 1 | *Write cost* dan *read cost* ketiga versi | `ukur_latensi.py`, ketiga *file* versi |
| 2 | *Replay cost* terhadap panjang *event log* | `ukur_penghitungan_ulang.py`, `versi_event.py` |
| 3 | *Temporal query* yang hanya terjawab oleh event | `tanya_riwayat.py`, ketiga *file* versi |

## Langkah eksperimen 1: *write cost* dan *read cost*

Yang diukur: biaya satu command dan biaya satu query pada ketiga versi,
seratus command disusul seratus query.

1. Jalankan pengukurannya. Satu penjalanan penuh selesai di bawah satu menit.

   ```bash
   python ukur_latensi.py
   # Keluarannya, baris saldo, tabel latensi, dan dua baris pembanding:
   # Saldo akhir ketiga versi            : 8425000 (sama)
   # Yang diukur       Median  Persentil-95  Terbesar
   # Tulis CRUD       28.0638       33.4099   38.7468
   # Tulis CQRS       56.2983       65.7894   98.8158
   # Tulis event      28.4599       41.4043   70.3732
   # Baca CRUD         0.0042        0.0252    0.0960
   # Baca CQRS         0.0074        0.0127    0.0335
   # Baca event        0.1776        0.2116    0.6033
   # Baca event lebih lambat             : 100 dari 100
   # Tulis CQRS lebih lambat             : 95 dari 100
   ```

2. Bandingkan ketiga baris tulis. Versi CQRS paling lambat, sebab satu
   command menuntut dua kali simpan ke cakram, sekali untuk write model dan
   sekali untuk read model. Angka mutlaknya ditentukan cakram, sebab setiap
   `commit` menunggu cakram selesai menulis.
3. Bandingkan baris `Range dibagi selisih` pada sisi tulis dan pada sisi
   baca. Pada sisi tulis *range*-nya 1,4 kali selisih yang dicari, sehingga
   selisihnya belum dapat disebut ada, sedangkan pada sisi baca *range*-nya
   hanya 0,2 kali selisihnya.
4. Ubah `JUMLAH_COMMAND` menjadi 500, jalankan ulang, lalu catat latensi baca
   versi event sourcing. Lognya menjadi lima kali lebih panjang, dan setiap
   query melipat seluruh log itu. Kembalikan nilainya sesudah dicatat.

## Langkah eksperimen 2: *replay cost*

Yang diukur: waktu menyusun ulang read model dari *event log* pada tiga
panjang log, dengan dan tanpa snapshot, seratus putaran tiap keadaan.

1. Jalankan pengukurannya. Penyusunan log seratus ribu event memakan waktu
   paling lama.

   ```bash
   python ukur_penghitungan_ulang.py
   # Keluarannya, tabel untuk log 100.000 event:
   # Log 100.000 event     Median  Persentil-95  Terbesar
   # Tanpa snapshot      231.5220      318.3880  320.2136
   # Dengan snapshot       0.8048        0.8671    1.1413
   # Snapshot mempercepat  : 287.7 kali
   # Saldo kedua jalur     : sama
   # Ukuran event log      : 6720.0 KiB
   ```

2. Bandingkan pertumbuhan kedua jalur. Jalur tanpa snapshot naik 105,6 kali
   ketika lognya seratus kali lebih panjang, sedangkan jalur bersnapshot naik
   1,4 kali, sebab event yang dilipatnya tetap 250 buah.
3. Perhatikan persentil ke-95 jalur tanpa snapshot pada seratus ribu event,
   yaitu 318,3880 ms atau 1,4 kali mediannya. Mematikan pemungut sampah
   dengan `gc.disable()` tidak menyempitkan ekor itu, sebab persentil ke-95
   tetap 316,79 ms, sehingga sumbernya bukan pemungut sampah.
4. Ubah `EVENT_SESUDAH_SNAPSHOT` menjadi 5.000, jalankan ulang, lalu catat
   angka jalur bersnapshot. Kembalikan nilainya sesudah dicatat.

## Langkah eksperimen 3: *temporal query*

Yang diukur: berapa dari dua pertanyaan riwayat yang dapat dijawab tiap versi.

1. Jalankan percobaannya.

   ```bash
   python tanya_riwayat.py
   # Keluarannya: event : 2132000 (melipat event sampai 2026-03-01 08:30:00)
   #              Pertanyaan terjawab CRUD  : 0 dari 2
   #              Pertanyaan terjawab CQRS  : 1 dari 2
   #              Pertanyaan terjawab event : 2 dari 2
   ```

2. Bandingkan jawaban versi event sourcing dengan baris `pembanding`, yang
   dihitung langsung dari daftar command tanpa menyentuh basis data.
3. Buka `versi_cqrs.py`, lalu tunjukkan bagian yang membuat pertanyaan kedua
   terjawab sedangkan pertanyaan pertama tidak. Projection-nya menyimpan pencacah
   perubahan, sedangkan nilai antaranya tetap tertimpa.
4. Tambahkan satu pertanyaan ketiga pada `tanya_riwayat.py`, misalnya berapa
   setoran terbesar, lalu catat versi mana saja yang perlu disunting agar dapat
   menjawabnya.

## Menghasilkan ulang diagram

Kedua diagram UML dibuat dari *file* `.puml` di `diagram/`, dan hasilnya
tersimpan sebagai PDF di `figures/`.

```bash
bash sources/chapter10/diagram/buat_diagram.sh
pdffonts figures/kelas-cqrs.pdf
# Keluarannya memuat TitilliumWeb-Regular dan TitilliumWeb-Bold
```

Skrip `ukur_penyimpanan.py` tidak dipakai latihan mana pun. Skrip itu
menghasilkan angka pada tabel ukuran *storage* di dalam naskah bab. Lamanya
bergantung pada cakram, sebab sepuluh ribu command disimpan dengan `commit`
tersendiri. Pada mesin pengukuran bab ini satu `commit` memakan sekitar 28 ms,
sehingga penjalanan penuhnya memakan sekitar sembilan belas menit.
