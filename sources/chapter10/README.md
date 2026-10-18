# Sumber Bab 10: CQRS dan Event Sourcing

Satu domain kecil, yaitu buku besar saldo dompet mahasiswa, ditulis tiga kali
dengan perilaku luar yang sama persis. Ketiganya menerima perintah yang sama,
menolak perintah yang sama, dan berakhir pada saldo yang sama. Yang berbeda
hanya cara menyimpannya.

Versi CRUD menimpa satu baris keadaan. Versi CQRS memisahkan model tulis dari
model baca, lalu memperbarui model baca lewat proyeksi sesudah setiap perintah.
Versi event sourcing hanya menyimpan event, menghitung ulang keadaan
sekarang dari event itu, dan memakai snapshot agar penghitungan ulangnya
tidak selalu dimulai dari event pertama.

Seluruh berkas memakai pustaka standar Python, termasuk `sqlite3`, sehingga
tidak ada pemasangan tambahan. Berkas basis datanya dibentuk ulang oleh
skripnya sendiri dan tidak ikut dilacak Git.

| Berkas | Kegunaan |
| --- | --- |
| `domain.py` | Bentuk perintah, bentuk ringkasan, aturan bisnis, dan pembangkit perintah |
| `sebaran.py` | Median, persentil ke-95, nilai terbesar, dan rentang bagi seluruh skrip pengukuran |
| `versi_crud.py` | Satu tabel keadaan, perintah dan kueri memakai model yang sama |
| `versi_cqrs.py` | Model tulis terpisah dari model baca, dijembatani proyeksi |
| `versi_event.py` | Hanya event log beserta snapshot, keadaan dihitung ulang |
| `ukur_latensi.py` | Seratus perintah dan seratus kueri pada ketiga versi |
| `ukur_penghitungan_ulang.py` | Waktu menyusun ulang model baca, dengan dan tanpa snapshot |
| `ukur_penyimpanan.py` | Besar berkas keadaan dibanding besar event log |
| `tanya_riwayat.py` | Dua pertanyaan riwayat yang diajukan kepada ketiga versi |
| `diagram/kelas-cqrs.puml` | Diagram kelas sisi perintah, event log, proyeksi, dan sisi kueri |
| `diagram/sekuens-cqrs.puml` | Diagram urutan satu perintah lalu satu kueri pada versi CQRS dan CRUD |
| `diagram/buat_diagram.sh` | Menghasilkan ulang kedua diagram menjadi PDF di `figures/` |

Venv disiapkan sekali dengan `bash sources/siapkan_venv.sh` dari akar
repositori, lalu diaktifkan dengan `source .venv/bin/activate`. Langkah
lengkapnya ada di `sources/README.md`.

Seluruh skrip dijalankan dari direktori ini. Mulai dengan `python
versi_event.py` untuk melihat satu dompet berisi sembilan puluh lima event.

| Latihan | Masalah yang disasar | Berkas yang dipakai |
| --- | --- | --- |
| 1 | *Write cost* dan *read cost* ketiga versi | `ukur_latensi.py`, ketiga berkas versi |
| 2 | *Replay cost* terhadap panjang *event log* | `ukur_penghitungan_ulang.py`, `versi_event.py` |
| 3 | *Temporal query* yang hanya terjawab oleh event | `tanya_riwayat.py`, ketiga berkas versi |

## Langkah eksperimen 1: *write cost* dan *read cost*

Yang diukur: biaya satu perintah dan biaya satu kueri pada ketiga versi,
seratus perintah disusul seratus kueri.

1. Jalankan pengukurannya. Satu penjalanan penuh selesai di bawah satu menit.

   ```bash
   python ukur_latensi.py
   # Keluarannya: Saldo akhir ketiga versi : 8425000 (sama)
   #              tulis CRUD   median 2.1958 ms  p95 2.6481  tbsr 3.2731
   #              tulis CQRS   median 4.6257 ms  p95 5.4658  tbsr 7.8009
   #              baca  event  median 0.3078 ms  p95 0.4598  tbsr 0.5240
   #              Tulis CQRS lebih lambat   : 99 dari 100
   ```

2. Bandingkan ketiga baris tulis. Versi CQRS paling lambat, sebab satu
   perintah menuntut dua kali simpan ke cakram, sekali untuk model tulis dan
   sekali untuk model baca.
3. Bandingkan baris `Rentang dibagi selisih` pada sisi tulis dan pada sisi
   baca. Pada sisi tulis rentangnya 1,3 kali selisih yang dicari, sehingga
   selisihnya belum dapat disebut ada, sedangkan pada sisi baca rentangnya
   hanya 0,1 kali selisihnya.
4. Ubah `JUMLAH_PERINTAH` menjadi 500, jalankan ulang, lalu catat latensi baca
   versi event sourcing. Lognya menjadi lima kali lebih panjang, dan setiap
   kueri melipat seluruh log itu. Kembalikan nilainya sesudah dicatat.

## Langkah eksperimen 2: *replay cost*

Yang diukur: waktu menyusun ulang model baca dari *event log* pada tiga
panjang log, dengan dan tanpa snapshot, seratus putaran tiap keadaan.

1. Jalankan pengukurannya. Penyusunan log seratus ribu event memakan waktu
   paling lama.

   ```bash
   python ukur_penghitungan_ulang.py
   # Keluarannya: Tanpa snapshot 100.000 event  : median 173.9364 ms
   #              Dengan snapshot 100.000 event : median   2.9440 ms
   #              Snapshot mempercepat          : 59.1 kali
   #              Saldo kedua jalur             : sama
   ```

2. Bandingkan pertumbuhan kedua jalur. Jalur tanpa snapshot naik 90,8 kali
   ketika lognya seratus kali lebih panjang, sedangkan jalur bersnapshot naik
   4,1 kali sebab indeksnya memang lebih dalam pada tabel yang lebih besar.
3. Perhatikan persentil ke-95 jalur tanpa snapshot pada seratus ribu event,
   yaitu 602,7324 ms atau 3,5 kali mediannya. Ekor itu datang dari pemungut
   sampah Python, sebab setiap putaran membuat seratus ribu objek `Ringkasan`.
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
   dihitung langsung dari daftar perintah tanpa menyentuh basis data.
3. Buka `versi_cqrs.py`, lalu tunjukkan bagian yang membuat pertanyaan kedua
   terjawab sedangkan pertanyaan pertama tidak. Proyeksinya menyimpan pencacah
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
menghasilkan angka pada tabel ukuran penyimpanan di dalam naskah bab, dan
berjalan sekitar dua sampai tiga menit sebab sepuluh ribu perintah disimpan ke
cakram satu per satu.
