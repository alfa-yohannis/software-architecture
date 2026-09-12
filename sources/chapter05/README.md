# Sumber Bab 5: Microkernel dan Plugin

Satu inti kecil yang tidak mengenal satu pun plugin, ditambah empat plugin yang
mendaftarkan dirinya lewat berkas manifes. Menambah kemampuan berarti menambah
dua berkas, yaitu modul dan manifesnya, tanpa menyunting inti sama sekali.

Manifes disimpan terpisah dari modulnya agar inti dapat membaca daftar perintah
tanpa mengimpor kodenya. Pemisahan itulah yang membuat aktivasi lambat mungkin,
sama seperti `package.json` pada Visual Studio Code dan `manifest.json` pada
Chrome.

| Berkas | Kegunaan |
| --- | --- |
| `kontrak.py` | Kontrak yang wajib dipenuhi plugin beserta kunci wajib manifesnya |
| `inti.py` | Inti microkernel, menemukan manifes lalu menjalankan perintah |
| `domain.py` | Tabel kurs dan fungsi hitung, dipakai bersama oleh plugin |
| `plugin_konversi.py` | Perintah `konversi`, menghitung satu nominal antar mata uang |
| `plugin_kurs.py` | Perintah `kurs`, menampilkan seluruh pasangan kurs |
| `plugin_riwayat.py` | Perintah `riwayat`, plugin yang ditambahkan pada Latihan 1 |
| `plugin_rusak.py` | Perintah `rusak`, sengaja gagal saat diimpor |
| `periksa_inti.py` | Membaca kode tanpa menjalankannya, melaporkan penyebutan plugin di dalam inti |
| `uji_isolasi.py` | Membandingkan nasib aplikasi dengan dan tanpa pembungkus galat |
| `ukur_aktivasi.py` | Seratus putaran, membandingkan aktivasi lambat dengan aktivasi awal |

Venv disiapkan sekali dengan `bash sources/siapkan_venv.sh` dari akar
repositori, lalu diaktifkan dengan `source .venv/bin/activate`. Langkah
lengkapnya ada di `sources/README.md`.

Seluruh skrip dijalankan dari direktori ini. Mulai dengan `python inti.py
daftar` untuk melihat plugin yang terpasang.

| Latihan | Masalah yang disasar | Berkas yang dipakai |
| --- | --- | --- |
| 1 | Menambah kemampuan tanpa menyentuh inti | `periksa_inti.py`, `plugin_riwayat.py` |
| 2 | Nasib aplikasi ketika satu plugin rusak | `uji_isolasi.py`, `plugin_rusak.py` |
| 3 | Biaya aktivasi awal dibanding aktivasi lambat | `ukur_aktivasi.py` |
