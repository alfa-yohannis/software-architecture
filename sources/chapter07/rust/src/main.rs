use tokio::net::{TcpListener, TcpStream};
use tokio::io::{AsyncReadExt, AsyncWriteExt};
use serde::{Serialize, Deserialize};
use std::env;
use std::error::Error;

// Struct ini mewakili pesan yang dikirim antar pengguna.
// Kita menggunakan `Serialize` dan `Deserialize` dari crate `serde` agar kita bisa
// dengan mudah mengubah struct Rust ini menjadi string JSON dan sebaliknya.
#[derive(Serialize, Deserialize)]
struct Message {
    sender: String,
    content: String,
}

// Kata kunci `async` menandakan bahwa fungsi ini tidak memblokir thread saat menunggu
// operasi jaringan (seperti melakukan binding ke port atau menerima koneksi).
async fn start_server(address: &str) -> Result<(), Box<dyn Error>> {
    // Kita mengikat (bind) listener TCP ke alamat yang diberikan. Kata kunci `await` menghentikan sementara fungsi ini
    // hingga proses binding selesai, membiarkan tugas asinkron lainnya berjalan sementara itu.
    let listener = TcpListener::bind(address).await?;
    println!("Mendengarkan pada {}", address);

    // Ini adalah infinite loop (perulangan tak terbatas) yang terus menerus menerima koneksi yang masuk.
    loop {
        // `accept()` menunggu klien untuk terhubung. Saat terhubung, fungsi ini mengembalikan `socket`
        // (untuk membaca/menulis data) dan `addr` (alamat IP klien).
        let (mut socket, addr) = listener.accept().await?;
        println!("Koneksi baru dari: {}", addr);

        // Kita menggunakan `tokio::spawn` untuk membuat tugas asinkron baru yang ringan untuk menangani
        // klien spesifik ini. Ini memungkinkan server kita menangani banyak klien secara bersamaan
        // tanpa harus menunggu satu klien selesai sebelum menerima klien lainnya.
        tokio::spawn(async move {
            // Buat buffer untuk menyimpan sementara data yang masuk dari jaringan.
            let mut buffer = vec![0; 1024];
            
            // Baca data dari socket ke dalam buffer kita.
            match socket.read(&mut buffer).await {
                // Jika kita berhasil membaca beberapa data (ukuran > 0)...
                Ok(size) if size > 0 => {
                    // Ubah byte di dalam buffer menjadi String yang dapat dibaca.
                    // `from_utf8_lossy` menangani karakter yang tidak valid dengan aman.
                    let received_msg = String::from_utf8_lossy(&buffer[..size]);
                    println!("Diterima: {}", received_msg);
                }
                // Jika ukurannya 0 atau terjadi error, koneksi ditutup.
                _ => println!("Koneksi ditutup."),
            }
        });
    }
}

// Fungsi ini mengirim pesan ke alamat server rekan (peer) tertentu.
async fn send_message(peer_address: &str, sender_name: &str, content: &str) -> Result<(), Box<dyn Error>> {
    // Mencoba terhubung ke server TCP rekan. Ini juga merupakan operasi asinkron.
    let mut stream = TcpStream::connect(peer_address).await?;
    
    // Buat struct Message kita dengan pengirim dan konten yang diberikan.
    let message = Message {
        sender: sender_name.to_string(),
        content: content.to_string(),
    };

    // Ubah struct Rust kita menjadi string berformat JSON.
    let serialized_msg = serde_json::to_string(&message)?;
    
    // Tulis string JSON melalui stream TCP ke rekan tersebut.
    stream.write_all(serialized_msg.as_bytes()).await?;
    
    println!("Pesan terkirim: {}", serialized_msg);
    Ok(())
}

// Makro `#[tokio::main]` mengatur runtime asinkron Tokio.
// Anggap saja ini sebagai mesin yang menggerakkan semua fungsi `async` dan panggilan `await` kita.
#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    // Kumpulkan argumen baris perintah (command-line arguments) yang diberikan saat menjalankan program.
    let args: Vec<String> = env::args().collect();
    
    // Jika argumen yang diberikan tidak cukup, tampilkan cara menggunakan program.
    if args.len() < 2 {
        println!("Penggunaan:\n  Mode Server: {} server <alamat>\n  Mode Klien: {} client <alamat_rekan> <nama> <pesan>", args[0], args[0]);
        return Ok(());
    }

    // Periksa mode mana yang ingin dijalankan pengguna: 'server' atau 'client'
    if args[1] == "server" {
        // Jika alamat diberikan, gunakan itu; jika tidak, default ke localhost pada port 8080.
        let address = args.get(2).cloned().unwrap_or_else(|| "127.0.0.1:8080".to_string());
        // Mulai server dan `await` eksekusinya.
        start_server(&address).await?;
    } else if args[1] == "client" {
        // Pastikan semua argumen yang dibutuhkan untuk klien telah diberikan.
        if args.len() < 5 {
            println!("Penggunaan: {} client <alamat_rekan> <nama> <pesan>", args[0]);
            return Ok(());
        }
        
        let peer_address = &args[2];
        let sender_name = &args[3];
        let message = &args[4];
        
        // Kirim pesan dan `await` sampai operasi selesai.
        send_message(peer_address, sender_name, message).await?;
    }

    Ok(())
}
