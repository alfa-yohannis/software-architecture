"""Menghitung titik sentuh satu penambahan pada repositori yang sudah ada.

Titik sentuh adalah baris kode yang menyebut satu hal secara langsung, misalnya
kode bahasa "vi" atau nama negara "Vietnam". Semakin banyak modul yang memuat
titik sentuh, semakin besar peluang satu penambahan terlewat di salah satunya.

Angka inilah keadaan awal pada dimensi maintainability. Sesudah pengetahuan itu
dipusatkan ke satu registri, skrip yang sama dijalankan lagi, lalu kedua
angkanya dibandingkan. Klaim yang hendak dibuktikan karena itu dapat dihitung,
bukan dirasakan.

Penandanya ditentukan dari baris perintah, sehingga skrip ini dapat dipakai
untuk penambahan apa pun, misalnya bahasa, negara, format dokumen, atau
backend model.

Cara menjalankan:
  python ukur_titik_sentuh.py exim/app "vi" "en" "id"
  python ukur_titik_sentuh.py exim/app Vietnam Indonesia
"""

import os
import sys

# Direktori paket yang diperiksa bila tidak disebutkan di baris perintah.
JALUR_BAKU = "exim/app"
# Penanda bawaan, yaitu ketiga kode bahasa yang didukung Exim saat ini.
PENANDA_BAKU = ("\"id\"", "\"en\"", "\"vi\"")
# Akhiran berkas yang diperiksa. Berkas antarmuka ikut dimasukkan, sebab
# sebagian penambahan menyentuh gaya tampilan, bukan hanya kode Python.
AKHIRAN_SUMBER = (".py", ".css", ".js", ".html")
# Lebar kolom nama modul pada tabel keluaran.
LEBAR_NAMA = 18


def cari_titik_sentuh(jalur_berkas: str, daftar_penanda: tuple) -> list:
  """Mencari baris yang memuat salah satu penanda pada satu berkas.

  Pencariannya memakai pencocokan teks biasa, sebab yang dihitung memang
  penyebutan harfiah, termasuk yang berada di dalam komentar dan docstring.
  Mengembalikan list berisi tuple nomor baris dan isi barisnya.
  """
  berkas = open(jalur_berkas, encoding="utf-8")
  isi = berkas.read()
  berkas.close()
  temuan = []
  for nomor, baris in enumerate(isi.splitlines(), start=1):
    for penanda in daftar_penanda:
      if penanda in baris:
        temuan.append((nomor, baris.strip()))
        break
  return temuan


def kumpulkan_titik_sentuh(jalur_paket: str, daftar_penanda: tuple) -> dict:
  """Memeriksa seluruh modul di dalam satu paket.

  Mengembalikan dict berisi nama modul dan daftar temuannya, hanya untuk modul
  yang memuat sedikitnya satu titik sentuh.
  """
  hasil = {}
  for nama_berkas in sorted(os.listdir(jalur_paket)):
    if not nama_berkas.endswith(AKHIRAN_SUMBER):
      continue
    jalur_berkas = os.path.join(jalur_paket, nama_berkas)
    temuan = cari_titik_sentuh(jalur_berkas, daftar_penanda)
    if temuan:
      hasil[nama_berkas] = temuan
  return hasil


def cetak_tabel(hasil: dict) -> None:
  """Mencetak jumlah titik sentuh tiap modul beserta baris pertamanya.

  Baris pertama disertakan agar pembaca dapat segera membuka berkasnya dan
  melihat bentuk penyebutannya. Tidak mengembalikan apa pun.
  """
  print(f"{'Berkas':<{LEBAR_NAMA}}{'Titik sentuh':>14}  Baris pertama")
  for nama_modul, temuan in hasil.items():
    nomor_pertama, isi_pertama = temuan[0]
    potongan = isi_pertama[:44]
    print(f"{nama_modul:<{LEBAR_NAMA}}{len(temuan):>14}  "
          f"baris {nomor_pertama}: {potongan}")


def cetak_ringkasan(hasil: dict, daftar_penanda: tuple) -> None:
  """Mencetak jumlah modul dan jumlah baris yang harus disentuh.

  Tidak mengembalikan apa pun.
  """
  jumlah_modul = len(hasil)
  jumlah_baris = sum(len(temuan) for temuan in hasil.values())
  print()
  print(f"Penanda dicari      : {', '.join(daftar_penanda)}")
  print(f"Berkas tersentuh    : {jumlah_modul}")
  print(f"Baris tersentuh     : {jumlah_baris}")
  print("Satu penambahan harus memeriksa seluruh modul di atas, dan modul "
        "yang terlewat menjadi cacat yang baru terlihat saat dipakai.")


if __name__ == "__main__":
  if len(sys.argv) > 1:
    jalur_paket_utama = sys.argv[1]
  else:
    jalur_paket_utama = JALUR_BAKU
  if len(sys.argv) > 2:
    penanda_utama = tuple(sys.argv[2:])
  else:
    penanda_utama = PENANDA_BAKU
  print(f"Paket diperiksa     : {jalur_paket_utama}\n")
  hasil_utama = kumpulkan_titik_sentuh(jalur_paket_utama, penanda_utama)
  cetak_tabel(hasil_utama)
  cetak_ringkasan(hasil_utama, penanda_utama)
