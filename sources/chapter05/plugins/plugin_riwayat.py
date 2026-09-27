"""Plugin yang menampilkan riwayat konversi lewat plugin lain.

Plugin ini memperlihatkan gunanya rujukan ke core. Alih-alih menghitung sendiri,
setiap baris riwayat disusun dengan memanggil perintah konversi lewat core.
Kedua plugin karena itu tetap tidak saling mengenal, sebab core-lah perantaranya.

Cara menjalankan: python inti.py riwayat
"""

PERINTAH_PERANTARA = "konversi"
CONTOH_AWAL = [("USD", "IDR", "100"), ("EUR", "IDR", "50")]


class HistoryPlugin:
  """Menyimpan daftar konversi, lalu menampilkannya lewat perintah lain."""

  def __init__(self, inti) -> None:
    """Menyimpan rujukan core dan mengisi riwayat dengan contoh awal.

    Rujukan core di sini benar-benar dipakai, sebab plugin ini menyusun
    keluarannya lewat perintah milik plugin lain.
    """
    self.inti = inti
    self.riwayat = list(CONTOH_AWAL)

  def catat(self, kode_asal: str, kode_tujuan: str, nominal: str) -> None:
    """Menambahkan satu konversi ke dalam riwayat yang tersimpan di memori.

    Riwayatnya sengaja tidak ditulis ke file, sebab bab ini menyoroti cara
    plugin ditemukan, bukan cara datanya disimpan. Tidak mengembalikan apa pun.
    """
    self.riwayat.append((kode_asal, kode_tujuan, nominal))

  def jalankan(self, argumen: list[str]) -> str:
    """Menyusun riwayat dengan meminta core menjalankan perintah konversi.

    Pemanggilan lewat core membuat kedua plugin tetap tidak saling mengenal,
    sebab core-lah perantaranya. Mengembalikan str berisi satu baris untuk
    setiap catatan riwayat.
    """
    baris = []
    for catatan in self.riwayat:
      argumen_konversi = list(catatan)
      hasil = self.inti.jalankan(PERINTAH_PERANTARA, argumen_konversi)
      baris.append(hasil)
    return "\n".join(baris)
