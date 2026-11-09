# Checklist buku referensi: Arsitektur Perangkat Lunak Terukur

Status per 9 November 2026, untuk naskah di `module/software-architecture.tex`.

Naskah ini disiapkan sebagai **buku referensi** yang **juga dapat digunakan
sebagai buku ajar** mata kuliah IF231303 Arsitektur Perangkat Lunak. Satu
terbitan hanya dinilai pada satu kategori angka kredit, sehingga pengajuannya
memakai kategori buku referensi. Pernyataan itu tercetak di sampul, halaman
hak cipta, Prakata, dan seksi Penggunaan sebagai Buku Ajar pada Pendahuluan.

Naskah tidak dipecah menjadi dua edisi seperti `advanced-web-engineering`.
Seluruh bab tetap memuat Tujuan Pembelajaran, *Summary*, dan Latihan, lalu
Pendahuluan menjelaskan bagian mana yang melayani pembaca rujukan dan bagian mana
yang melayani kelas.

## Syarat buku referensi

Definisi buku referensi pada PO PAK 2019 bersifat positif: ber-ISBN, satu
bidang ilmu sesuai kompetensi penulis, dan memenuhi ciri karya ilmiah utuh.

- [x] Satu bidang ilmu sesuai kompetensi penulis, yaitu arsitektur perangkat
  lunak di dalam rekayasa perangkat lunak
- [x] Mencakup beberapa topik dalam bidang itu, yaitu empat belas gaya pada
  Bab 1 sampai Bab 14, sehingga berbeda dari monograf
- [x] Rumusan masalah bernilai kebaruan, ada di Pendahuluan, tiga pertanyaan
- [x] Metodologi pemecahan masalah, ada di Pendahuluan seksi Metode
  Penyusunan, enam langkah ditambah tabel lingkungan pengukuran
- [x] Dukungan data, yaitu angka pengukuran nyata dari program yang disertakan
  di `sources/`
- [ ] Dukungan teori mutakhir dari karya ilmiah. Dari 67 entri yang dikutip,
  baru 3 artikel jurnal dan 5 makalah prosiding, sedangkan 46 berupa
  dokumentasi dan halaman web. Sasarannya dua sampai tiga karya ilmiah per bab
  yang membahas hal yang sama
- [x] Kesimpulan, ada di Penutup: sintesis, jawaban atas rumusan masalah,
  kontribusi, keterbatasan, dan arah pengembangan
- [x] Daftar pustaka
- [x] Naskah tidak berasal dari disertasi atau tesis penulis. Naskah tumbuh
  dari bahan mata kuliah, dan repositorinya dimulai Januari 2023
- [x] Tebal 315 halaman PDF, yaitu 40 halaman bagian awal termasuk sampul dan
  275 halaman bernomor arab, jauh di atas 40 halaman cetak format UNESCO pada
  PO PAK 2019 dan 49 halaman yang disyaratkan Perpusnas untuk ISBN
- [x] Ditulis satu kolom
- [ ] ISBN
- [ ] Nama penerbit, tahun terbit, editor, desainer sampul, penata letak, dan
  pemegang hak cipta. Tempatnya sudah disiapkan dan ditandai merah lewat makro
  `\isian{}` pada `halamanjudul.tex` dan `prakata.tex`
- [ ] Buku terbit dan beredar
- [ ] Ukuran cetak dipastikan ke penerbit. Naskah memakai B5, 17,6 x 25 cm,
  sedangkan sebagian panduan menyebut format UNESCO 15,5 x 23 cm

## Kegunaan sebagai buku ajar

- [x] Bahan pegangan mata kuliah IF231303 Arsitektur Perangkat Lunak, ditulis
  pengampunya
- [x] Tiap bab dibuka tiga butir Tujuan Pembelajaran
- [x] Tiap bab ditutup *Summary*
- [x] Bab 1 sampai Bab 14 masing-masing memuat tiga Latihan, seluruhnya 42,
  lengkap dengan perintah, keluaran nyata, tabel contoh terisi, lembar isian,
  dan pertanyaan analisis
- [x] Bab 15 berisi proyek akhir atas sistem Exim, dengan dua puluh pilihan
  judul
- [x] Slide per bab di `slides/sessionNN/` dan kode per bab di
  `sources/chapterNN/`

## Susunan naskah

- [x] Sampul memuat label Buku Referensi, judul, dan penulis, tanpa label
  "Modul Kuliah"
- [x] Judul *Arsitektur Perangkat Lunak Terukur*, tanpa subjudul. Judulnya
  tercetak di sampul, halaman judul, halaman hak cipta, dan metadata PDF.
  Nama mata kuliah IF231303 tetap Arsitektur Perangkat Lunak, sehingga slide
  yang menyebut mata kuliah itu tidak berubah
- [x] Arti kata terukur dijelaskan pada seksi Arti Kata Terukur di
  Pendahuluan: tiga syarat, satu analogi, dan lima contoh pada Tabel 1.
  Prakata dan Glosarium merujuk ke seksi itu
- [x] Halaman judul penuh dan halaman hak cipta, menurut Permendikbudristek
  22/2022 Lampiran III Tabel 1
- [x] Daftar isi, daftar gambar (63), daftar tabel (189), dan daftar listing
  (103)
- [x] Prakata
- [x] Pernyataan penggunaan kecerdasan artifisial
- [x] Pendahuluan, terpisah dari Prakata
- [x] Bab 1 sampai Bab 15, bernomor
- [x] Penutup tanpa nomor bab
- [x] Glosarium, 125 istilah, diturunkan dari kalimat definisi di babnya
- [x] Daftar pustaka berjudul Daftar Pustaka. Sebelumnya babel mencetaknya
  sebagai Bibliografi
- [x] Indeks subjek, 157 penanda untuk 118 entri, dipasang pada kemunculan
  pertama tiap istilah kunci di setiap bab
- [x] Riwayat penulis, menurut Permendikbudristek 22/2022 Lampiran III Tabel 3

## Catatan teknis

- [x] Urutan kompilasi: `xelatex`, `bibtex`, `makeindex`, lalu `xelatex` dua
  kali, seluruhnya dari direktori `module/`
- [x] Nol `Overfull`, nol rujukan yang tidak terdefinisi, dan nol tujuan
  hyperref ganda
- [x] Halaman sampul, halaman judul, hak cipta, daftar, Prakata, Pendahuluan,
  Penutup, Glosarium, Daftar Pustaka, Indeks, dan Riwayat Penulis dirender
  pada 65 dpi lalu diperiksa dengan mata
- [x] Halaman kosong sebelum bab tidak lagi mencetak nomor halaman, termasuk
  sisi belakang sampul, lewat paket `emptypage`
- [x] Tabel Pendahuluan bernomor 1 sampai 4, dan tabel Penutup melanjutkannya
  sebagai Tabel 5, bukan Tabel 15.14
- [x] Penanda indeks tidak berada di dalam listing, tabel, gambar, caption,
  judul seksi, komentar, maupun argumen perintah lain. Penanda yang semula
  jatuh di dalam `\textbf{}` dipindah ke luar, sebab di sana entrinya tertulis
  berbeda dan muncul ganda di indeks
- [x] Kata "port" pada Bab 11 dan Bab 13 berarti nomor port jaringan, sehingga
  tidak diindeks. Kata "fan-out" pada Bab 15 berarti jumlah modul yang
  diimpor, sehingga juga tidak diindeks
- [x] Lima kalimat yang menyebut naskah sebagai "modul ini" kini menyebut
  "buku ini", empat di Bab 1 dan satu di Bab 15
- [x] Slide tidak lagi menyebut naskah sebagai modul. Sebelas kalimat di Sesi 1,
  4, 5, 6, 7, 8, 9, 13, dan 14 kini menyebut buku, misalnya "ada di buku,
  Bab 6". Kata modul yang berarti modul Python tetap, sebab kode dan tabel di
  slide wajib sama dengan babnya. Kesembilan dek terkompilasi tanpa Overfull,
  dan sebelas bingkai yang berubah diperiksa dengan mata
- [x] Pembungkus uji `uji-babNN.tex` tetap terkompilasi, sebab `\index` milik
  LaTeX tidak berbuat apa-apa tanpa `\makeindex`

## Yang masih perlu dikerjakan

1. Pustaka diperkuat dengan artikel jurnal dan makalah prosiding, dua sampai
   tiga per bab. Setiap tautan diperiksa sebelum dikutip.
2. Penerbit dipilih, lalu ISBN dan isian merah dilengkapi.
3. Penulis memastikan daftar alat pada Pernyataan Penggunaan Kecerdasan
   Artifisial. Riwayat repositori baru mencatat Claude.
4. Penulis memeriksa Pendahuluan, Penutup, dan Glosarium, sebab ketiganya
   ditulis baru.

## Sumber

Sumber berikut dipakai checklist repositori saudara. Isinya belum dibaca ulang
khusus untuk buku ini.

- [PO PAK 2019](https://kepegawaian.itera.ac.id/wp-content/uploads/2021/09/PO-PAK-2019_MULAI-BERLAKU-APRIL-2019-1.pdf),
  definisi dan syarat buku referensi
- Kepmendiktisaintek 63/M/KEP/2025, angka kredit: buku referensi 40, buku ajar
  20, masing-masing satu buku per tahun. Dibaca lewat OCR dan dicatat di
  `TODO.md` repositori `advanced-web-engineering` pada 9 November 2026
- [Kepmendiktisaintek 39/M/KEP/2026](https://lldikti3.kemdiktisaintek.go.id/wp-content/uploads/2026/03/Salinan-Kepmendiktisaintek-39MKEP2026_Juknis-Layanan-Pengembangan-Profesi-dan-Karier-Dosen.pdf),
  petunjuk teknis layanan pengembangan profesi dosen
- [Permendikbudristek 22/2022](https://peraturan.bpk.go.id/Download/219102/Salinan%20permendikbudristek%20nomor%2022%20tahun%202022.pdf),
  susunan bagian awal dan bagian akhir buku
- [Informasi ISBN Perpusnas](https://isbn.perpusnas.go.id/landing_page/isbn_info),
  syarat pengajuan ISBN
