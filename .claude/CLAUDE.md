# Aturan Penulisan Modul Arsitektur Perangkat Lunak

Aturan ini diekstrak dari `module/chapter02.tex`, yang menjadi bab acuan. Bab
lain ditulis mengikuti pola yang sama persis, sehingga seluruh modul terbaca
sebagai satu suara.

## 1. Bahasa

- Bahasa Indonesia baku. Tingkat bahasanya diarahkan ke mahasiswa awal tahun
  ketiga, sehingga keterbacaan didahulukan di atas istilah yang canggih.
- **Kalimat pendek, satu gagasan per kalimat.** Batas praktisnya 28 kata.
- **Kalimat majemuk setara maksimal tiga klausa.** Kalimat majemuk bertingkat
  maksimal dua tingkat. Bila lebih, kalimatnya dipecah.
- **Gunakan kata sambung** untuk menyambung gagasan: lalu, kemudian, sehingga,
  sebab, karena itu, namun, sedangkan, agar, bila.
- **Tanpa kata ganti orang.** Hindari "kami", "kita", "saya", dan sapaan
  "Anda". Naskah berbicara tentang sistem, bukan kepada orang. Pakai bentuk
  pasif atau frasa benda seperti "penelitian ini" dan "bab ini".
- **Tanpa tanda pisah panjang.** Em dash dan en dash dilarang. Ganti dengan
  koma, titik, atau tanda kurung.
- **Setiap singkatan dieja penuh saat pertama muncul di bab itu**, lalu dipakai
  singkatnya: "Structured Query Language (SQL)". Kode mata kuliah dan nama diri
  bukan singkatan, sehingga tidak perlu dieja.
- **Istilah asing yang belum punya padanan mapan ditulis miring**:
  `\textit{pipeline}`, `\textit{layered architecture}`, `\textit{stub}`.
  Istilah yang sudah diserap ditulis biasa: server, klien, data, latensi,
  median, persentil.
- **Jangan memaksakan terjemahan yang janggal.** Bila padanan Indonesianya
  terasa dibuat-buat, pakai istilah Inggrisnya dan cetak miring. Contoh yang
  dipakai apa adanya: *architectural style*, *benchmark*, *confusion matrix*,
  *hold-out set*, *message broker*, *coupling*, *framework*, *state*,
  *offline*, *stub*, *maintainability*, *scalability*.
- **Istilah yang sudah dipakai wajib konsisten di seluruh bab dan slide.**
  Yang sudah ditetapkan: *layer*, *closed layer*, *open layer*, *layer
  violation*, *pass-through*, *call stack*, *range*, *dependency*, *observer*,
  *binding*, *symptom*, *template*, *port*, *adapter*, *ports and adapters*,
  *inbound port*, *outbound port*, *inbound adapter*, *outbound adapter*,
  *core logic*, *core independence*, *adapter swap cost*, *testing in
  isolation*, *downward call flow*, *change containment*, *storage coupling*,
  *dependency inversion*, *falsifiable claim*, *composition root*, *data
  source*, *in-memory map*, *storage*, *file*, *error*, *behavior*, *call
  direction*, *class diagram*, *sequence diagram*, *unit test*, *automated
  check*, *trade-off*. Penggantian istilah dikerjakan sekaligus pada naskah,
  slide, kode, berkas `.puml`, README, dan label keluaran skrip. Diagram
  dibuat ulang dan skripnya dijalankan ulang pada penggantian yang sama.
- **Konsep yang padanan Indonesianya janggal ditulis dalam bahasa Inggris.**
  Kata seperti lapisan, berkas, galat, penyimpanan, kelakuan, dan pemeriksaan
  otomatis diganti *layer*, *file*, *error*, *storage*, *behavior*, dan
  *automated check*. Nama diri produk dan nama konsep yang sudah diserap tetap
  ditulis biasa.
- **Istilah Inggris yang baru muncul diberi glosa sekali**, lalu dipakai
  singkatnya: "klaim yang dapat dibuktikan salah, atau *falsifiable claim*".
- **Akhiran Indonesia pada istilah asing memakai tanda hubung**:
  `\textit{adapter}-nya`, `\textit{port}-nya`, bukan `\textit{adapter}nya`.
- Nama diri seperti Python, FastAPI, Redis, NATS, Docker, dan Pillow **tidak**
  dicetak miring, sesuai kaidah ejaan.
- Nama berkas, perintah, dan potongan kode inline memakai `\texttt{}`. Jalur
  berkas memakai `\berkas{}`.
- Garis bawah di luar `lstlisting` wajib di-escape: `\texttt{basis\_data.py}`.

### 1.1 Pola yang dihindari

Naskah tidak boleh terbaca seperti keluaran mesin. Yang sering muncul dan harus
dihindari:

- Pembukaan kalimat yang berulang, misalnya seluruh seksi dibuka dengan
  "Penelitian ini menghasilkan".
- Pola bernomor yang seragam di semua bab, misalnya "Tujuan pertama, Tujuan
  kedua, Tujuan ketiga" pada setiap bab tanpa perkecualian.
- Klaim kesenjangan yang diulang dengan kata yang sama persis, misalnya "belum
  pernah diukur" di setiap bab.
- Kelompok tiga yang dipaksakan, dan kalimat "bukan X melainkan Y" yang
  berlebihan.
- **Kata yang tidak dapat diperiksa.** Ganti dengan yang dapat dihitung atau
  disebut namanya. "Susunannya rapi" menjadi "susunan direktorinya tidak
  berubah dan seluruh *unit test* tetap lulus". "Menyentuh infrastruktur"
  menjadi "memanggil `sqlite3.connect`, membaca *file* dari disk lewat `open`,
  atau membuka soket lewat `socket.connect`". "Menghasilkan jawaban yang sama"
  menjadi "mengembalikan nilai bertipe sama seperti yang diminta *port*".
  "Klaim yang menyebut angka pasti" menjadi klaimnya itu sendiri beserta
  angkanya.
- **Analogi tidak diulang antar bab.** Satu analogi dipakai satu bab saja,
  sehingga stopkontak di Bab 4 tidak muncul lagi di bab lain.
- **Analogi harus tepat pemetaannya.** Bila *adapter* diibaratkan benda, benda
  itu harus benar-benar mengubah bentuk, misalnya adapter kaki tiga ke kaki
  dua, bukan colokan yang hanya menempel.

## 2. Struktur bab

Urutan seksi tetap, tanpa perkecualian:

1. `\section*{Tujuan Pembelajaran}` — tepat tiga butir, tiap butir berupa kata
   kerja terukur (Menjelaskan, Membedakan, Mengukur, Merancang), bukan
   "Memahami" atau "Mengetahui". Butir ketiga menyebut ketiga hal yang diukur
   pada latihan.
2. `\section{Pendahuluan}` — dua sampai tiga paragraf. Paragraf terakhir
   menyebut referensi utama bab tersebut dengan `\cite{}`.
3. Seksi materi, tiga sampai delapan buah.
4. `\section{Ringkasan}` — empat sampai lima paragraf naratif, bukan daftar
   berbutir. Paragraf terakhir menutup dengan pesan utama bab.
5. `\section{Latihan}` — tepat tiga latihan, lihat bagian 6.

**Tidak ada seksi Praktikum.** Kegiatan praktikum diwujudkan sebagai Latihan.

**Tidak ada bagian Outcome-Based Education.** Capaian pembelajaran cukup
dinyatakan sebagai Tujuan Pembelajaran tiga butir di awal bab.

## 3. Cara menjelaskan satu konsep

Pola tiga langkah, dipakai berulang:

1. **Pernyataan.** Satu paragraf berisi definisi dan cara kerjanya.
2. **Analogi sehari-hari.** Diambil dari dunia kampus atau kehidupan biasa:
   loket pembayaran uang kuliah, warung dengan satu kasir, surat pengantar yang
   melewati tiga meja, loket informasi. Analogi ditulis satu paragraf, lalu
   ditinggalkan. Tidak dipaksakan sepanjang seksi.
3. **Contoh konkret.** Diambil dari kode di `sources/chapterNN/`, disertai
   angka nyata.

**Setiap bab wajib memuat contoh, kasus, dan analogi.** Kasus berupa cerita
kegagalan atau keberhasilan yang masuk akal, ditulis sebagai rangkaian langkah,
lalu ditutup dengan akibatnya.

Transisi antarbagian memakai pertanyaan eksplisit yang langsung dijawab:

> Konsekuensi kedua itulah yang menimbulkan persoalan berikutnya. Pertanyaannya,
> apakah setiap permintaan benar-benar wajib melewati semua lapisan.

Setiap konsekuensi ditulis eksplisit dan dihitung: "Aturan ini punya dua
konsekuensi praktis. Pertama, ... Kedua, ...".

## 4. Ketepatan materi

- **Materi dicocokkan dengan rujukan sebelum ditulis.** Sumber primer lebih
  dahulu: buku acuan, spesifikasi resmi, dokumentasi lembaga. Blog dan tutorial
  tidak dipakai sebagai rujukan utama.
- **Contoh dunia nyata dicari, bukan dikarang.** Bila bab membutuhkan contoh
  informasi publik, cari yang benar-benar ada. Bab 2 memakai kurs referensi
  JISDOR dari Bank Indonesia, bukan contoh rekaan.
- **Aturan praktis yang tidak esensial tidak perlu dikutip.** Angka pegangan
  seperti perbandingan delapan puluh berbanding dua puluh dihapus, sebab
  angkanya tidak dapat diverifikasi pada latihan dan mengalihkan perhatian dari
  yang benar-benar diukur.

## 5. Gambar dan tabel

- Tiap seksi materi punya minimal satu gambar TikZ atau satu tabel.
- Gambar dibuat dengan TikZ, bukan gambar raster, kecuali tangkapan layar.
- **Diagram Unified Modeling Language (UML) dibuat dengan PlantUML**, yaitu
  diagram kelas dan diagram urutan. Sumbernya disimpan sebagai `.puml` di
  `sources/chapterNN/diagram/`, dikompilasi menjadi PDF ke `figures/` lewat
  skrip `buat_diagram.sh` di direktori yang sama, lalu disisipkan dengan
  `\includegraphics`. Berkas PDF hasilnya ikut dilacak agar modul tetap
  dapat dikompilasi tanpa memasang PlantUML. Diagram selain UML tetap memakai
  TikZ.
- **Fontnya Titillium Web**, sama dengan font naskah, dan warnanya mengikuti
  palet yang sama. Kotak catatan bawaan PlantUML berwarna kuning, sehingga
  `skinparam note` wajib diatur ke hijau.
- **Jalur PDF langsung tidak dipakai.** `plantuml -tpdf` tidak mengenali
  Titillium lalu menggantinya dengan Times tanpa peringatan. Skripnya
  menghasilkan SVG lebih dahulu, lalu mengubahnya dengan `rsvg-convert`, sebab
  jalur itu mencari font lewat fontconfig dan menanamkannya ke dalam PDF.
  Hasilnya diperiksa dengan `pdffonts`, dan nama fontnya harus muncul di sana.
- **Palet tetap dan berbasis hijau.** `blue!8` untuk kotak biasa, `green!10`
  untuk hasil akhir atau komponen yang ditekankan ringan, `praditagreen!15` dan
  `praditagreen!25` untuk simpul utama, `red!70` putus-putus untuk penanda jalur
  yang menyimpang. **Warna oranye tidak dipakai**, baik di modul maupun di
  slide, termasuk pada tema Beamer.
- Gaya panah tetap: `panah/.style={-{Stealth[length=2mm]}, thick}`.
- **Diagram kelas PlantUML digambar dari kiri ke kanan** memakai `left to right
  direction`, dengan sisi pemanggil di kiri, inti beserta kontraknya di tengah,
  dan pengisi kontrak di kanan. Bila arah panah menarik kotak ke sisi yang
  salah, tulis relasinya terbalik, misalnya `RateSource <-- MemoryRateSource`,
  sehingga arah panahnya tetap benar sedangkan letaknya berpindah.
- Font di dalam gambar `\scriptsize` atau `\footnotesize`, keterangan kecil
  memakai `{\tiny\mdseries ...}`.
- Tabel memakai `tabularx` selebar `\textwidth`, dengan `\hline` di **setiap**
  baris, termasuk sebelum baris judul dan sesudah baris terakhir.
- Tiap gambar dan tabel wajib punya `\caption` dan `\label`, dan wajib dirujuk
  dari naskah dengan `\ref{}` sebelum kemunculannya.
- Penamaan label: `fig:nama-pendek`, `tab:nama-pendek`, `lst:nama-pendek`.
  Tabel lembar isian latihan memakai pola `tab:latN-hasil`, contoh terisi
  memakai `tab:latN-contoh`.

### 5.1 Pemeriksaan tata letak wajib

Sebelum bab atau slide dinyatakan selesai, ketiganya diperiksa:

1. **Meluap.** Jumlah `Overfull` pada berkas log harus nol.
2. **Rujukan.** Tidak boleh ada `??` maupun `Reference undefined`. Jalankan
   `xelatex` dua kali, dan `bibtex` bila ada sitasi baru.
3. **Tumpang-tindih dan terpotong.** Peringatan tidak muncul untuk masalah ini,
   sehingga halaman **wajib dirender menjadi gambar lalu diperiksa dengan
   mata**: `pdftoppm -png -r 65 berkas.pdf keluaran`. Yang sering terjadi:
   label TikZ menabrak logo, tanggal sampul tertutup panel bawah, dan gambar
   melebihi lebar halaman B5.

## 6. Latihan

- **Tepat tiga latihan per bab**, dan ketiganya menyasar **tiga masalah yang
  berbeda**. Boleh memakai satu basis kode yang sama.
- Latihan diberi judul `\subsection*{Latihan N: Judul}`, bernomor urut dari 1
  dan konsisten dengan penomoran pada caption tabelnya.
- **Setiap latihan wajib punya listing perintahnya sendiri**, bukan perintah
  yang hanya disebut di dalam langkah kerja, dan listingnya memuat komentar
  `# Keluarannya:` berisi baris nyata yang harus dicatat mahasiswa.
- Tiap latihan berisi: kalimat pembuka yang menyebut apa yang dibuktikan,
  langkah kerja sebagai `enumerate`, listing perintah untuk menjalankannya,
  satu tabel contoh yang **sudah terisi**, dan satu tabel lembar isian kosong
  berisi `\dots`.
- Langkah kerja ditulis berurutan sesuai waktu pelaksanaan.
- Latihan ditutup dengan dua atau tiga pertanyaan analisis yang jawabannya
  menuntut pembacaan angka, bukan hafalan. Pertanyaan terakhir pada Latihan 3
  meminta mahasiswa menggabungkan hasil ketiga latihan menjadi satu keputusan.
- Disebutkan bahwa hasil tiap mahasiswa akan berbeda, dan yang dilaporkan
  adalah pola perbandingannya, bukan angka persisnya.

## 7. Pengukuran

- **Angka pada tabel contoh diambil apa adanya dari pengukuran nyata**,
  termasuk kejanggalannya, lalu kejanggalan itu dijelaskan sebabnya di paragraf
  sesudahnya.
- **Satu kali pengukuran tidak cukup.** Bila selisih yang dicari kecil,
  rancang pengukuran berulang, minimal seratus putaran, lalu laporkan berapa
  kali tiap pilihan menang. Perbandingan tiga kali terlalu sedikit untuk
  menyimpulkan apa pun.
- **Laporkan sebaran, bukan hanya rata-rata.** Median, persentil ke-95, dan
  nilai terbesar. Gejala antrean hanya terlihat pada nilai terbesar.
- **Bandingkan selisih dengan ragamnya.** Selisih yang lebih kecil daripada
  ragam pengukuran belum dapat disebut ada.
- Komentar `# Keluarannya:` di dalam skrip wajib disamakan dengan hasil
  eksekusi terakhir.
- **Label yang dicetak skrip memakai istilah yang sama dengan naskah**, sebab
  langkah latihan menyuruh mahasiswa mencatat baris keluaran itu. Bila
  istilahnya berubah di naskah, label skripnya ikut diubah.

## 8. Kode

- **Bahasa kode adalah Python** untuk seluruh contoh dan skrip pengukuran.
  Kode lama dalam bahasa lain disimpan di subdirektori `java/` atau `go/` di
  dalam `sources/chapterNN/`, sebagai bahan pembanding lintas bahasa, dan tidak
  dipakai pada latihan.
- **Kode dibuat sesederhana mungkin, tetapi cukup untuk menjelaskan konsep yang
  diajarkan.** Kesederhanaan bukan alasan menghilangkan bagian yang menjadi
  inti pelajaran.
- **Lapisan atau komponen yang diajarkan harus benar-benar bekerja.** Bila bab
  membahas lapisan bisnis, lapisan itu harus menuntut sesuatu yang nyata,
  misalnya autentikasi dan otorisasi. Fungsi yang hanya meneruskan panggilan
  boleh ada, tetapi harus disertai alasan mengapa memang tidak ada tuntutan
  bisnis di situ.

### 8.1 Aturan penulisan kode

- **Tanpa fungsi bersarang.** Seluruh fungsi berada di tingkat modul.
- **Setiap modul, kelas, dan fungsi wajib punya docstring yang berguna.**
  Docstring menjelaskan *mengapa* dan *apa akibatnya*, bukan mengulang nama
  fungsinya. Docstring modul menyebutkan kegunaan berkas dan cara
  menjalankannya. Docstring satu baris yang hanya menerjemahkan nama fungsi
  dianggap belum memadai, termasuk pada `__init__`.
- **Docstring menyebutkan apa yang dikembalikan**, misalnya "Mengembalikan dict
  berisi manifes yang lolos". Tipe kembaliannya juga ditulis pada tanda tangan
  fungsi bila membantu pembaca, misalnya `-> kontrak.Plugin`.
- **Nama menjelaskan isinya**, dalam bahasa Indonesia: `koneksi` bukan `c`,
  `daftar_kurs` bukan `dk`. Nama fungsi berupa kata kerja, nama variabel berupa
  kata benda. Nama harus lengkap, sehingga `sumber_kurs` dipakai, bukan
  `sumber`.
- **Nama kelas mengikuti istilah yang dipakai naskahnya.** Bila konsepnya
  ditulis dalam bahasa Inggris, nama kelasnya ikut Inggris, misalnya
  `RateSource`, `MemoryRateSource`, `SqliteRateSource`, dan `StubRateSource`.
  Nama fungsi, variabel, dan berkas tetap bahasa Indonesia.
- **Konstanta bernama menyebut batasnya, bukan sifatnya**, misalnya
  `BATAS_KEWAJARAN_NOMINAL`, dan pesan galatnya ikut menyebut angka itu.
- **Angka ajaib diberi nama** sebagai konstanta di puncak modul. Kueri SQL
  panjang juga diangkat menjadi konstanta bernama.
- Baris maksimum 88 karakter. **Tanpa karakter tab**, indentasi dua spasi,
  termasuk pada berkas `.tex`.
- Setiap `lstlisting` wajib punya `caption` dan `label`, dan captionnya
  menyebutkan lokasi berkasnya: `tersedia di \berkas{sources/chapterNN/nama}`.
- **Kode di dalam naskah adalah salinan dari berkas di `sources/chapterNN/`.**
  Potongan yang ditampilkan boleh lebih pendek, tetapi tidak boleh berbeda
  isinya.
- Keluaran nyata perintah disertakan sebagai komentar di bawah perintahnya,
  diawali `# Keluarannya:`.
- Skrip dijalankan memakai venv di `~/venv`.

## 9. Slide

- Satu slide per bab, di `slides/sessionNN/sessionNN.tex`, memakai tema di
  `slides/theme/`.
- Isinya ringkasan bab. **Gambar, tabel, dan angka pada slide wajib sama dengan
  yang ada pada naskah babnya.**
- Judul slide ditulis `\title{\Huge{Judul}}`, **tanpa** nomor pertemuan dan
  **tanpa** `\vspace` di dalamnya, sebab tambahan itu mendorong tanggal menimpa
  panel bawah. Nomor pertemuannya sudah tampak dari nama direktorinya.
- **Nama penulis digambar tema di dalam panel hijau sampul**, bukan mengalir
  bersama judul. Warnanya putih, sehingga di luar panel nama itu tidak terbaca,
  dan letaknya tidak boleh bergantung pada jumlah baris judul.
- **Setiap varian yang punya kode mendapat dua bingkai**, yaitu diagram
  komponen beserta potongan kodenya, lalu diagram urutannya.
- Urutan bingkai: Judul, Tujuan Pembelajaran, seksi materi, analogi, kasus,
  hasil pengukuran, **Ringkasan, lalu Latihan**. Latihan berada setelah
  Ringkasan.
- **Latihan pada slide ditulis rinci**, bukan sekadar daftar judul. Setiap
  latihan mendapat satu bingkai berisi perintah yang dijalankan, langkah kerja
  bernomor, dan pertanyaan analisisnya.
- **Judul bingkai dijaga pendek**, sebab judul panjang menabrak logo di sudut
  kanan atas. "Latihan 1: *Core Independence*" cukup, tanpa kata kerja
  tambahan.
- **Gambar besar mendapat bingkai sendiri selebar halaman**, memakai
  `width=\textwidth` beserta batas tinggi, lalu penjelasannya dipindah ke
  bingkai berikutnya dengan judul "Penjelasan *Class Diagram*" atau
  "Penjelasan *Sequence Diagram*". Tata letak dua kolom dipakai hanya bila
  gambarnya memang kecil.
- **Bingkai persiapan latihan menyebut modul sebagai rujukan utama**, sebab
  langkah lengkap, tabel contoh, dan lembar isian hanya ada di naskah bab.
- Slide dikompilasi dua kali agar nomor halaman totalnya benar.

## 10. Referensi

- Entri ditambahkan ke `module/references.bib`, disertai `url` yang dapat
  dibuka.
- Sitasi dipasang pada kalimat yang benar-benar mengambil isinya, bukan
  ditumpuk di akhir paragraf.

## 11. Struktur repositori

- Naskah bab: `module/chapterNN.tex`, disatukan oleh
  `module/software-architecture.tex`. Lampiran memakai `module/appendixA.tex`
  dan seterusnya.
- Berkas pendukung: `sources/chapterNN/`, satu direktori per bab, masing-masing
  punya `README.md` berisi tabel daftar berkas dan kegunaannya, ditambah tabel
  pemetaan latihan ke berkas yang dipakainya.
- Slide: `slides/sessionNN/sessionNN.tex`, tema di `slides/theme/`.
- Gambar bersama: `figures/`.
- Rancangan penelitian: `papers/nama-topik/`, satu direktori per topik.
- **Nomor bab, nomor slide, dan nomor direktori sumber harus selalu sejalan**,
  dan urutannya mengikuti daftar isi pada `README.md`.
- Berkas hasil kompilasi tidak ikut dilacak. Aturannya ada di `.gitignore`,
  mencakup keluaran LaTeX, `__pycache__`, `target/`, `bin/`, berkas basis data
  contoh, PDF hasil kompilasi di `module/`, `slides/`, dan `papers/`, serta
  direktori `videos/`. Berkas PDF di `figures/` tetap dilacak, sebab itu
  masukan kompilasi, bukan hasilnya.
