"""Pemeriksaan autentikasi dan otorisasi untuk lapisan bisnis.

Autentikasi menjawab pertanyaan siapa pemanggilnya. Otorisasi menjawab
pertanyaan apakah pemanggil tersebut berhak. Keduanya dipisahkan agar terlihat
bahwa jalur pintas melewatkan dua pemeriksaan, bukan satu.

Cara menjalankan: python autentikasi.py
"""

import hashlib

# Token disimpan sebagai ringkasan, bukan sebagai teks biasa.
PENGGUNA = {
  hashlib.sha256(b"token-andi").hexdigest(): {"nama": "andi", "peran": "staf"},
  hashlib.sha256(b"token-budi").hexdigest(): {"nama": "budi", "peran": "tamu"},
}

PERAN_BOLEH_MEMBACA = {"staf", "admin"}


def periksa_token(token):
  """Mengembalikan data pengguna bila token dikenali, atau None bila tidak.

  Perhitungan ringkasan sengaja dilakukan setiap kali, sebab beban itulah yang
  dilewati jalur pintas dan menjadi bagian dari yang diukur.
  """
  return PENGGUNA.get(hashlib.sha256(token.encode()).hexdigest())


def boleh_membaca(pengguna):
  """Menentukan apakah peran pengguna berhak membaca daftar kurs."""
  return pengguna["peran"] in PERAN_BOLEH_MEMBACA


if __name__ == "__main__":
  print(periksa_token("token-andi"))
  # Keluarannya: {'nama': 'andi', 'peran': 'staf'}
  print(periksa_token("token-palsu"))
  # Keluarannya: None
