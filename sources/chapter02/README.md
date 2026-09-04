# Sumber Bab 2: Layered Architecture

Satu basis kode dipakai untuk tiga latihan yang menyasar tiga masalah berbeda,
yaitu lapisan yang tidak bekerja, arah ketergantungan yang dilanggar, dan biaya
waktu setiap lompatan antar lapisan.

| Berkas | Kegunaan |
| --- | --- |
| `basis_data.py` | Membuat tabel kurs pada SQLite dan mengisinya dengan data awal |
| `aplikasi_tertutup.py` | Aplikasi konversi mata uang dengan empat lapisan tertutup, setiap lapisan hanya memanggil lapisan di bawahnya |
| `aplikasi_terbuka.py` | Varian yang membiarkan lapisan presentasi memanggil lapisan persistensi langsung untuk pembacaan tanpa aturan bisnis |
| `periksa_lapisan.py` | Membaca kode tanpa menjalankannya, lalu melaporkan fungsi penerus, pelanggaran arah ketergantungan, dan jumlah fungsi per lapisan |
| `ukur_lapisan.py` | Menjalankan kedua jalur berulang kali, lalu melaporkan waktu median dan persentil ke-95 |

Seluruh skrip dijalankan dari direktori ini. Jalankan `python basis_data.py`
lebih dahulu agar berkas `kurs.db` terbentuk.

| Latihan | Masalah yang disasar | Berkas yang dipakai |
| --- | --- | --- |
| 1 | Lapisan yang hanya meneruskan panggilan | `periksa_lapisan.py` |
| 2 | Arah ketergantungan yang dilanggar | `periksa_lapisan.py` |
| 3 | Biaya waktu satu lompatan antar lapisan | `ukur_lapisan.py` |
