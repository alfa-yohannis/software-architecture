# Sumber Bab 7: Peer-to-Peer

Satu jaringan *node* pencari kurs yang dibangun tiga kali dengan kerangka yang
sama, lalu diadu memakai bahan *lookup* yang sama persis. Domainnya sama dengan
Bab 2 dan Bab 4, yaitu pasangan mata uang, sehingga yang dibandingkan hanya cara
menemukan nilai kursnya.

*Node*-nya berupa objek di dalam satu proses, bukan proses terpisah lewat soket.
Yang diukur adalah jumlah *message* dan jumlah *hop*, bukan waktu, sehingga ragam
penjadwalan sistem operasi hanya akan mengotori angkanya tanpa mengubah satu pun
kesimpulan. Sebagai gantinya, setiap perpindahan *message* dihitung satu per satu.

Nilai kursnya diambil apa adanya dari Kurs Transaksi Bank Indonesia tanggal
18 September 2026, yaitu nilai tengah antara kurs jual dan kurs beli.

| *File* | Kegunaan |
| --- | --- |
| `domain.py` | Tabel 26 key kurs beserta nilainya, dipakai ketiga susunan |
| `jaringan.py` | Kerangka bersama, yaitu kelas `LookupResult`, `Node`, dan `Network` |
| `indeks.py` | Susunan client-server, satu *node* indeks yang tahu semua |
| `tetangga.py` | Susunan *unstructured*, *query flooding* dengan batas *hop* |
| `cincin.py` | Susunan *structured*, *identifier ring* beserta *finger table* ala Chord |
| `susunan.py` | Pemilih susunan beserta peragaan satu kali *lookup* |
| `sebaran.py` | Median, persentil ke-95, dan nilai terbesar sederet angka |
| `uji_perpindahan.py` | Mencacah key yang berpindah pemilik pada tiga cara penempatan ketika satu *node* bergabung |
| `uji_pencarian_sebagian.py` | Menguji pertanyaan yang hanya menyebut sebagian nama key |
| `ukur_pencarian.py` | Dua ratus *lookup*, melaporkan sebaran *message* dan *hop* |
| `uji_ketahanan.py` | Mematikan satu *node* bergiliran, mencacah *lookup* yang terjawab |
| `ukur_penskalaan.py` | Menggandakan jumlah *node* dari 8 ke 16, menimbang pertumbuhan *message* |
| `diagram/kelas-p2p.puml` | Sumber *class diagram*, hasilnya `figures/kelas-p2p.pdf` |
| `diagram/sekuens-p2p-unstructured.puml` | Sumber *sequence diagram* jalur *unstructured* |
| `diagram/sekuens-p2p-structured.puml` | Sumber *sequence diagram* jalur *structured* |
| `diagram/buat_diagram.sh` | Menghasilkan ulang kedua PDF diagram lewat SVG |

Venv disiapkan sekali dengan `bash sources/siapkan_venv.sh` dari akar
repositori, lalu diaktifkan dengan `source .venv/bin/activate`. Bab ini hanya
memakai pustaka standar Python, sehingga tidak ada pemasangan tambahan.

Seluruh skrip dijalankan dari direktori ini. Mulai dengan `python susunan.py
daftar` untuk melihat ketiga susunan berdampingan.

| Latihan | Masalah yang disasar | *File* yang dipakai |
| --- | --- | --- |
| 1 | *Lookup cost*, *cost* satu *lookup* pada ketiga susunan | `ukur_pencarian.py`, `tetangga.py`, `cincin.py` |
| 2 | *Failure resilience*, *lookup* yang masih terjawab saat satu *node* mati | `uji_ketahanan.py`, `tetangga.py`, `cincin.py` |
| 3 | *Message scalability*, pertumbuhan *message* saat jumlah *node* digandakan | `ukur_penskalaan.py`, `ukur_pencarian.py` |

## Langkah eksperimen 1: *lookup cost*

Yang diukur: jumlah *message* dan jumlah *hop* pada dua ratus *lookup*, dengan
daftar peminta yang sama persis pada ketiga susunan.

1. Jalankan pengukurannya, lalu catat keenam angka sebaran tiap susunan.

   ```bash
   python ukur_pencarian.py
   # Keluarannya pada susunan unstructured: Message median   : 19.0
   #                                        Message terbesar : 20.0
   #                                        Hop median       : 2.0
   #                                        Lookup terjawab  : 200 dari 200
   # Keluarannya pada susunan structured:   Message median   : 4.0
   #                                        Message terbesar : 8.0
   #                                        Hop median       : 2.0
   ```

2. Bandingkan satu *lookup* yang sama lewat kedua jalur.

   ```bash
   python susunan.py cari tetangga EUR/IDR
   # Keluarannya: Jumlah message  : 20
   #              Jumlah hop      : 3
   python susunan.py cari cincin EUR/IDR
   # Keluarannya: Jumlah message  : 6
   #              Jumlah hop      : 3
   ```

3. Buka `tetangga.py`, lalu tunjukkan baris yang membuang pertanyaan berulang.
4. Ubah `BATAS_LOMPATAN` pada *file* itu dari empat menjadi dua, jalankan ulang
   `python ukur_pencarian.py`, lalu catat angkanya. Satu kali percobaan nyata
   menghasilkan *message* median 9,0 dan *lookup* terjawab 176 dari 200. Kembalikan
   angkanya sesudah dicatat.

## Mengapa *identifier ring* dipakai

Letak key dapat dihitung tanpa *ring*, yaitu dengan sisa bagi jumlah *node*
atau dengan membagi ruang *identifier* menjadi blok sama lebar. Bedanya baru muncul
ketika jumlah *node* berubah, dan selisih ketiganya dapat dicacah.

```bash
python uji_perpindahan.py
# Keluarannya: Jumlah node                : 8 lalu 9
#              Jumlah key                 : 26
#              Pindah pemilik, sisa bagi  : 26 (100.0 persen)
#              Pindah pemilik, bagi rata  : 9 (34.6 persen)
#              Pindah pemilik, ring       : 1 (3.8 persen)
python uji_perpindahan.py 16 17
# Keluarannya: Pindah pemilik, sisa bagi  : 24 (92.3 persen)
#              Pindah pemilik, bagi rata  : 13 (50.0 persen)
#              Pindah pemilik, ring       : 2 (7.7 persen)
```

Setiap key yang berpindah berarti satu pemindahan data antar *node*, sehingga
cara sisa bagi memindahkan hampir seluruh data setiap kali satu *node*
bergabung.

## Mengapa *query flooding* masih dipakai

Pertanyaan sehari-hari sering hanya menyebut sebagian nama, misalnya seluruh
key yang memuat USD. Susunan *structured* tidak dapat menjawabnya lewat satu
*lookup*, sebab letak key dihitung dari hash nama yang lengkap.

```bash
python uji_pencarian_sebagian.py
# Keluarannya: Potongan nama dicari       : USD
#              Key yang memuatnya         : 1 dari 26
#              Client-server ketemu       : 1 (2 message)
#              Unstructured ketemu        : 1 (14 message)
#              Structured ketemu          : 0 (2 message)
```

Susunan *unstructured* menjawab sebab setiap *node* memindai titipannya sendiri,
dan kemampuan itu tidak menuntut siapa pun memegang daftar.

## Langkah eksperimen 2: *failure resilience*

Yang diukur: berapa persen *lookup* yang masih terjawab ketika satu *node*
keluar dari jaringan, dengan setiap *node* bergiliran menjadi yang mati.

1. Jalankan percobaannya, lalu catat kelima baris hasil tiap susunan.

   ```bash
   python uji_ketahanan.py
   # Keluarannya pada susunan client-server: Node 0 mati             : 0.0 persen
   #                                         Rata-rata satu node mati: 87.5 persen
   #                                         Terburuk satu node mati : 0.0 persen
   # Keluarannya pada susunan unstructured:  Terburuk satu node mati : 55.2 persen
   # Keluarannya pada susunan structured:    Terburuk satu node mati : 71.5 persen
   ```

2. Bandingkan baris rata-rata dengan baris terburuk pada susunan client-server.
   Rata-ratanya 87,5 persen, sedangkan terburuknya 0,0 persen, sebab tujuh dari
   delapan giliran memang tidak menghilangkan apa pun.
3. Cari *node* yang hanya punya satu *neighbor* beserta jumlah key yang
   dipegangnya.

   ```bash
   python tetangga.py
   # Keluarannya memuat: node 5 neighbor [1] key 6
   ```

4. Cari *node* yang dititipi key paling banyak pada susunan *structured*.

   ```bash
   python cincin.py
   # Keluarannya memuat: node 6 identifier 27881 finger [...] key 7
   ```

## Langkah eksperimen 3: *message scalability*

Yang diukur: pertumbuhan jumlah *message* ketika jumlah *node* digandakan, lalu
dibandingkan dengan dua pembanding, yaitu 2,00 kali bila tumbuh sebanding dengan
jumlah *node* dan 1,33 kali bila tumbuh sebanding dengan logaritmanya.

1. Jalankan pengukurannya, lalu catat kedua angka pembanding beserta
   pertumbuhan *message* tiap susunan.

   ```bash
   python ukur_penskalaan.py
   # Keluarannya: Pertumbuhan jumlah node    : 2.00 kali
   #              Pertumbuhan logaritmanya   : 1.33 kali
   # Keluarannya pada susunan unstructured: Pertumbuhan message : 1.84 kali
   # Keluarannya pada susunan structured  : Pertumbuhan message : 1.50 kali
   ```

2. Jalankan pengukuran yang sama pada jaringan 32 *node*, lalu catat median
   *message*-nya.

   ```bash
   python ukur_pencarian.py 32
   # Keluarannya pada susunan unstructured: Message median  : 52.0
   #                                        Lookup terjawab : 172 dari 200
   # Keluarannya pada susunan structured:   Message median  : 6.0
   #                                        Lookup terjawab : 200 dari 200
   ```

3. Catat berapa *lookup* yang tidak terjawab pada susunan *unstructured*, lalu
   jelaskan sebabnya dari batas *hop*-nya.

## Menghasilkan ulang diagram

Kedua diagram UML dibuat dari *file* `.puml` di `diagram/`, dan hasilnya
tersimpan sebagai PDF di `figures/`. Perintahnya dijalankan dari direktori mana
pun, dan membutuhkan PlantUML beserta `rsvg-convert`.

```bash
bash sources/chapter07/diagram/buat_diagram.sh
pdffonts figures/kelas-p2p.pdf
# Keluarannya memuat TitilliumWeb-Regular dan TitilliumWeb-Bold
```

Ruang *identifier* pada *ring*-nya enam belas bit. Ruang delapan bit sempat dicoba, lalu
ditinggalkan, sebab pada 32 *node* dua di antaranya jatuh pada *identifier*
sama lalu menyesatkan penelusuran tanpa satu pun tanda. Tabrakan seperti itu
sekarang dihentikan sebagai *error* oleh `periksa_pengenal_unik`.
