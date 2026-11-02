"""Mengukur stale read, yaitu pembacaan yang memakai angka yang sudah tertinggal.

Satu unit mengubah sisa kuota terus-menerus, sedangkan unit lain membacanya
dari grid memorinya sendiri. Selama replication lag belum lewat, pembaca masih
melihat angka lama, dan pembacaan itulah yang dicacah sebagai stale read.

Yang diubah pada percobaan ini hanya replication lag. Jedanya dinaikkan dari
nol sampai dua ratus milidetik, sehingga terlihat bahwa jarak itulah yang
menentukan jauhnya angka yang tertinggal, bukan beban mesinnya.

Cara menjalankan: python ukur_stale_read.py
"""

import threading
import time

import domain
import grid as modul_grid
import sebaran

MILIDETIK = 1000.0
# Replication lag yang dicoba, dalam milidetik.
JEDA_DICOBA = (0, 10, 25, 50, 100, 200)
# Lama satu putaran pengukuran untuk setiap jeda, dalam detik.
LAMA_PUTARAN = 1.0
# Jarak antar perubahan yang dilakukan penulis, dalam detik.
JEDA_TULIS = 0.002
# Jarak antar pembacaan, dipilih agar pembacaannya meniru pemakai, bukan
# perulangan yang berlari secepat mungkin.
JEDA_BACA = 0.001
# Kelas yang dipantau, yaitu satu kelas saja agar perbandingannya jelas.
KELAS_DIPANTAU = sorted(domain.KUOTA_AWAL)[0]
# Kuota besar agar kuotanya tidak habis sebelum putarannya selesai.
KUOTA_UKUR = 100000


def menulis_terus(grid_penulis: modul_grid.DataGrid,
                  berhenti: threading.Event) -> None:
  """Mengurangi kuota kelas yang dipantau sampai tanda berhenti menyala.

  Penulisnya dijalankan pada thread tersendiri, sehingga pembacanya dapat
  mengambil cuplikan kapan saja di tengah perubahan. Tidak mengembalikan apa
  pun.
  """
  nomor_request = 0
  while not berhenti.is_set():
    nomor_request += 1
    request = domain.Request(nomor_request, "202600000", KELAS_DIPANTAU)
    grid_penulis.kurangi(request)
    time.sleep(JEDA_TULIS)


def jalankan_satu_jeda(jeda_milidetik: int) -> dict:
  """Menjalankan satu putaran penulisan dan pembacaan pada satu jeda tertentu.

  Penulis mengurangi kuota berkala, sedangkan pembaca membandingkan angka di
  grid-nya dengan angka terbaru milik penulis. Mengembalikan dict berisi jumlah
  pembacaan, pembacaan basi, bagiannya, dan selisih terbesar yang terlihat.
  """
  saluran = modul_grid.SaluranReplikasi(jeda_milidetik / MILIDETIK, 2)
  grid_penulis = modul_grid.DataGrid("unit-penulis", saluran, KUOTA_UKUR, 1)
  grid_pembaca = modul_grid.DataGrid("unit-pembaca", saluran, KUOTA_UKUR, 2)
  berhenti = threading.Event()

  utas_penulis = threading.Thread(target=menulis_terus,
                                  args=(grid_penulis, berhenti), daemon=True)
  utas_penulis.start()

  jumlah_baca = 0
  jumlah_stale = 0
  daftar_selisih = []
  batas = time.monotonic() + LAMA_PUTARAN
  while time.monotonic() < batas:
    grid_pembaca.serap_replikasi()
    terlihat = grid_pembaca.baca(KELAS_DIPANTAU)
    sebenarnya = grid_penulis.baca(KELAS_DIPANTAU)
    jumlah_baca += 1
    selisih = terlihat - sebenarnya
    daftar_selisih.append(selisih)
    if selisih != 0:
      jumlah_stale += 1
    time.sleep(JEDA_BACA)

  berhenti.set()
  utas_penulis.join(timeout=1.0)
  bagian = (jumlah_stale / jumlah_baca * 100.0) if jumlah_baca else 0.0
  ringkasan = sebaran.ringkas(daftar_selisih)
  return {
    "jeda": jeda_milidetik,
    "baca": jumlah_baca,
    "stale": jumlah_stale,
    "bagian": bagian,
    "selisih_median": ringkasan["median"],
    "selisih_terbesar": ringkasan["terbesar"],
  }


if __name__ == "__main__":
  print(f"Kelas dipantau         : {KELAS_DIPANTAU}")
  print(f"Lama tiap putaran      : {LAMA_PUTARAN:.1f} detik")
  print(f"Jarak antar perubahan  : {JEDA_TULIS * MILIDETIK:.0f} ms\n")
  for jeda in JEDA_DICOBA:
    hasil = jalankan_satu_jeda(jeda)
    print(f"Replication lag {hasil['jeda']:3d} ms"
          f"  pembacaan {hasil['baca']:6d}"
          f"  stale read {hasil['bagian']:5.1f} persen"
          f"  selisih median {hasil['selisih_median']:5.1f} kuota"
          f"  terbesar {hasil['selisih_terbesar']:4.0f} kuota")
