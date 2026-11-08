"""Mengukur stale read, yaitu pembacaan yang memakai angka yang sudah tertinggal.

Satu unit mengubah sisa kuota terus-menerus, sedangkan unit lain membacanya
dari grid memorinya sendiri. Selama replication lag belum lewat, pembaca masih
melihat angka lama, dan pembacaan itulah yang dicacah sebagai stale read.

Dua hal diubah pada percobaan ini. Replication lag dinaikkan dari nol sampai
dua ratus milidetik, dan jarak antar perubahan dicoba dua macam. Jarak dua
milidetik meniru menit pertama pembukaan pengisian rencana studi, sedangkan
jarak lima puluh milidetik meniru hari-hari sesudahnya. Bagian pembacaan yang
basi ditentukan perbandingan keduanya, bukan oleh lag-nya saja.

Cara menjalankan: python ukur_stale_read.py
"""

import threading
import time

import domain
import grid as modul_grid
import sebaran

MILIDETIK = 1000.0
PERSEN = 100.0
# Replication lag yang dicoba, dalam milidetik.
JEDA_DICOBA = (0, 10, 25, 50, 100, 200)
# Jarak antar perubahan yang dilakukan penulis, dalam detik, beserta namanya.
JEDA_TULIS_DICOBA = (
  (0.002, "jam pembukaan"),
  (0.050, "hari biasa"),
)
# Lama satu putaran pengukuran untuk setiap pasangan jeda, dalam detik.
LAMA_PUTARAN = 1.0
# Jarak antar pembacaan, dipilih agar pembacaannya meniru pemakai, bukan
# perulangan yang berlari secepat mungkin.
JEDA_BACA = 0.001
# Lama menunggu thread penulis selesai sesudah tanda berhenti dinyalakan.
BATAS_TUNGGU_PENULIS = 1.0
# Kelas yang dipantau, yaitu satu kelas saja agar perbandingannya jelas.
KELAS_DIPANTAU = sorted(domain.KUOTA_AWAL)[0]
# Kuota besar agar kuotanya tidak habis sebelum putarannya selesai.
KUOTA_UKUR = 100000
# Nomor induk yang dipakai penulis, sebab yang diukur hanya sisa kuotanya.
NIM_PENULIS = "202600000"


def menulis_terus(grid_penulis: modul_grid.DataGrid, jeda_tulis: float,
                  berhenti: threading.Event, pencacah: list) -> None:
  """Mengurangi kuota kelas yang dipantau sampai tanda berhenti menyala.

  Penulisnya dijalankan pada thread tersendiri, sehingga pembacanya dapat
  mengambil cuplikan kapan saja di tengah perubahan. Pencacah dipakai agar
  banyaknya perubahan nyata dapat dilaporkan, bukan hanya jarak yang diminta.
  Tidak mengembalikan apa pun.
  """
  nomor_request = 0
  while not berhenti.is_set():
    nomor_request += 1
    request = domain.Request(nomor_request, NIM_PENULIS, KELAS_DIPANTAU)
    grid_penulis.kurangi(request)
    pencacah[0] += 1
    time.sleep(jeda_tulis)


def jalankan_satu_jeda(jeda_milidetik: int, jeda_tulis: float) -> dict:
  """Menjalankan satu putaran penulisan dan pembacaan pada satu pasangan jeda.

  Penulis mengurangi kuota berkala, sedangkan pembaca membandingkan angka di
  grid-nya dengan angka terbaru milik penulis. Mengembalikan dict berisi jumlah
  pembacaan, jumlah perubahan, bagian pembacaan yang basi, dan sebaran selisih
  kuota yang terlihat.
  """
  saluran = modul_grid.SaluranReplikasi(jeda_milidetik / MILIDETIK, 2)
  grid_penulis = modul_grid.DataGrid("unit-penulis", saluran, KUOTA_UKUR, 1)
  grid_pembaca = modul_grid.DataGrid("unit-pembaca", saluran, KUOTA_UKUR, 2)
  berhenti = threading.Event()
  pencacah = [0]

  utas_penulis = threading.Thread(
    target=menulis_terus, args=(grid_penulis, jeda_tulis, berhenti, pencacah),
    daemon=True)
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
  utas_penulis.join(timeout=BATAS_TUNGGU_PENULIS)
  saluran.tutup()
  bagian = 0.0
  if jumlah_baca:
    bagian = jumlah_stale / jumlah_baca * PERSEN
  ringkasan = sebaran.ringkas(daftar_selisih)
  return {
    "jeda": jeda_milidetik,
    "baca": jumlah_baca,
    "perubahan": pencacah[0],
    "bagian": bagian,
    "selisih_median": ringkasan["median"],
    "selisih_terbesar": ringkasan["terbesar"],
  }


def cetak_judul_tabel() -> None:
  """Mencetak baris judul tabel, sekali untuk setiap jarak antar perubahan.

  Selisih adalah banyaknya kuota yang masih terlihat tersedia oleh pembaca,
  padahal sudah diambil di unit penulis. Tidak mengembalikan apa pun.
  """
  print(f"{'Lag ms':>6} {'Pembacaan':>10} {'Perubahan':>10} "
        f"{'Stale read':>11} {'Selisih median':>15} {'Terbesar':>9}")


if __name__ == "__main__":
  print(f"Kelas dipantau    : {KELAS_DIPANTAU}")
  print(f"Lama tiap putaran : {LAMA_PUTARAN:.1f} detik")
  for jeda_tulis, nama_jeda in JEDA_TULIS_DICOBA:
    print(f"\nSatu perubahan tiap {jeda_tulis * MILIDETIK:.0f} ms, "
          f"seperti {nama_jeda}")
    cetak_judul_tabel()
    for jeda in JEDA_DICOBA:
      hasil = jalankan_satu_jeda(jeda, jeda_tulis)
      print(f"{hasil['jeda']:>6} {hasil['baca']:>10} "
            f"{hasil['perubahan']:>10} {hasil['bagian']:>9.1f} % "
            f"{hasil['selisih_median']:>15.1f} "
            f"{hasil['selisih_terbesar']:>9.0f}")
  # Keluarannya, baris lag 100 ms pada jam pembukaan:
  #    100        910        479     100.0 %            48.0        49
