# Aplikasi Pesan P2P Sederhana dengan Rust

Ini adalah aplikasi pesan TCP asinkron sederhana yang ditulis dalam bahasa Rust. Aplikasi ini mendemonstrasikan kemampuan jaringan dasar menggunakan `tokio` untuk eksekusi asinkron dan `serde_json` untuk menyerialisasi dan mendeserialisasi pesan.

## Cara Kerjanya

Aplikasi ini dapat berjalan dalam dua mode:
1. **Mode Server**: Mendengarkan pada alamat TCP dan port tertentu untuk koneksi yang masuk, kemudian membaca dan mencetak pesan yang diterima.
2. **Mode Klien**: Terhubung ke alamat server rekan (peer) yang ditentukan, mengirimkan pesan dalam format JSON yang berisi nama pengirim dan isi pesan, lalu keluar.

Pesan disusun dengan struktur seperti berikut:
```json
{
  "sender": "Nama",
  "content": "Isi pesan"
}
```

## Tutorial: Alice, Bob, dan Charlie

Dalam tutorial ini, kita akan mengatur tiga instance yang mewakili tiga pengguna berbeda: Alice, Bob, dan Charlie. Masing-masing dari mereka akan menjalankan server untuk menerima pesan dan menggunakan mode klien untuk mengirim pesan satu sama lain.

### Prasyarat
Pastikan Anda telah menginstal Rust dan Cargo.

### Langkah 1: Mulai Server untuk Alice, Bob, dan Charlie

Buka tiga jendela terminal terpisah. Di setiap terminal, arahkan ke direktori proyek ini dan jalankan server untuk setiap pengguna pada port yang berbeda.

**Terminal 1 (Server Alice):**
```bash
cargo run -- server 127.0.0.1:8081
```

**Terminal 2 (Server Bob):**
```bash
cargo run -- server 127.0.0.1:8082
```

**Terminal 3 (Server Charlie):**
```bash
cargo run -- server 127.0.0.1:8083
```

Ketiga server sekarang sedang mendengarkan pesan yang masuk.

### Langkah 2: Kirim Pesan

Buka terminal keempat (atau gunakan salah satu yang sudah ada jika Anda menjalankan server di latar belakang/background) untuk bertindak sebagai pengirim. Kita akan menggunakan mode klien untuk mengirim pesan.

**Alice mengirim pesan ke Bob:**
```bash
cargo run -- client 127.0.0.1:8082 Alice "Hai Bob, apa kabar?"
```
Cek Terminal 2 (Server Bob) untuk melihat pesan yang diterima!

**Bob membalas Alice:**
```bash
cargo run -- client 127.0.0.1:8081 Bob "Kabarku baik, terima kasih Alice!"
```
Cek Terminal 1 (Server Alice).

**Charlie mengirim pesan ke Alice:**
```bash
cargo run -- client 127.0.0.1:8081 Charlie "Hei Alice, ini Charlie."
```
Cek Terminal 1 (Server Alice).

**Alice mengirim pesan ke Charlie:**
```bash
cargo run -- client 127.0.0.1:8083 Alice "Halo Charlie!"
```
Cek Terminal 3 (Server Charlie).

### Kesimpulan

Anda telah berhasil mengatur tiga node pesan independen dan mendemonstrasikan komunikasi di antara mereka menggunakan jaringan TCP asinkron di Rust.
