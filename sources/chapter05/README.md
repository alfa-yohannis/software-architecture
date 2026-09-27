# Sumber Bab 5: Microkernel dan Plugin

Satu *core* kecil yang tidak mengenal satu pun *plugin*, ditambah empat
*plugin* yang mendaftarkan dirinya lewat *file manifest*. Menambah kemampuan
berarti menambah dua *file*, yaitu modul dan *manifest*-nya, tanpa menyunting
*core* sama sekali.

Seluruh *plugin* berada di direktori `plugins/`, terpisah dari *core*, meniru
folder `plugins` pada Eclipse. *Manifest* disimpan terpisah dari modulnya agar
*core* dapat membaca daftar perintah tanpa mengimpor kodenya. Pemisahan itulah
yang membuat *lazy activation* mungkin, sama seperti `package.json` pada Visual
Studio Code dan `manifest.json` pada Chrome.

| Berkas | Kegunaan |
| --- | --- |
| `kontrak.py` | *Contract* yang wajib dipenuhi *plugin* beserta kunci wajib *manifest*-nya |
| `inti.py` | *Core* microkernel, menemukan *manifest* lalu menjalankan perintah |
| `domain.py` | Tabel kurs dan fungsi hitung, dipakai bersama oleh *plugin* |
| `plugins/plugin_konversi.py` | Kelas `ConversionPlugin`, perintah `konversi` |
| `plugins/plugin_kurs.py` | Kelas `RatePlugin`, perintah `kurs` |
| `plugins/plugin_riwayat.py` | Kelas `HistoryPlugin`, memanggil perintah lain lewat *core* |
| `plugins/plugin_rusak.py` | Kelas `BrokenPlugin`, modulnya sengaja gagal saat diimpor |
| `periksa_inti.py` | *Automated check*, melaporkan penyebutan *plugin* di dalam *core* |
| `uji_isolasi.py` | Membandingkan nasib aplikasi dengan dan tanpa *error handler* |
| `ukur_aktivasi.py` | Seratus putaran, membandingkan *lazy activation* dengan *eager activation* |
| `diagram/kelas-microkernel.puml` | Sumber *class diagram*, hasilnya `figures/kelas-microkernel.pdf` |
| `diagram/sekuens-aktivasi.puml` | Sumber *sequence diagram*, hasilnya `figures/sekuens-aktivasi.pdf` |
| `diagram/buat_diagram.sh` | Menghasilkan ulang kedua PDF diagram lewat SVG |

Venv disiapkan sekali dengan `bash sources/siapkan_venv.sh` dari akar
repositori, lalu diaktifkan dengan `source .venv/bin/activate`. Langkah
lengkapnya ada di `sources/README.md`. Bab ini hanya memakai pustaka standar
Python.

Seluruh skrip dijalankan dari direktori ini. Mulai dengan `python inti.py
daftar` untuk melihat *plugin* yang terpasang.

| Latihan | Masalah yang disasar | Berkas yang dipakai |
| --- | --- | --- |
| 1 | *Core independence*, menambah kemampuan tanpa menyentuh *core* | `periksa_inti.py`, `plugins/plugin_riwayat.py` |
| 2 | *Error isolation*, nasib aplikasi ketika satu *plugin* rusak | `uji_isolasi.py`, `plugins/plugin_rusak.py` |
| 3 | *Activation cost*, *eager* dibandingkan *lazy activation* | `ukur_aktivasi.py` |

## Langkah eksperimen 1: *core independence*

Yang dibuktikan: `inti.py` tidak menyebut satu pun nama modul maupun nama kelas
*plugin*, sehingga menambah kemampuan tidak mengubah satu baris pun di sana.

1. Jalankan *automated check*-nya, lalu catat kelima barisnya.

   ```bash
   python periksa_inti.py
   # Keluarannya: File core              : inti.py
   #              Manifest ditemukan     : 4
   #              Plugin disebut core    : 0 []
   #              Baris core             : 142
   #              Baris seluruh plugin   : 112
   #              Bagian plugin          : 44% dari kode yang dibaca
   ```

2. Salin `plugins/plugin_riwayat.py` beserta `plugins/plugin_riwayat.json`
   menjadi `plugin_pajak.py` dan `plugin_pajak.json`, lalu ubah nama kelas,
   nama perintah, dan kunci `modul` serta `kelas` pada *manifest*-nya.
3. Jalankan `python inti.py daftar`, lalu pastikan jumlah *plugin* terpasang
   bertambah menjadi lima tanpa menyunting `inti.py`.
4. Jalankan ulang pemeriksaannya, lalu bandingkan angkanya. Satu kali
   percobaan nyata menghasilkan *manifest* 5, *plugin* disebut *core* tetap 0,
   baris *core* tetap 142, baris *plugin* naik menjadi 147, dan bagian
   *plugin* naik dari 44 persen menjadi 51 persen.

## Langkah eksperimen 2: *error isolation*

Yang dibuktikan: satu *plugin* yang gagal saat diimpor tidak menjatuhkan
aplikasi, asalkan pemanggilannya dilindungi *error handler*.

1. Baca `plugins/plugin_rusak.py`, lalu tunjukkan baris pada tingkat modul yang
   menyebabkan kegagalannya.
2. Jalankan pembandingnya, lalu catat kedua barisnya.

   ```bash
   python uji_isolasi.py
   # Keluarannya: Dengan error handler : 3 perintah jalan, 1 dilewati
   #              Tanpa error handler  : 3 modul terimpor, lalu berhenti
   #              Penyebab berhenti    : plugins.plugin_rusak: ('JPY', 'IDR')
   ```

3. Jalankan kedua perintah berikut berurutan, lalu pastikan perintah kedua
   tetap dilayani sesudah yang pertama gagal.

   ```bash
   python inti.py rusak
   # Keluarannya: Dilewati: Plugin Rusak gagal dimuat: ('JPY', 'IDR')
   python inti.py kurs
   # Keluarannya: EUR -> IDR: 17,600.00
   #              SGD -> IDR: 12,100.00
   #              USD -> IDR: 16,250.00
   ```

4. Buka `inti.py`, temukan `try` pada metode `aktifkan`, hapus sementara
   *error handler* itu, lalu jalankan ulang `python inti.py rusak` dan catat
   akibatnya. Satu kali percobaan nyata berhenti dengan `KeyError: ('JPY',
   'IDR')`, sedangkan `python inti.py kurs` tetap menjawab seperti biasa,
   sebab *plugin* sehat tidak pernah menyentuh *error handler* itu.
   Kembalikan kodenya sesudah dicatat.

## Langkah eksperimen 3: *activation cost*

Yang diukur: selisih *startup time* antara *lazy activation* dan *eager
activation*, seratus putaran.

1. Jalankan pengukurannya. Baris kemajuan tercetak setiap sepuluh putaran.

   ```bash
   python ukur_aktivasi.py
   # Keluarannya: Median lazy activation       : 0,3988 ms
   #              Median eager activation      : 1,3380 ms
   #              Selisih median antar jalur   : 0,9391 ms
   #              Eager activation lebih lambat: 3,4 kali
   #              Range dalam jalur lazy       : 0,2579 ms
   #              Range dibagi selisih         : 0,3 kali (lazy)
   #              Putaran lazy lebih cepat     : 100 dari 100
   ```

2. Bandingkan baris *range* dengan baris selisih. Selisih baru layak disebut
   ada bila *range*-nya lebih kecil, dan di sini *range*-nya sepertiga
   selisihnya.
3. Buka `ukur_aktivasi.py`, lalu tunjukkan metode `bersihkan_cache` yang
   mengeluarkan modul *plugin* dari *import cache*.
4. Hapus sementara pemanggilan metode itu, jalankan ulang, lalu catat
   perubahan angkanya. Tanpa pembersihan, putaran kedua dan seterusnya hanya
   membaca cache, sehingga *eager activation* terlihat jauh lebih murah
   daripada sebenarnya. Kembalikan kodenya sesudah dicatat.

## Menghasilkan ulang diagram

Kedua diagram UML dibuat dari *file* `.puml` di `diagram/`, dan hasilnya
tersimpan sebagai PDF di `figures/`. Perintahnya dijalankan dari direktori mana
pun, dan membutuhkan PlantUML beserta `rsvg-convert`.

```bash
bash sources/chapter05/diagram/buat_diagram.sh
pdffonts figures/kelas-microkernel.pdf
# Keluarannya memuat TitilliumWeb-Regular dan TitilliumWeb-Bold
```

Mekanismenya sama dengan contoh Java pada `java-example/`, yang memuat setiap
*plugin* dari *file* JAR memakai `URLClassLoader` lalu `Class.forName`.
Padanannya di Python adalah `importlib.import_module` dan `getattr`.
