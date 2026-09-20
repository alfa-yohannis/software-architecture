# Sumber Bab 4: Ports and Adapters

Satu *core logic* dipakai bersama oleh tiga *adapter* yang berbeda. Mengganti
teknologi *storage* berarti mengganti pilihan pada `aplikasi.py`, tanpa
menyunting `domain.py` sama sekali.

Pilihan *adapter* terkumpul di `aplikasi.py`, yaitu *composition root*. Hanya
*file* itu yang mengenal seluruh *adapter*, sehingga nama teknologi tidak
tersebar ke mana-mana.

| Berkas | Kegunaan |
| --- | --- |
| `domain.py` | *Core logic* beserta *outbound port* `RateSource`, tidak menyebut teknologi *storage* apa pun |
| `adapter_memori.py` | `MemoryRateSource`, kurs penutupan hari sebelumnya dari *in-memory map* |
| `adapter_sqlite.py` | `SqliteRateSource`, kurs hari berjalan dari *file* SQLite |
| `aplikasi.py` | *Composition root*, merangkai *core logic* dengan salah satu *adapter* |
| `periksa_port.py` | *Automated check*, menghitung *adapter* yang disebut `domain.py`, seharusnya nol |
| `uji_tanpa_basis_data.py` | Tiga *unit test* memakai `StubRateSource`, tanpa basis data |
| `diagram/kelas-port-adapter.puml` | Sumber *class diagram*, hasilnya `figures/kelas-port-adapter.pdf` |
| `diagram/sekuens-port-adapter.puml` | Sumber *sequence diagram*, hasilnya `figures/sekuens-port-adapter.pdf` |
| `diagram/buat_diagram.sh` | Menghasilkan ulang kedua PDF diagram lewat SVG |

Venv disiapkan sekali dengan `bash sources/siapkan_venv.sh` dari akar
repositori, lalu diaktifkan dengan `source .venv/bin/activate`. Langkah
lengkapnya ada di `sources/README.md`. Bab ini hanya memakai pustaka standar
Python beserta SQLite yang sudah menyertainya.

Seluruh skrip dijalankan dari direktori ini. Mulai dengan `python aplikasi.py
memori` untuk melihat aplikasinya berjalan.

| Latihan | Masalah yang disasar | Berkas yang dipakai |
| --- | --- | --- |
| 1 | *Core independence* terhadap teknologi *storage* | `periksa_port.py`, `domain.py` |
| 2 | *Adapter swap cost* | `aplikasi.py`, kedua *adapter* |
| 3 | *Testing in isolation* | `uji_tanpa_basis_data.py` |

## Langkah eksperimen 1: *core independence*

Yang dibuktikan: `domain.py` tidak menyebut satu pun teknologi *storage*, dan
satu baris impor sudah cukup untuk menggugurkan klaim itu.

1. Jalankan pemeriksaannya, lalu catat baris `Adapter disebut`.

   ```bash
   python periksa_port.py
   # Keluarannya: Adapter disebut    : 0 []
   ```

2. Buka `domain.py`, lalu cari nama teknologi *storage* di dalamnya. Satu-satunya
   impor yang ada adalah `typing`, yang hanya dipakai untuk menuliskan bentuk
   *port*.
3. Tambahkan `import sqlite3` di puncak `domain.py`, lalu jalankan ulang
   perintah tadi. Angkanya berubah menjadi 1 dan baris terakhirnya menjadi
   `Klaim gagal`.
4. Batalkan penambahan tersebut, jalankan sekali lagi, lalu pastikan angkanya
   kembali 0.

## Langkah eksperimen 2: *adapter swap cost*

Yang diukur: berapa *file* dan baris yang berubah ketika teknologi *storage*
diganti.

1. Jalankan aplikasi dengan kedua *adapter*, lalu bandingkan hasilnya.

   ```bash
   python aplikasi.py memori
   # Keluarannya: memori: 100 USD = 1,625,000.00 IDR
   python aplikasi.py sqlite
   # Keluarannya: sqlite: 100 USD = 1,631,000.00 IDR
   ```

   Kedua angka itu berbeda sebab kurs yang disimpan kedua *adapter* memang
   berbeda hari. Perbedaannya berguna, sebab keluarannya langsung menunjukkan
   *adapter* mana yang terpasang.

2. Catat berapa *file* yang harus diubah untuk berpindah antara kedua *adapter*
   itu. Jawabannya nol, sebab pilihannya berupa argumen baris perintah, dan
   `domain.py` menjalankan baris yang sama pada kedua jalur.
3. Tulis *adapter* ketiga bernama `adapter_berkas.py` yang membaca kurs dari
   *file* teks biasa, misalnya `kurs.txt` yang tiap barisnya berisi kode asal,
   kode tujuan, dan nilainya.
4. Daftarkan *adapter* itu pada `pilih_sumber` di `aplikasi.py`, lalu jalankan
   `python aplikasi.py berkas` dan pastikan hasilnya sama.
5. Hitung *file* dan baris yang berubah. Satu kali pengukuran nyata menghasilkan
   2 *file* dan 29 baris, dan `domain.py` sama sekali tidak tersentuh.

## Langkah eksperimen 3: *testing in isolation*

Yang dibuktikan: *core logic* dapat diuji tanpa basis data, tanpa *file*, dan
tanpa jaringan.

1. Jalankan ketiga *unit test*-nya, lalu catat hasilnya.

   ```bash
   python uji_tanpa_basis_data.py
   # Keluarannya: hasil benar            lulus=True
   #              nominal nol ditolak    lulus=True
   #              kurs hilang ditolak    lulus=True
   #              Basis data yang disentuh: 0
   ```

2. Buka `uji_tanpa_basis_data.py`, lalu hitung jumlah baris kelas
   `StubRateSource`. Itulah seluruh biaya untuk menggantikan basis data.
3. Tambahkan satu *unit test* baru untuk nominal yang melewati
   `BATAS_KEWAJARAN_NOMINAL`, misalnya dua miliar, lalu pastikan `ValueError`
   yang muncul menyebut batasnya.
4. Hitung berapa kali seluruh *unit test* tersebut membuka koneksi basis data
   lewat `sqlite3.connect`, membaca *file* dari disk lewat `open`, atau membuka
   soket lewat `socket.connect`. Ketiganya nol.

## Menghasilkan ulang diagram

Kedua diagram UML dibuat dari berkas `.puml` di `diagram/`, dan hasilnya
tersimpan sebagai PDF di `figures/`. Perintahnya dijalankan dari direktori mana
pun, dan membutuhkan PlantUML beserta `rsvg-convert`.

```bash
bash sources/chapter04/diagram/buat_diagram.sh
pdffonts figures/kelas-port-adapter.pdf
# Keluarannya memuat TitilliumWeb-Regular dan TitilliumWeb-Bold
```

Direktori `java/` dan `go/` berisi versi lama dari materi yang sama dalam kedua
bahasa tersebut. Keduanya disimpan sebagai bahan pembanding lintas bahasa dan
tidak dipakai pada latihan.
