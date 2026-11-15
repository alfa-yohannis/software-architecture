# Dari Slide ke Google Drive, YouTube, dan Aswaya

Dokumen ini menjelaskan langkah lengkap untuk satu pertemuan. Urutannya: menarik
perubahan terbaru, membangun buku dan slide, memeriksa tata letak slide, mengunggah
PDF ke Google Drive, membuat video narasi, mengunggah video ke YouTube, lalu memasang
tautannya di Aswaya. Contoh perintah memakai pertemuan 10.

Langkahnya sama untuk dua repositori mata kuliah, yaitu `software-architecture`
(Arsitektur Perangkat Lunak) dan `advanced-web-engineering` (Pengembangan Aplikasi
Web). Nilai yang berbeda antarmata kuliah dikumpulkan di bagian 1. Seluruh perintah
dijalankan di HP Envy, tempat kedua repositori dan perkakasnya terpasang.

## Ringkasan alur

| Langkah | Perkakas | Hasil | Waktu kira-kira |
| --- | --- | --- | --- |
| 3. Tarik perubahan | git | repositori terbaru | 1 menit |
| 4. Bangun buku dan slide | xelatex atau latexmk | dua PDF | 1 sampai 2 menit |
| 5. Periksa tata letak slide | pdftotext, pdftoppm, montage | slide tanpa tumpang-tindih | 10 menit |
| 6. Unggah PDF ke Drive | rclone | file Drive tertimpa, ID tetap | 1 menit |
| 7. Atur bawaan metadata | `youtube_defaults.txt` | sekali per repositori | 2 menit |
| 8. Buat video narasi | slides_narrator | `sessionNN.mp4`, `.srt`, `youtube.txt` | 40 menit untuk 26 slide |
| 9. Periksa hasil video | ffprobe, editor teks | video siap unggah | 5 menit |
| 10. Unggah ke YouTube | shorts_automated_uploader | tautan `youtu.be` | 10 sampai 20 menit |
| 11. Pasang tautan di Aswaya | aswaya-mcp atau Moodle | modul "Video Pembelajaran" | 2 menit |
| 12. Commit dan push | git | perubahan tercatat | 1 menit |

Pembuatan video adalah tahap terlama. Tahap itu menunggu naskah narasi dari `claude`
dan suara dari Edge TTS, sehingga sebaiknya dijalankan di latar belakang. Selama
menunggu, langkah 6, 7, dan 12 dapat dikerjakan.

## 1. Nilai per mata kuliah

| Hal | Arsitektur Perangkat Lunak | Pengembangan Aplikasi Web |
| --- | --- | --- |
| Repositori | `~/projects/software-architecture` | `~/projects/advanced-web-engineering` |
| Membangun buku | `xelatex`, `bibtex`, `makeindex`, lalu `xelatex` dua kali di `module/` | `latexmk -xelatex advanced-web-engineering.tex` di `module/` |
| PDF buku | `module/software-architecture.pdf` | `module/advanced-web-engineering.pdf` |
| Membangun slide | `xelatex sessionNN.tex` dua kali di `slides/sessionNN/` | `latexmk -xelatex sessionNN.tex` di `slides/sessionNN/` |
| Aturan pemeriksaan | `CLAUDE.md` bagian 5.1: Overfull wajib nol | `TATA-CARA-PENULISAN.md` aturan 47 sampai 51 |
| Folder Drive (akun Pradita) | `IF231303 - Arsitektur Perangkat Lunak` | `IF140303_Pengembangan_Aplikasi_Web_2026-2027/resources` |
| Nama buku di Drive | `main.pdf` | `advanced-web-engineering.pdf` |
| Nama slide di Drive | `ch01b.pdf` untuk sesi 1, `chNN.pdf` untuk sesi 2 sampai 14 | `sessionNN.pdf`, sama dengan nama lokal |
| Playlist YouTube | Arsitektur Perangkat Lunak (Sofware Architecture) | Advanced Web Engineering (Rekayasa Web Lanjut) |
| Akhiran judul video | `\| Arsitektur Perangkat Lunak` | `\| Pengembangan Aplikasi Web` |
| Kursus Aswaya | id 5026 (IF31613, Ganjil 2026/2027) | id 5040 (IF140303, Ganjil 2026/2027) |
| Section pertemuan N | sesi 1 sampai 8 di section nomor N, sesi 9 sampai 14 di nomor N + 3 | section nomor N + 1 |

Ejaan "Sofware" pada nama playlist memang begitu di YouTube. Uploader mencocokkan
judul playlist persis, sehingga ejaan itu jangan dibetulkan di `youtube_defaults.txt`.

Id section Aswaya yang dipakai sampai November 2026:

| Pertemuan | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 11 | 12 | 13 | 14 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Kursus 5026 | 56688 | 56689 | 62604 | 56691 | 63093 | 63246 | 63247 | 63392 | 63393 | 63394 | 63395 | 63396 | 63397 | 63398 |
| Kursus 5040 | 56759 | 56760 | 56761 | 60807 | 60808 | 60809 | 60810 | 60811 | 60812 | 60813 | 60814 | 60815 | 60816 | 60817 |

Id ini dapat berubah bila section ditambah atau diurutkan ulang, sehingga selalu
dicocokkan lagi dengan `daftar_section` sebelum dipakai (langkah 11).

**Aturan privasi.** Folder `resources` milik Pengembangan Aplikasi Web dibagikan
kepada siapa pun yang memegang tautannya, dan folder itu juga berisi daftar peserta
serta folder tugas mahasiswa. Kedua repositori bersifat publik. Karena itu tautan
atau ID folder itu tidak pernah ditulis di repositori mana pun. Perintah rclone di
dokumen ini memakai jalur folder, bukan ID.

## 2. Persiapan sekali saja

### 2.1 Perkakas sistem

```bash
sudo apt install texlive-full latexmk poppler-utils imagemagick ffmpeg git curl rsync
```

`poppler-utils` menyediakan `pdftoppm`, `pdfinfo`, dan `pdftotext`. `imagemagick`
menyediakan `montage` untuk lembar kontak slide. Google Chrome versi stabil dipasang
dari situs Google. Claude Code (`claude`) harus sudah login, sebab slides_narrator
memakainya untuk menulis naskah narasi.

rclone dipasang dari paket `.deb` di rclone.org, sebab versi apt (1.60) jauh lebih
lama. Versi yang terpasang adalah 1.76.

### 2.2 Susunan direktori

Kedua perkakas berada sejajar dengan repositori mata kuliah:

```
~/projects/
├── software-architecture/
├── advanced-web-engineering/
├── slides_narrator/              # github.com/alfa-yohannis/slides_narrator
└── shorts_automated_uploader/    # github.com/alfa-yohannis/shorts_automated_uploader
```

### 2.3 slides_narrator

Tidak perlu instalasi manual. Pada jalannya yang pertama, `build.py` membuat
`slides_narrator/.venv` sendiri lalu memasang `edge-tts` ke dalamnya. Edge TTS tidak
memerlukan kunci maupun akun.

### 2.4 shorts_automated_uploader

```bash
cd ~/projects/shorts_automated_uploader
./setup.sh                       # venv, dependensi, profiles/, dan sessions/
```

Video diunggah ke kanal **AYO Learn!** (@alfayohannis). Kanal itu milik akun Gmail
yang login di profil Chrome "Default". Akun Pradita hanya untuk Google Drive dan
tidak dipakai untuk video, sebab kanalnya sendiri kosong.

Google memblokir login yang diketik oleh skrip, sehingga uploader memakai salinan
profil Chrome "Default" di `profiles/youtube/`. Salinan itu dibuat begini:

1. Pastikan youtube.com di Chrome biasa sudah login dengan akun Gmail tadi.
2. Tutup **semua** jendela Chrome.
3. Jalankan:

   ```bash
   cd ~/projects/shorts_automated_uploader
   ./init_youtube_profile.sh
   ```

   Lewat SSH, perintahnya membutuhkan layar dan D-Bus milik sesi desktop, agar
   keyring dapat membuka cookie:

   ```bash
   echo y | env DISPLAY=:0 XAUTHORITY=/home/alfa/.Xauthority \
     DBUS_SESSION_BUS_ADDRESS=unix:path=/run/user/1000/bus ./init_youtube_profile.sh
   ```

4. Buka kembali Chrome biasa.

Langkah ini diulang bila YouTube Studio di jendela otomasi berkata tidak punya izin
untuk kanal `UCEWLCMe8iwKOakYoaQ2k1eg`. Gejala itu berarti salinan profil sudah
berpindah ke akun lain.

### 2.5 Remote rclone `gdrive`

Remote `gdrive` memakai akun Pradita dengan cakupan `drive`. Bila remote belum ada
atau tokennya kedaluwarsa:

```bash
rclone config create gdrive drive scope=drive     # remote baru
rclone config reconnect gdrive:                   # token kedaluwarsa
```

Keduanya membuka halaman login Google di browser, lalu login dengan akun Pradita.
Lewat SSH, halaman itu perlu dibuka di layar Envy. Caranya: jalankan perintahnya di
latar belakang dengan keluaran ke berkas log, ambil tautan
`http://127.0.0.1:53682/auth?state=...` dari log, lalu buka di layar Envy:

```bash
setsid -f env DISPLAY=:0 XAUTHORITY=/home/alfa/.Xauthority XDG_CURRENT_DESKTOP=XFCE \
  XDG_RUNTIME_DIR=/run/user/1000 DBUS_SESSION_BUS_ADDRESS=unix:path=/run/user/1000/bus \
  xdg-open 'http://127.0.0.1:53682/auth?state=...'
```

Log itu dihapus sesudahnya, sebab rclone menulis token ke dalamnya. Setiap perintah
rclone mencetak pemberitahuan bahwa `client_id` bersama milik rclone akan dihentikan
pada 2026. Remote tetap bekerja sampai saat itu. Bila login mulai gagal, buat OAuth
client ID sendiri di Google Cloud mengikuti panduan rclone.

### 2.6 Aswaya

Tautan dipasang lewat server MCP `aswaya-mcp` di Claude Code. Kredensialnya dibaca
dari `.env` milik server itu, sehingga tidak ada kata sandi yang diketik. Tanpa Claude
Code, tautan dipasang lewat halaman Moodle (langkah 11.2).

## 3. Tarik perubahan terbaru

```bash
cd ~/projects/advanced-web-engineering          # atau software-architecture
git fetch --all --prune
git status -sb                                  # lihat berapa commit tertinggal
git pull --ff-only
```

Bila `git pull --ff-only` menolak karena ada perubahan lokal, simpan dulu perubahan
itu dengan `git stash`. Bila perubahan lokal memang boleh dibuang dan versi GitHub
yang dipakai, jalankan perintah berikut. Perintah ini menghapus semua perubahan lokal
yang belum di-push:

```bash
git reset --hard origin/main
```

## 4. Bangun buku dan slide

Pengembangan Aplikasi Web memakai latexmk. latexmk menjalankan `bibtex` dan
`makeindex` sendiri, lalu mengulang `xelatex` sampai rujukan stabil:

```bash
cd ~/projects/advanced-web-engineering/module
latexmk -xelatex -interaction=nonstopmode advanced-web-engineering.tex
cd ../slides/session10
latexmk -xelatex -interaction=nonstopmode session10.tex
```

Arsitektur Perangkat Lunak memakai urutan manual:

```bash
cd ~/projects/software-architecture/module
xelatex software-architecture
bibtex software-architecture
makeindex software-architecture
xelatex software-architecture
xelatex software-architecture
cd ../slides/session10
xelatex session10.tex
xelatex session10.tex             # kedua kalinya agar nomor halaman total benar
```

Periksa tiga hal pada setiap PDF:

```bash
pdfinfo session10.pdf | grep Pages                                # jumlah halaman
grep -c Overfull session10.log                                    # baris meluap
grep -E 'Reference .* undefined|Citation .* undefined' session10.log  # rujukan kosong
pdftotext session10.pdf - | grep -c '??'                          # harus 0
```

Pada Arsitektur Perangkat Lunak jumlah `Overfull` wajib nol. Pada Pengembangan
Aplikasi Web buku memiliki 103 Overfull kecil (paling besar 1,7 pt) sejak sebelum
November 2026, hampir semuanya dari baris listing. Angka itu dipakai sebagai
pembanding, sehingga yang perlu diperiksa adalah kenaikannya.

## 5. Periksa tata letak slide

Video menampilkan slide apa adanya, sehingga kesalahan tata letak ikut terekam.
Beamer tidak memberi peringatan untuk teks yang menumpuk, jadi pemeriksaan ini
memakai dua cara: kotak kata dari `pdftotext -bbox` dan pemeriksaan dengan mata.

### 5.1 Pemeriksaan otomatis

Tema Pradita menggambar logo mulai x = 12,16 cm (346 pt) sampai y sekitar 40,5 pt
dari atas halaman. Judul bingkai digambar dengan latar putih, sehingga judul yang
terlalu panjang menutupi sebagian logo. Isi bingkai diletakkan di tengah secara
vertikal, sehingga isi yang terlalu tinggi mendorong baris pertamanya naik ke samping
judul dan ke bawah logo.

Simpan skrip berikut sebagai `/tmp/check_slides.py`:

```python
"""Find beamer slides (Pradita theme, 16:9) where text runs into the logo, the
title, or the green footer bar. Beamer prints no warning for these.

Usage: python3 check_slides.py deck.pdf      (or a saved `pdftotext -bbox` .html)
Prints one line per problem slide and exits 1 if any slide is flagged.
"""
import re
import subprocess
import sys

CM = 28.4528                 # points per centimetre
LOGO_X0 = 12.16 * CM         # logo: centred at 13.5 cm, 2.68 cm wide
LOGO_Y1 = 40.5               # logo bottom, in points from the page top
TITLE_BAND = 22              # title words start above this y
BAR_TOP = 237.0              # top of the green footer bar


def read_pages(path):
    if path.endswith(".pdf"):
        html = subprocess.run(["pdftotext", "-bbox", path, "-"],
                              capture_output=True, text=True, check=True).stdout
    else:
        html = open(path, encoding="utf-8").read()
    return re.findall(r'<page width="([\d.]+)" height="([\d.]+)">(.*?)</page>', html, re.S)


def words_of(body):
    found = re.findall(r'<word xMin="([\d.]+)" yMin="([\d.]+)" xMax="([\d.]+)" '
                       r'yMax="([\d.]+)">(.*?)</word>', body)
    words = [(float(a), float(b), float(c), float(d), t) for a, b, c, d, t in found]
    return [w for w in words if not re.fullmatch(r"\d+/\d+", w[4])]   # page number


def problems(words, page_width):
    title = [w for w in words if w[1] < TITLE_BAND]
    body = [w for w in words if w[1] >= TITLE_BAND]
    notes = []
    if title:
        title_right = max(w[2] for w in title)
        title_bottom = max(w[3] for w in title)
        if title_right > LOGO_X0 - 2:
            notes.append(f"title reaches the logo ({title_right:.0f} pt)")
        under_title = [w[4] for w in body
                       if w[1] < title_bottom - 1 and w[0] < title_right + 2]
        if under_title:
            notes.append("text beside the title: " + " ".join(under_title[:5]))
    in_logo = [w[4] for w in body if w[2] > LOGO_X0 - 2 and w[1] < LOGO_Y1 + 1.5]
    if in_logo:
        notes.append("text under the logo: " + " ".join(in_logo[:5]))
    if body and max(w[3] for w in body) > BAR_TOP - 6:
        notes.append(f"text near the footer bar ({max(w[3] for w in body):.0f} pt)")
    if any(w[2] > page_width - 4 for w in words):
        notes.append("text at the right edge")
    return notes


def main():
    flagged = 0
    pages = read_pages(sys.argv[1])
    for number, (width, _height, body) in enumerate(pages, 1):
        if number == 1:            # the cover has its own layout
            continue
        notes = problems(words_of(body), float(width))
        if notes:
            flagged += 1
            print(f"slide {number}: " + "; ".join(notes))
    print(f"{len(pages)} slides, {flagged} flagged")
    sys.exit(1 if flagged else 0)


if __name__ == "__main__":
    main()
```

Jalankan pada deck yang baru dibangun:

```bash
python3 /tmp/check_slides.py ~/projects/advanced-web-engineering/slides/session10/session10.pdf
# Keluaran yang diharapkan:
# 57 slides, 0 flagged
```

Arti tiap tanda dan cara memperbaikinya:

| Tanda | Artinya | Perbaikan |
| --- | --- | --- |
| `title reaches the logo` | judul bingkai lebih panjang daripada ruang sebelum logo | pendekkan judul; batas praktisnya sekitar 34 karakter |
| `text beside the title` | baris pertama isi naik ke samping judul | kurangi tinggi isi, lihat catatan di bawah |
| `text under the logo` | baris pertama isi menyentuh logo | sama seperti di atas |
| `text near the footer bar` | baris terakhir hampir menyentuh pita hijau | pendekkan isi atau pecah menjadi dua slide |
| `text at the right edge` | teks keluar dari tepi kanan | perkecil tabel atau gambar, atau pendekkan baris kode |

Isi bingkai diletakkan di tengah secara vertikal. Akibatnya, memendekkan isi di bawah
baris pertama menurunkan baris pertama sebanyak setengah tinggi yang dibuang.
Sebaliknya, mengurangi `\vspace` di awal bingkai justru **menaikkan** baris pertama.
Untuk menurunkan baris pertama, pendekkan kalimat di bawahnya, rapatkan jarak
antarbutir, atau pecah slidenya. Aturan 44 pada `TATA-CARA-PENULISAN.md` mengizinkan
potongan kode yang panjang dipersingkat.

Contoh pada sesi 10 Pengembangan Aplikasi Web (commit `96e37c8`): judul "Resource
Server Memeriksanya Bagaimana" menjadi "Cara Resource Server Memeriksa", dan kalimat
pengantar dua baris di slide 10 menjadi satu baris.

### 5.2 Pemeriksaan dengan mata

Skrip di atas hanya melihat teks. Gambar yang terpotong atau diagram yang menabrak
judul hanya terlihat dari hasil render:

```bash
mkdir -p /tmp/cek-slide && cd /tmp/cek-slide && rm -f p-*.png lembar*.png
pdftoppm -png -r 65 ~/projects/advanced-web-engineering/slides/session10/session10.pdf p
montage p-*.png -tile 4x4 -geometry +4+4 lembar.png    # lembar-0.png, lembar-1.png, ...
```

Setiap lembar memuat 16 slide. Slide yang mencurigakan dirender ulang lebih besar
(`pdftoppm -r 150 -f 21 -l 21 ...`) lalu diperiksa sudut kanan atasnya. Sesudah
memperbaiki `.tex`, bangun ulang slide (langkah 4), lalu ulangi langkah 5 sampai
bersih.

## 6. Unggah PDF ke Google Drive

Aswaya menautkan langsung ke ID file di Drive. Karena itu file lama **ditimpa**,
bukan dihapus lalu diunggah ulang. `rclone copyto` ke nama yang sudah ada memperbarui
isi file itu, sehingga ID, tautan, dan izin berbaginya tetap.

```bash
cd ~/projects/advanced-web-engineering
DRIVE="gdrive:IF140303_Pengembangan_Aplikasi_Web_2026-2027/resources"
rclone copyto module/advanced-web-engineering.pdf "$DRIVE/advanced-web-engineering.pdf"
rclone copyto slides/session10/session10.pdf "$DRIVE/session10.pdf"
```

```bash
cd ~/projects/software-architecture
DRIVE="gdrive:IF231303 - Arsitektur Perangkat Lunak"
rclone copyto module/software-architecture.pdf "$DRIVE/main.pdf"
rclone copyto slides/session10/session10.pdf "$DRIVE/ch10.pdf"
```

Periksa sebelum dan sesudah menimpa. ID harus sama, ukuran harus sama dengan berkas
lokal, dan waktu ubahnya harus baru:

```bash
rclone lsjson --stat "$DRIVE/session10.pdf" 2>/dev/null \
  | python3 -c 'import json,sys; d=json.load(sys.stdin); print(d["ID"], d["Size"], d["ModTime"])'
ls -l slides/session10/session10.pdf
rclone lsf "$DRIVE" --files-only --max-depth 1 2>/dev/null | sort | uniq -d   # harus kosong
```

Keluaran `--stat` ditulis `"ID": "..."` dengan spasi, sehingga diurai sebagai JSON,
bukan dengan `grep`. Jangan memakai `--max-depth` lebih dari 1 pada folder Pengembangan
Aplikasi Web, sebab subfoldernya berisi nama mahasiswa. Izin berbagi dapat diperiksa
lewat dialog "Bagikan" di Drive. Izin yang benar:

- Arsitektur Perangkat Lunak: folder privat, tiap file dibagikan ke domain
  pradita.ac.id sebagai *commenter*.
- Pengembangan Aplikasi Web: siapa pun yang memegang tautan sebagai *commenter*, dan
  domain pradita.ac.id sebagai *editor*.

Tanpa rclone, file dapat ditimpa dari Drive di browser. Klik kanan file, pilih
"Informasi file", lalu "Kelola versi", lalu "Upload versi baru". Mengunggah lewat
tombol "Baru" justru membuat file kedua dengan ID baru, dan tautan Aswaya tetap
menunjuk ke file lama.

## 7. Atur bawaan metadata YouTube

Setiap repositori punya `youtube_defaults.txt` di akarnya. slides_narrator membacanya
saat menulis `videos/sessionNN/youtube.txt`. Baris sebelum header pertama diabaikan.
Isi milik Pengembangan Aplikasi Web:

```
PLAYLIST
Advanced Web Engineering (Rekayasa Web Lanjut)

LANGUAGE
Indonesian

CATEGORY
Education

LICENSE
creative_commons

VISIBILITY
public

MADE_FOR_KIDS
no

ALTERED_CONTENT
no

TITLE_SUFFIX
| Pengembangan Aplikasi Web
```

| Header | Nilai yang sah | Dipakai untuk |
| --- | --- | --- |
| `PLAYLIST` | judul playlist persis seperti di YouTube | playlist video |
| `LANGUAGE` | nama bahasa seperti di Studio, mis. `Indonesian` | bahasa video dan subtitle |
| `CATEGORY` | nama kategori seperti di Studio, mis. `Education` | kategori video |
| `LICENSE` | `creative_commons` atau `standard` | lisensi |
| `VISIBILITY` | `public`, `unlisted`, atau `private` | visibilitas saat terbit |
| `MADE_FOR_KIDS` | `yes` atau `no` | audiens |
| `ALTERED_CONTENT` | `yes` atau `no` | pertanyaan konten sintetis |
| `TITLE_SUFFIX` | teks apa pun | ditempel di akhir judul |

Video pertemuan 2 sampai 9 kedua mata kuliah diunggah dengan kategori Science &
Technology, sedangkan bawaan sejak sesi 10 adalah Education. Ubah `CATEGORY` bila
ingin seragam dengan video lama. Setiap nilai juga dapat ditimpa per video dengan
flag `--youtube-playlist`, `--youtube-language`, `--youtube-category`,
`--youtube-license`, `--youtube-visibility`, `--youtube-made-for-kids`,
`--youtube-altered-content`, atau `--youtube-title-suffix` pada slides_narrator.

## 8. Buat video narasi

Jalankan dari akar repositori mata kuliah:

```bash
cd ~/projects/advanced-web-engineering
nohup python3 ../slides_narrator/slides_narrator/build.py \
  --pdf slides/session10/session10.pdf --target videos/session10 \
  --final-name session10 --claude-effort max --concurrency 4 \
  > /tmp/session10-video.log 2>&1 &
tail -f /tmp/session10-video.log
```

Bila perintah ini dijalankan dari dalam sesi Claude Code, awali dengan
`env -u CLAUDECODE`. Tanpa itu, `claude` yang dipanggil di dalamnya menolak berjalan.

Tahapan yang tampil di log:

| Label log | Pekerjaan | Hasil di `videos/session10/` |
| --- | --- | --- |
| `[1/6]` | merender tiap halaman PDF ke PNG 300 DPI | `slides/slide_NN.png` |
| `[2/6]` | `claude` (Opus, effort max) menulis naskah narasi tiap slide | `scripts/slide_NN.txt` |
| `[3/6+5/6]` | Edge TTS membacakan naskah sekaligus membuat subtitle per slide | `audio/slide_NN.mp3`, `subtitles/clip_NN.srt` |
| `[4/6]` | ffmpeg menggabungkan gambar slide dengan suaranya | `clips/clip_NN.mp4` |
| `[6/6]` | ffmpeg menyambung semua klip dan subtitle | `session10.mp4`, `session10.srt` |
| `[7/7]` | `claude` menulis judul, deskripsi dengan daftar isi, dan kata kunci | `youtube.txt` |

Tahap `[2/6]` paling lama, sebab `claude` membaca seluruh PDF, sumber `.tex`, dan kode
di `sources/` sebelum menulis. Baris `claude session started` yang berulang dengan id
sesi yang sama adalah hal biasa, bukan tanda gagal. Sesi 10 Arsitektur Perangkat Lunak
(26 slide) selesai dalam sekitar 40 menit.

Prosesnya dapat dilanjutkan. Bila terhenti, misalnya karena Edge TTS gagal tersambung,
jalankan ulang perintah yang sama. Tahap yang sudah selesai dilewati. Pilihan lain:

```bash
# hanya menulis ulang pengaturan di youtube.txt, teksnya tetap
python3 ../slides_narrator/slides_narrator/build.py --pdf slides/session10/session10.pdf \
  --target videos/session10 --final-name session10 --only youtube --skip-scripts

# menulis ulang judul, deskripsi, dan daftar isi juga (sekitar 7 menit)
python3 ../slides_narrator/slides_narrator/build.py --pdf slides/session10/session10.pdf \
  --target videos/session10 --final-name session10 --only youtube --skip-scripts --force
```

Bila slide diubah sesudah video dibuat, hapus `videos/sessionNN/` lalu bangun ulang,
agar gambar, naskah, dan suara tetap sejalan dengan PDF. Folder `videos/` tidak ikut
dilacak git di kedua repositori.

## 9. Periksa hasil video

```bash
cd ~/projects/advanced-web-engineering/videos/session10
ffprobe -v error -select_streams v:0 -show_entries stream=width,height \
  -show_entries format=duration -of default=nw=1 session10.mp4
grep -c -- '-->' session10.srt          # jumlah baris subtitle
cat youtube.txt
```

Hasil yang benar:

- Video 1920 x 1080, durasinya masuk akal untuk jumlah slidenya.
- `TITLE` diakhiri akhiran judul mata kuliah dan tidak lebih dari 100 karakter.
- `DESCRIPTION` memuat blok `Daftar isi:` dengan minimal tiga cap waktu. Cap pertama
  `0:00`, dan jarak antarcap minimal 10 detik. YouTube hanya membuat bab video bila
  ketiga syarat ini terpenuhi.
- Pengaturan di bawah `KEYWORDS` lengkap: `VIDEO`, `PLAYLIST`, `LANGUAGE`, `CATEGORY`,
  `LICENSE`, `VISIBILITY`, `MADE_FOR_KIDS`, `ALTERED_CONTENT`, `RECORDING_DATE`,
  `COVER` (`slides/slide_01.png`), dan `SUBTITLES` (`session10.srt`).

Tonton beberapa bagian video, terutama awal, satu slide berkode, dan penutup. Judul
dan deskripsi boleh disunting langsung di `youtube.txt` sebelum diunggah.

## 10. Unggah ke YouTube

### 10.1 Jalankan uploader

Periksa dulu apakah jendela Chrome otomasi dari unggahan sebelumnya masih terbuka:

```bash
curl -s --max-time 3 http://127.0.0.1:9222/json/version | head -3
```

Bila ada jawaban, pakai `--cdp`. Bila tidak, pakai `--chrome` agar uploader membuka
Chrome di `profiles/youtube/`:

```bash
cd ~/projects/shorts_automated_uploader
DISPLAY=:0 ./venv/bin/python upload_youtube.py \
  ../advanced-web-engineering/videos/session10/youtube.txt --cdp http://127.0.0.1:9222 --post
# atau
DISPLAY=:0 ./venv/bin/python upload_youtube.py \
  ../advanced-web-engineering/videos/session10/youtube.txt --chrome --post
```

`youtube.txt` adalah satu-satunya argumen, sebab blok `VIDEO` menyebut berkas
videonya. Uploader lalu mengerjakan seluruh isian Studio:

1. membuka halaman unggah kanal dan memilih berkas video;
2. mengisi judul, deskripsi, dan tag dari kata kunci;
3. memasang thumbnail dari `COVER`, dikecilkan dulu bila lebih dari 2 MB;
4. mencentang playlist, lalu mengatur audiens, konten sintetis, bahasa, tanggal
   rekam, kategori, dan lisensi;
5. mengunggah subtitle `.srt` dengan pewaktuannya, sesudah bahasa video terpasang;
6. memilih visibilitas, menunggu "Checks complete", lalu menekan Publish.

Di awal, uploader mencetak pengaturan yang akan dipakai. Bacalah sebelum unggahan
berjalan jauh:

```
Upload settings: visibility=public, playlist=Advanced Web Engineering (Rekayasa Web Lanjut),
language=Indonesian, category=Education, license=creative_commons, made_for_kids=no,
altered_content=no, recording_date=2026-11-15
Thumbnail: .../videos/session10/slides/slide_01.png
Subtitles: .../videos/session10/session10.srt
```

Di akhir, uploader mencetak `Video URL: https://youtu.be/<id>` lalu mencatat id itu di
`ledger.json`. Flag di baris perintah, misalnya `--visibility unlisted` atau
`--playlist "..."`, menimpa isi `youtube.txt` untuk unggahan itu saja.

Video yang panjang memunculkan dialog "Video processing ... needs to finish processing
before your video is public" sesudah Publish. Dialog itu tanda berhasil. Video menjadi
publik sendiri setelah YouTube selesai memprosesnya.

### 10.2 Pastikan hasilnya

```bash
curl -s "https://www.youtube.com/oembed?url=https://youtu.be/<id>&format=json"
```

Jawaban berisi judul video berarti video sudah publik. Periksa juga di Studio bahwa
video masuk playlist yang benar, subtitlenya tampil, thumbnail-nya slide judul, dan
daftar isi muncul sebagai bab video.

### 10.3 Unggahan uji coba dan penghapusan

Untuk mencoba tanpa menerbitkan, pakai `--visibility private` tanpa `--post`.
Uploader berhenti di langkah Visibility dan meninggalkan draf. Hapus draf atau video
yang salah dengan:

```bash
DISPLAY=:0 ./venv/bin/python delete_youtube.py https://youtu.be/<id> --chrome          # uji coba
DISPLAY=:0 ./venv/bin/python delete_youtube.py https://youtu.be/<id> --chrome --yes    # hapus
```

Ledger menolak mengunggah berkas yang sama dua kali. Untuk mengunggah ulang, hapus
dulu video lamanya dengan `delete_youtube.py`, yang juga menghapus catatannya di
ledger, atau tambahkan `--force`.

## 11. Pasang tautan di Aswaya

### 11.1 Lewat Claude Code

Minta Claude Code, misalnya: "Tambahkan https://youtu.be/<id> sebagai Video
Pembelajaran di Aswaya, mata kuliah Pengembangan Aplikasi Web, pertemuan 10." Di
baliknya, Claude memanggil tool `aswaya-mcp` berurutan:

1. `daftar_kursus(cari="Web")` untuk mendapatkan `kursus_id` (5040).
2. `daftar_section(kursus_id=5040)` untuk mendapatkan `section_id` pertemuan 10
   (60813, section nomor 11).
3. `daftar_tautan(kursus_id=5040)` untuk memastikan tautan video belum ada.
4. `tambah_tautan(kursus_id=5040, section_id=60813, nama="Video Pembelajaran",
   url="https://youtu.be/<id>")` sebagai uji coba. Pratinjaunya ditunjukkan dulu.
5. Panggilan yang sama dengan `kirim=True` setelah pratinjau disetujui.
6. `daftar_tautan` sekali lagi untuk memastikan modulnya muncul di section yang benar.

Bila jawaban pengiriman berisi `terkirim=true` tetapi `ok=false`, jangan mengirim
ulang. Periksa dulu dengan `daftar_tautan`, sebab tautannya mungkin sudah masuk.

### 11.2 Lewat browser

1. Buka halaman kursus di Aswaya, lalu nyalakan mode sunting.
2. Pada section pertemuan yang benar, pilih "Add an activity or resource", lalu "URL".
3. Isi Name dengan `Video Pembelajaran` dan External URL dengan tautan `youtu.be`.
4. Biarkan Display pada "Automatic", lalu "Save and return to course".

## 12. Commit dan push

Yang di-commit hanya sumber yang berubah, misalnya perbaikan `.tex` slide, README,
atau `youtube_defaults.txt`. PDF hasil kompilasi dan folder `videos/` tidak dilacak.

```bash
cd ~/projects/advanced-web-engineering
git status --short
git add slides/session10/session10.tex
git commit -m "Keep session 10 titles and first lines clear of the logo"
git push
```

## 13. Daftar periksa akhir

- [ ] `git status -sb` menunjukkan repositori sejajar dengan `origin/main`.
- [ ] Buku dan slide terbangun tanpa galat, tanpa `??`, dan tanpa Overfull baru.
- [ ] `check_slides.py` melaporkan `0 flagged`, dan lembar kontak sudah dilihat.
- [ ] Kedua PDF di Drive tertimpa: ID lama, ukuran sama dengan lokal, tanpa duplikat.
- [ ] `videos/sessionNN/youtube.txt` lengkap, dengan minimal tiga bab video.
- [ ] Video publik di kanal AYO Learn!, masuk playlist yang benar, dengan subtitle,
      thumbnail, dan bab video.
- [ ] Aswaya punya modul "Video Pembelajaran" di section pertemuan itu.
- [ ] Perubahan sumber sudah di-commit dan di-push.

## 14. Masalah yang pernah muncul

| Gejala | Penyebab | Penanganan |
| --- | --- | --- |
| `claude` menolak berjalan saat narasi dibuat | dipanggil dari dalam sesi Claude Code | awali perintah dengan `env -u CLAUDECODE` |
| Pembuatan video berhenti di tengah | Edge TTS atau jaringan putus | jalankan ulang perintah yang sama |
| Studio berkata tidak punya izin untuk kanal | `profiles/youtube` berpindah ke akun Pradita | salin ulang profil Chrome "Default" (bagian 2.4) |
| Playlist tidak tercentang | judul di `PLAYLIST` tidak persis sama | salin judul dari YouTube, termasuk ejaan "Sofware" |
| Tombol Add subtitle tidak aktif | bahasa video belum terpasang | isi `LANGUAGE`; uploader memasang bahasa lebih dulu |
| Unggahan berhenti di langkah Visibility | `--post` tidak dipakai | terbitkan dari Studio, atau hapus draf lalu ulangi dengan `--post` |
| "has already been successfully uploaded" | ledger mencatat berkas itu | `--force`, atau hapus videonya dengan `delete_youtube.py` |
| Dialog "Video processing" sesudah Publish | video panjang masih diproses | bukan galat; tunggu sampai video publik |
| rclone gagal login | token kedaluwarsa atau `client_id` bersama dihentikan | `rclone config reconnect gdrive:`, atau buat OAuth client ID sendiri |
| Tautan Aswaya ke slide rusak sesudah unggah | file dihapus lalu diunggah ulang sehingga ID berubah | perbarui modul "Slides" dengan `ubah_tautan`; lain kali timpa dengan `rclone copyto` |
| Login Aswaya terhalang captcha atau MFA | kebijakan login web | pasang tautan lewat browser (bagian 11.2) |
