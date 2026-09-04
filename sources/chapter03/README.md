# Sumber Bab 3: Model-View-*

Satu aplikasi yang sama, yaitu konversi mata uang, ditulis dalam empat varian.
Logika bisnisnya dipakai bersama dari `domain.py`, sehingga perbandingan antar
varian hanya menguji susunan komponennya.

| Berkas | Kegunaan |
| --- | --- |
| `domain.py` | Aturan bisnis dan tabel kurs, dipakai bersama oleh keempat varian |
| `mvc.py` | Varian Model-View-Controller, View membaca Model secara langsung |
| `mvp.py` | Varian Model-View-Presenter, View bersifat pasif dan tidak mengenal Model |
| `mvvm.py` | Varian Model-View-ViewModel, View mengikat diri pada properti yang dapat diamati |
| `mvi.py` | Varian Model-View-Intent, setiap tindakan menjadi Intent dan keadaan bersifat tetap |
| `periksa_mv.py` | Membaca kode tanpa menjalankannya, lalu melaporkan ketergantungan setiap komponen |
| `uji_tanpa_antarmuka.py` | Menguji keempat varian dengan cara yang paling sedikit menyentuh View |

| Latihan | Masalah yang disasar | Berkas yang dipakai |
| --- | --- | --- |
| 1 | Siapa mengenal siapa antar komponen | `periksa_mv.py` |
| 2 | Kemudahan pengujian tanpa antarmuka | `uji_tanpa_antarmuka.py` |
| 3 | Luas dampak satu permintaan perubahan | keempat berkas varian |

Direktori `java/` berisi versi Java dari materi yang sama, yaitu `currency-mvc`,
`currency-mvvm`, dan `mvc-mvp-mvvm`. Versi tersebut disimpan sebagai bahan
pembanding lintas bahasa dan tidak dipakai pada latihan.
