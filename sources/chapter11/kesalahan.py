"""Jenis kesalahan yang dipakai bersama oleh ketiga bidang domain.

Kesalahan sengaja dikumpulkan pada modul tanpa ketergantungan apa pun, agar
modul domain maupun modul web dapat mengimpornya tanpa saling mengenal. Tiap
jenis kesalahan dipetakan ke satu kode status HTTP di sarana.py, sehingga
bidang domain tidak perlu menyebut angka status sama sekali.

Berkas ini tidak dijalankan sendiri, melainkan diimpor modul lain.
"""


class TidakDitemukan(Exception):
  """Data yang diminta memang tidak ada di dalam basis data.

  Dipakai ketika kode mata uang, nomor pesanan, atau nomor tagihan tidak
  terdaftar. Pemanggil menjawabnya dengan status 404, bukan 500, sebab
  permintaannya sah dan yang kosong hanyalah datanya.
  """


class AturanDilanggar(Exception):
  """Permintaan ditolak oleh aturan bisnis, bukan oleh kesalahan teknis.

  Contohnya menagih pesanan yang sudah dibatalkan. Kesalahan jenis ini
  dijawab dengan status 409, sehingga pemanggil tahu bahwa mengulang
  permintaan yang sama tidak akan menolong.
  """


class LayananTakTerjangkau(Exception):
  """Satu layanan domain tidak menjawab panggilan gerbang.

  Kesalahan ini hanya mungkin muncul pada versi service-based, sebab versi
  monolit memanggil bidangnya lewat pemanggilan fungsi biasa. Kemunculannya
  itulah yang dihitung pada skrip uji_kegagalan.py.
  """
