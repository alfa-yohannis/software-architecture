"""Menguji pertanyaan yang hanya menyebut sebagian nama kunci.

Lookup biasa menyebut nama kunci selengkapnya, misalnya USD/IDR. Pertanyaan
sehari-hari sering tidak selengkap itu, misalnya "seluruh kunci yang memuat
USD". Ketiga susunan menjawab pertanyaan seperti itu dengan cara yang sangat
berbeda, dan perbedaan itulah yang menjelaskan mengapa query flooding masih
dipakai walaupun pesannya paling mahal.

Susunan client-server menjawab murah, sebab indeksnya memegang seluruh kunci
sehingga dapat memindainya sendiri. Susunan unstructured menjawab dengan
bertanya kepada seluruh node, sebab setiap node dapat memindai titipannya
sendiri. Susunan structured tidak dapat menjawab sama sekali lewat satu lookup,
sebab letak kunci dihitung dari hash nama yang lengkap, dan hash potongan nama
menunjuk titik yang tidak ada hubungannya.

Cara menjalankan:
  python uji_pencarian_sebagian.py
  python uji_pencarian_sebagian.py JPY
"""

import sys

import cincin
import domain
import susunan

TEKS_BAKU = "USD"
NOMOR_PEMINTA = 3
PESAN_PER_TANYA = 2


def cocokkan_titipan(simpul, teks: str) -> list[str]:
  """Memindai titipan satu node lalu mengumpulkan kunci yang memuat teks.

  Pemindaian hanya mungkin pada node yang benar-benar memegang kuncinya.
  Mengembalikan list berisi nama kunci yang cocok, dan kosong bila tidak ada.
  """
  cocok = []
  for kunci in simpul.simpanan:
    if teks in kunci:
      cocok.append(kunci)
  return cocok


def cari_lewat_indeks(jaringan_ini, teks: str) -> dict:
  """Menanyakan potongan nama kepada satu node indeks saja.

  Indeks memegang seluruh kunci, sehingga pemindaiannya cukup sekali.
  Mengembalikan dict berisi jumlah kunci yang ketemu dan jumlah pesannya.
  """
  indeks = jaringan_ini.simpul[0]
  cocok = cocokkan_titipan(indeks, teks)
  return {"ketemu": len(cocok), "pesan": PESAN_PER_TANYA}


def cari_lewat_penyebaran(jaringan_ini, teks: str) -> dict:
  """Menanyakan potongan nama kepada seluruh node selain peminta.

  Setiap node memindai titipannya sendiri lalu menjawab, sehingga pertanyaannya
  tidak perlu menyebut nama kunci selengkapnya. Mengembalikan dict berisi jumlah
  kunci yang ketemu dan jumlah pesannya.
  """
  ketemu = 0
  pesan = 0
  peminta = jaringan_ini.simpul[NOMOR_PEMINTA]
  cocok_sendiri = cocokkan_titipan(peminta, teks)
  ketemu += len(cocok_sendiri)
  for simpul in jaringan_ini.simpul:
    if simpul.nomor == peminta.nomor:
      continue
    pesan += PESAN_PER_TANYA
    cocok = cocokkan_titipan(simpul, teks)
    ketemu += len(cocok)
  return {"ketemu": ketemu, "pesan": pesan}


def cari_lewat_ring(jaringan_ini, teks: str) -> dict:
  """Memperlakukan potongan nama seperti kunci utuh, lalu menelusuri ring.

  Hasilnya hampir selalu kosong, sebab titik hash potongan nama tidak ada
  hubungannya dengan titik kunci yang memuat potongan itu. Mengembalikan dict
  berisi jumlah kunci yang ketemu beserta jumlah pesan yang telanjur dipakai.
  """
  hasil = jaringan_ini.cari(NOMOR_PEMINTA, teks)
  ketemu = 0
  if hasil.terjawab:
    ketemu = 1
  return {"ketemu": ketemu, "pesan": hasil.pesan}


def laporkan(teks: str) -> None:
  """Mencetak hasil ketiga susunan untuk satu potongan nama yang sama.

  Tidak mengembalikan apa pun, sebab keluarannya memang dibaca langsung oleh
  mahasiswa pada lembar isian latihan.
  """
  daftar_kunci = domain.daftar_kunci()
  sasaran = 0
  for kunci in daftar_kunci:
    if teks in kunci:
      sasaran += 1

  jaringan_indeks = susunan.bangun("indeks")
  jaringan_tetangga = susunan.bangun("tetangga")
  jaringan_cincin = susunan.bangun("cincin")
  hasil_indeks = cari_lewat_indeks(jaringan_indeks, teks)
  hasil_tetangga = cari_lewat_penyebaran(jaringan_tetangga, teks)
  hasil_cincin = cari_lewat_ring(jaringan_cincin, teks)

  print(f"Potongan nama dicari       : {teks}")
  print(f"Kunci yang memuatnya       : {sasaran} dari {len(daftar_kunci)}")
  print(f"Client-server ketemu       : {hasil_indeks['ketemu']}"
        f" ({hasil_indeks['pesan']} pesan)")
  # Keluarannya: Client-server ketemu       : 1 (2 pesan)
  print(f"Unstructured ketemu        : {hasil_tetangga['ketemu']}"
        f" ({hasil_tetangga['pesan']} pesan)")
  # Keluarannya: Unstructured ketemu        : 1 (14 pesan)
  print(f"Structured ketemu          : {hasil_cincin['ketemu']}"
        f" ({hasil_cincin['pesan']} pesan)")
  # Keluarannya: Structured ketemu          : 0 (6 pesan)


def baca_teks(argumen: list[str]) -> str:
  """Membaca potongan nama dari argumen baris perintah.

  Tanpa argumen, dipakai potongan nama baku. Mengembalikan str berisi potongan
  nama yang akan dicari.
  """
  if len(argumen) < 2:
    return TEKS_BAKU
  return argumen[1]


if __name__ == "__main__":
  teks_dicari = baca_teks(sys.argv)
  laporkan(teks_dicari)
