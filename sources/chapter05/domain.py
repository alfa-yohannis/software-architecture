"""Logika inti konversi mata uang, dipakai bersama oleh plugin bab ini.

Berkas ini sengaja kecil dan tidak mengenal satu pun plugin. Isinya hanya tabel
kurs beserta satu fungsi hitung, sehingga bab ini dapat menitikberatkan cara
plugin ditemukan dan dijalankan, bukan rumus konversinya.

Cara menjalankan: berkas ini diimpor, bukan dijalankan langsung.
"""

KURS = {
  ("USD", "IDR"): 16250.0,
  ("EUR", "IDR"): 17600.0,
  ("SGD", "IDR"): 12100.0,
}


def nilai_kurs(kode_asal, kode_tujuan):
  """Mengembalikan kurs satu pasangan mata uang, atau None bila tidak ada."""
  return KURS.get((kode_asal, kode_tujuan))


def hitung_konversi(kode_asal, kode_tujuan, nominal):
  """Mengalikan nominal dengan kursnya, lalu menolak nominal yang tidak wajar."""
  if nominal <= 0:
    raise ValueError("Nominal harus lebih besar dari nol")
  kurs = nilai_kurs(kode_asal, kode_tujuan)
  if kurs is None:
    raise LookupError(f"Kurs {kode_asal} ke {kode_tujuan} tidak tersedia")
  return nominal * kurs
