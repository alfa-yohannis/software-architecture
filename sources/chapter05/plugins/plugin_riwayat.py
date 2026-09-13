"""Plugin yang menampilkan riwayat konversi lewat plugin lain.

Plugin ini memperlihatkan gunanya rujukan ke inti. Alih-alih menghitung sendiri,
setiap baris riwayat disusun dengan memanggil perintah konversi lewat inti.
Kedua plugin karena itu tetap tidak saling mengenal, sebab intilah perantaranya.

Cara menjalankan: python inti.py riwayat
"""

PERINTAH_PERANTARA = "konversi"
CONTOH_AWAL = [("USD", "IDR", "100"), ("EUR", "IDR", "50")]


class PluginRiwayat:
  """Menyimpan daftar konversi, lalu menampilkannya lewat perintah lain."""

  def __init__(self, inti) -> None:
    """Menyimpan rujukan inti dan mengisi riwayat dengan contoh awal.

    Rujukan inti di sini benar-benar dipakai, sebab plugin ini menyusun
    keluarannya lewat perintah milik plugin lain.
    """
    self.inti = inti
    self.riwayat = list(CONTOH_AWAL)

  def catat(self, kode_asal: str, kode_tujuan: str, nominal: str) -> None:
    """Menambahkan satu konversi ke dalam riwayat yang tersimpan di memori.

    Riwayatnya sengaja tidak ditulis ke berkas, sebab bab ini menyoroti cara
    plugin ditemukan, bukan cara datanya disimpan. Tidak mengembalikan apa pun.
    """
    self.riwayat.append((kode_asal, kode_tujuan, nominal))

  def jalankan(self, argumen: list[str]) -> str:
    """Menyusun riwayat dengan meminta inti menjalankan perintah konversi.

    Pemanggilan lewat inti membuat kedua plugin tetap tidak saling mengenal,
    sebab intilah perantaranya. Mengembalikan str berisi satu baris untuk
    setiap catatan riwayat.
    """
    baris = [self.inti.jalankan(PERINTAH_PERANTARA, list(catatan))
             for catatan in self.riwayat]
    return "\n".join(baris)
