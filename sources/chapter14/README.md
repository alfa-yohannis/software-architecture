# Sumber Bab 14: Serverless

Satu penjalan fungsi kecil yang memuat modul fungsi ketika peristiwanya datang,
menyimpan objeknya selama masih hangat, lalu melepasnya sesudah diam melewati
batas. Perilaku itu meniru tiga fase daur hidup AWS Lambda, yaitu `Init`,
`Invoke`, dan `Shutdown`, beserta kemampuan turun ke nol. Pembandingnya sebuah
layanan yang hidup terus dan menyiapkan seluruh penangannya sekali di awal.

Seluruh berkas berjalan di satu laptop dengan pustaka standar Python saja. Tidak
ada akun awan, tidak ada Docker, dan tidak ada layanan luar yang dibutuhkan.

Ketiga fungsi berada di direktori `fungsi/`, masing-masing sebagai satu modul
beserta satu berkas manifes. Manifes disimpan terpisah dari modulnya agar
penjalan dapat membaca daftar peristiwa tanpa mengimpor kodenya, dan pemisahan
itulah yang membuat turun ke nol mungkin. Kunci `memori_mb` pada manifes meniru
pengaturan memori per fungsi pada Lambda, lalu dipakai untuk menghitung gigabita
detik.

| Berkas | Kegunaan |
| --- | --- |
| `kontrak.py` | Kontrak `Fungsi` beserta kunci wajib manifesnya |
| `domain.py` | Tabel kurs dan lapisan tarif pajak, dipakai bersama ketiga fungsi |
| `pendaftar.py` | Registri manifes, membaca daftar peristiwa tanpa mengimpor modul |
| `penjalan.py` | Penjalan fungsi, mengurus fase Init, Invoke, Shutdown, dan kolam contoh |
| `layanan_hidup.py` | Pembanding yang hidup terus dan menyebut ketiga nama fungsinya |
| `fungsi/fungsi_kurs.py` | Kelas `FungsiKurs`, peristiwa `kurs`, persiapan ringan |
| `fungsi/fungsi_pesanan.py` | Kelas `FungsiPesanan`, peristiwa `pesanan`, state hanya hidup selama hangat |
| `fungsi/fungsi_pajak.py` | Kelas `FungsiPajak`, peristiwa `pajak`, menyusun tabel 200.001 baris saat Init |
| `ukur_mulai.py` | Dua ratus panggilan per fungsi, memisahkan latensi mulai dingin dari mulai hangat |
| `ukur_sumber_daya.py` | Memori dan waktu saat menganggur, lalu hitungan gigabita detik |
| `ukur_lonjakan.py` | Dua belas permintaan serentak, mencatat contoh yang dibuat dan yang menunggu |
| `ukur_perubahan.py` | Biaya menambah satu fungsi baru pada kedua jalur, dihitung sebagai berkas dan baris |
| `diagram/kelas-serverless.puml` | Diagram kelas penjalan, pendaftar, dan ketiga fungsinya |
| `diagram/sekuens-serverless.puml` | Diagram urutan satu pemanggilan dingin dibanding satu pemanggilan hangat |
| `diagram/buat_diagram.sh` | Menghasilkan kedua diagram menjadi PDF di `figures/` |

Venv disiapkan sekali dengan `bash sources/siapkan_venv.sh` dari akar
repositori, lalu diaktifkan dengan `source .venv/bin/activate`. Langkah
lengkapnya ada di `sources/README.md`.

Seluruh skrip dijalankan dari direktori ini. Mulai dengan `python penjalan.py`
untuk melihat satu contoh fungsi lahir, dipakai ulang, lalu dilepas kembali.

| Latihan | Masalah yang disasar | Berkas yang dipakai |
| --- | --- | --- |
| 1 | Selisih latensi mulai dingin dan mulai hangat ditakar terhadap ragamnya | `ukur_mulai.py`, `fungsi/fungsi_kurs.py` |
| 2 | Akibat persiapan berat dan tagihan gigabita detik pada beban rendah | `ukur_sumber_daya.py`, `fungsi/fungsi_pajak.py` |
| 3 | Lonjakan serentak, jumlah contoh fungsi, dan permintaan yang menunggu | `ukur_lonjakan.py`, `layanan_hidup.py` |

Skrip `ukur_perubahan.py` dipakai di luar ketiga latihan, yaitu untuk
memperlihatkan bahwa penjalan tidak menyebut satu nama fungsi pun, sedangkan
layanan hidup menyebutnya pada dua baris untuk setiap fungsi.

Kode Java lama ada di `java/`, yaitu contoh penangan bergaya AWS Lambda beserta
pemanggilnya. Kode itu disimpan sebagai bahan pembanding lintas bahasa dan tidak
dipakai pada latihan bab ini.
