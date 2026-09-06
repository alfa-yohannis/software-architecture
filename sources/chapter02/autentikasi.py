"""Pemeriksaan autentikasi dan otorisasi untuk lapisan bisnis.

Autentikasi menjawab pertanyaan siapa pemanggilnya. Otorisasi menjawab
pertanyaan apakah pemanggil tersebut berhak. Keduanya dipisahkan menjadi dua
metode agar terlihat bahwa jalan pintas melewatkan dua pemeriksaan, bukan satu.
Kelas PenjagaAkses menjadi kolaborator lapisan bisnis, bukan lapisan tersendiri,
sebab tugasnya menegakkan aturan bisnis tentang siapa yang boleh membaca apa.

Cara menjalankan: python autentikasi.py
"""

import hashlib

# Token disimpan sebagai ringkasan, bukan sebagai teks biasa.
PENGGUNA = {
  hashlib.sha256(b"token-andi").hexdigest(): {"nama": "andi", "peran": "staf"},
  hashlib.sha256(b"token-budi").hexdigest(): {"nama": "budi", "peran": "tamu"},
}

PERAN_BOLEH_MEMBACA = {"staf", "admin"}


class PenjagaAkses:
  """Pemeriksa identitas dan hak pemanggil.

  Daftar pengguna dan daftar peran diterima lewat konstruktor, sehingga
  pengujian dapat menyusun daftarnya sendiri tanpa mengubah kelas ini.
  """

  def __init__(self, pengguna=PENGGUNA, peran_boleh_membaca=PERAN_BOLEH_MEMBACA):
    """Menyimpan daftar pengguna dan daftar peran yang berhak membaca."""
    self.pengguna = pengguna
    self.peran_boleh_membaca = peran_boleh_membaca

  def periksa_token(self, token):
    """Mengembalikan data pengguna bila token dikenali, atau None bila tidak.

    Perhitungan ringkasan sengaja dilakukan setiap kali, sebab beban itulah
    yang dilewati jalan pintas dan menjadi bagian dari yang diukur.
    """
    return self.pengguna.get(hashlib.sha256(token.encode()).hexdigest())

  def boleh_membaca(self, pengguna):
    """Menentukan apakah peran pengguna berhak membaca daftar kurs jual."""
    return pengguna["peran"] in self.peran_boleh_membaca


if __name__ == "__main__":
  penjaga = PenjagaAkses()
  print(penjaga.periksa_token("token-andi"))
  # Keluarannya: {'nama': 'andi', 'peran': 'staf'}
  print(penjaga.periksa_token("token-palsu"))
  # Keluarannya: None
