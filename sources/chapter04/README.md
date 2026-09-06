# Sumber Bab 4: Ports and Adapters

Satu logika inti dipakai bersama oleh dua adapter penyimpanan yang berbeda.
Mengganti penyimpanan berarti mengganti satu baris pada `aplikasi.py`, tanpa
menyunting `domain.py` sama sekali.

| Berkas | Kegunaan |
| --- | --- |
| `domain.py` | Logika inti beserta port `SumberKurs`, tidak menyebut teknologi penyimpanan apa pun |
| `adapter_memori.py` | Adapter yang menyediakan kurs dari kamus di dalam memori |
| `adapter_sqlite.py` | Adapter yang menyediakan kurs dari berkas SQLite |
| `aplikasi.py` | Merangkai logika inti dengan salah satu adapter |
| `periksa_port.py` | Menghitung adapter yang disebut oleh `domain.py`, seharusnya nol |
| `uji_tanpa_basis_data.py` | Menguji logika inti memakai adapter tiruan, tanpa basis data |

Venv disiapkan sekali dengan `bash sources/siapkan_venv.sh` dari akar
repositori, lalu diaktifkan dengan `source .venv/bin/activate`. Langkah
lengkapnya ada di `sources/README.md`.

Seluruh skrip dijalankan dari direktori ini.

| Latihan | Masalah yang disasar | Berkas yang dipakai |
| --- | --- | --- |
| 1 | Kemandirian logika inti terhadap teknologi | `periksa_port.py` |
| 2 | Biaya penggantian adapter | `aplikasi.py`, kedua adapter |
| 3 | Pengujian tanpa infrastruktur | `uji_tanpa_basis_data.py` |

Direktori `java/` dan `go/` berisi versi lama dari materi yang sama dalam kedua
bahasa tersebut. Keduanya disimpan sebagai bahan pembanding lintas bahasa dan
tidak dipakai pada latihan.
