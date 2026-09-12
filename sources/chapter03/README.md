# Sumber Bab 3: Model-View-*

Satu aplikasi yang sama, yaitu konversi mata uang, ditulis dalam empat varian.
Logika bisnisnya dipakai bersama dari `domain.py`, sehingga perbandingan antar
varian hanya menguji susunan komponennya.

| Berkas | Kegunaan |
| --- | --- |
| `domain.py` | Aturan bisnis dan tabel kurs, dipakai bersama oleh keempat varian |
| `mvc_klasik.py` | Varian MVC klasik Smalltalk-80, Model memberi tahu observer lalu View menarik nilainya |
| `mvc.py` | Varian Model-View-Controller masa kini, Controller memerintah View menggambar |
| `mvp.py` | Varian Model-View-Presenter, View bersifat pasif dan tidak mengenal Model |
| `mvvm.py` | Varian Model-View-ViewModel, View mengikat diri pada properti yang dapat diamati |
| `mvi.py` | Varian Model-View-Intent, setiap tindakan menjadi Intent dan keadaan bersifat tetap |
| `periksa_mv.py` | Membaca kode tanpa menjalankannya, lalu melaporkan dependency setiap komponen pada kelima berkas varian |
| `uji_tanpa_antarmuka.py` | Menguji kelima berkas varian dengan cara yang paling sedikit menyentuh View |

Venv disiapkan sekali dengan `bash sources/siapkan_venv.sh` dari akar
repositori, lalu diaktifkan dengan `source .venv/bin/activate`. Keempat varian
memakai `tkinter`, yang pada Debian dan Ubuntu berada di paket `python3-tk`.
Langkah lengkapnya ada di `sources/README.md`.

| Latihan | Masalah yang disasar | Berkas yang dipakai |
| --- | --- | --- |
| 1 | Siapa mengenal siapa antar komponen | `periksa_mv.py` |
| 2 | Kemudahan pengujian tanpa antarmuka | `uji_tanpa_antarmuka.py` |
| 3 | Luas dampak satu change request | kelima berkas varian |

Direktori `java/` berisi versi Java dari materi yang sama, yaitu `currency-mvc`,
`currency-mvvm`, dan `mvc-mvp-mvvm`. Versi tersebut disimpan sebagai bahan
pembanding lintas bahasa dan tidak dipakai pada latihan.
