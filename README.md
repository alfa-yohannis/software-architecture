# software-architecture
Repositori ini memuat naskah buku referensi **Arsitektur Perangkat Lunak Terukur**, beserta
kode program, skrip pengukuran, dan slide yang menyertainya. Buku ini juga dapat
digunakan sebagai buku ajar mata kuliah Arsitektur Perangkat Lunak (IF231303).

## Buku
Naskahnya ada di `module/`. Selain lima belas bab, buku ini memuat bagian awal
(halaman judul, halaman hak cipta, daftar isi, daftar gambar, daftar tabel,
daftar listing, Prakata, Pernyataan Penggunaan Kecerdasan Artifisial, dan
Pendahuluan) serta bagian akhir (Penutup, Glosarium, Daftar Pustaka, Indeks, dan
Riwayat Penulis). Status kelengkapannya sebagai buku referensi dicatat di
`module/CHECKLIST-BUKU-REFERENSI.md`.

Buku dibangun dari direktori `module/`:

```bash
xelatex software-architecture
bibtex software-architecture
makeindex software-architecture
xelatex software-architecture
xelatex software-architecture
```

## PDF di Google Drive
PDF buku dan slide dibagikan lewat folder Google Drive utama
[IF231303 - Arsitektur Perangkat Lunak](https://drive.google.com/drive/folders/1D9gElAMKq6KNMZsQwGsQPEZ7SB9kjCVd).
Foldernya privat. Setiap file di dalamnya dibagikan ke domain pradita.ac.id sebagai
*commenter*, dan Aswaya menautkan langsung ke ID file-nya. Karena itu file ditimpa,
bukan dihapus lalu diunggah ulang, sehingga ID dan tautannya tetap.

| File lokal | Nama di Drive |
|---|---|
| `module/software-architecture.pdf` | `main.pdf` |
| `slides/session01/session01.pdf` | `ch01b.pdf` |
| `slides/sessionNN/sessionNN.pdf`, sesi 02 sampai 14 | `chNN.pdf` |

Penimpaan memakai rclone dengan remote `gdrive`, dijalankan dari akar repositori:

```bash
FOLDER=1D9gElAMKq6KNMZsQwGsQPEZ7SB9kjCVd
rclone copyto module/software-architecture.pdf gdrive:main.pdf \
  --drive-root-folder-id $FOLDER
rclone copyto slides/session10/session10.pdf gdrive:ch10.pdf \
  --drive-root-folder-id $FOLDER
```

## Daftar Isi
Materi Arsitektur Perangkat Lunak (Software Architecture) :
1. Introduction + Client-Server Architecture (CSA)
2. Layered Architecture
3. Model-View-* Architectures (MV*)
4. Ports and Adapters (Hexagonal) Architecture
5. Microkernel/Plugins Architecture
6. Pipeline / Pipe-and-Filter Architecture
7. Peer-to-Peer Architecture
8. Space-based Architecture (SBA)
9. Event-Driven Architecture (EDA)
10. CQRS and Event Sourcing
11. Service-based Architecture
12. Orchestration-driven Service-oriented Architecture (ODSOA)
13. Microservices Architecture
14. Serverless Architecture
15. Capstone Project

## Deskripsi
Dosen       : Alfa Ryano Yohannis
\
Kode MK     : IF231303
\
Universitas : Pradita University
