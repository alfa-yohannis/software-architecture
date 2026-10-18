"""Proses middleware yang memegang ruang bersama lalu meminjamkannya ke unit.

Satu objek Ruang hanya hidup di dalam satu proses. Agar beberapa processing unit
dapat memakai ruang yang sama, objeknya dititipkan ke satu proses tersendiri,
lalu setiap unit memegang proksinya. Setiap pemanggilan lewat proksi berubah
menjadi satu bolak-balik lewat soket, sehingga biayanya puluhan mikrodetik, jauh
lebih murah daripada satu commit ke berkas basis data.

Proses inilah yang pada Bab ini mewakili middleware tervirtualisasi. Isinya
belum lengkap, sebab hanya ada grid data dan grid pesan. Grid pemrosesan dan
deployment manager tidak dibuat, sebab keduanya hanya masuk akal pada beberapa
mesin sekaligus.

Cara menjalankan: python layanan_ruang.py
"""

import multiprocessing.managers

import domain
import ruang

# Alamat kosong berarti sistem operasi yang memilih porta yang masih menganggur.
# Porta yang terpilih dibaca kembali lewat atribut address, lalu diwariskan ke
# setiap unit.
ALAMAT_BEBAS = ("127.0.0.1", 0)
KUNCI = b"ruang-bab08"

# Satu-satunya ruang bersama di dalam proses middleware. Objeknya dibuat saat
# modul diimpor, bukan saat diminta, sehingga penyambung keberapa pun menerima
# proksi ke objek yang sama. Tanpa ini setiap penyambung akan memperoleh ruang
# barunya sendiri, dan tupel yang ditulis satu unit tidak pernah terlihat unit
# lain.
RUANG_BERSAMA = ruang.Ruang()


def ambil_ruang() -> ruang.Ruang:
  """Menyerahkan ruang bersama yang sudah ada, bukan membuat yang baru.

  Fungsi inilah yang didaftarkan ke manager, sehingga pendaftarannya berperan
  sebagai pencari, bukan sebagai pabrik. Mengembalikan objek Ruang tunggal milik
  proses middleware.
  """
  return RUANG_BERSAMA


class LayananRuang(multiprocessing.managers.BaseManager):
  """Manager yang menyalakan proses middleware beserta ruang di dalamnya.

  Kelas ini sengaja kosong. Isinya ditentukan oleh pendaftaran di bawah, yang
  membuat pemanggilan LayananRuang().ambil_ruang() menghasilkan proksi ke ruang
  bersama di dalam proses middleware.
  """


LayananRuang.register("ambil_ruang", callable=ambil_ruang)


def mulai_layanan() -> tuple[LayananRuang, object, tuple]:
  """Menyalakan proses middleware, membuat ruang, lalu mengisinya dengan kurs.

  Kurs diisikan di sini karena ruang harus sudah berisi kurs sebelum satu unit
  pun menyalin grid memorinya. Mengembalikan tuple berisi objek manager, proksi
  ruang, dan alamat soketnya yang dipakai unit untuk menyambung.
  """
  layanan = LayananRuang(address=ALAMAT_BEBAS, authkey=KUNCI)
  layanan.start()
  ruang_bersama = layanan.ambil_ruang()
  for tupel in domain.tupel_kurs():
    ruang_bersama.tulis(tupel)
  return layanan, ruang_bersama, layanan.address


def sambung_layanan(alamat: tuple) -> tuple[LayananRuang, object]:
  """Menyambung ke proses middleware yang sudah berjalan dari proses lain.

  Dipanggil setiap processing unit tepat setelah lahir, sebab proksi tidak dapat
  diwariskan lewat argumen proses pada semua sistem. Mengembalikan tuple berisi
  objek manager dan proksi ruang yang sama dengan milik pemanggil pertama.
  """
  layanan = LayananRuang(address=alamat, authkey=KUNCI)
  layanan.connect()
  return layanan, layanan.ambil_ruang()


if __name__ == "__main__":
  manager, ruang_uji, alamat_uji = mulai_layanan()
  print(f"Middleware menyala di porta : {alamat_uji[1] > 0}")
  # Keluarannya: Middleware menyala di porta : True
  print(f"Tupel kurs di dalam ruang   : {ruang_uji.hitung(domain.POLA_KURS)}")
  # Keluarannya: Tupel kurs di dalam ruang   : 3
  _, ruang_kedua = sambung_layanan(alamat_uji)
  ruang_kedua.tulis(("tugas", 1, "USD", "IDR", 10))
  print(f"Tugas terlihat dari proksi  : {ruang_uji.hitung(domain.POLA_TUGAS)}")
  # Keluarannya: Tugas terlihat dari proksi  : 1
  manager.shutdown()
