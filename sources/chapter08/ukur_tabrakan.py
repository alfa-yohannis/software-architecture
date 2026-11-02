"""Mengukur data collision, yaitu dua unit mengubah baris yang sama sekaligus.

Selama replication lag belum lewat, dua unit dapat mengubah baris kelas yang
sama tanpa saling mengetahui. Ketika pesan replikasinya tiba, perubahan yang
satu menimpa perubahan yang lain, sehingga satu kuota terjual dua kali.

Richards dan Ford memberi rumus pegangan untuk menaksir seringnya kejadian itu,
yaitu N dikali UR kuadrat dibagi S, lalu dikali RL. N adalah jumlah unit yang
berbagi cache, UR laju perubahan per detik, S jumlah baris di dalam cache, dan
RL replication lag dalam detik. Skrip ini menjalankan keadaan yang sama lalu
membandingkan cacahan nyatanya dengan taksiran rumus itu.

Cara menjalankan: python ukur_tabrakan.py
"""

import random
import threading
import time

import domain
import grid as modul_grid

MILIDETIK = 1000.0
# Lama setiap keadaan dijalankan, dalam detik.
LAMA_PUTARAN = 2.0
# Laju perubahan seluruh unit, dalam perubahan per detik.
LAJU_PERUBAHAN = 200
# Jumlah baris di dalam cache, yaitu banyaknya kelas yang diperebutkan.
JUMLAH_BARIS = 50
# Replication lag bawaan percobaan ini, dalam detik.
JEDA_BAKU = 0.100
# Jumlah unit bawaan percobaan ini.
UNIT_BAKU = 5
# Kuota besar agar kuotanya tidak habis sebelum putarannya selesai.
KUOTA_UKUR = 1000000

# Keadaan yang dicoba, masing-masing mengubah satu peubah saja.
KEADAAN = (
  ("acuan", UNIT_BAKU, JEDA_BAKU, JUMLAH_BARIS, LAJU_PERUBAHAN),
  ("lag 10 ms", UNIT_BAKU, 0.010, JUMLAH_BARIS, LAJU_PERUBAHAN),
  ("unit 2", 2, JEDA_BAKU, JUMLAH_BARIS, LAJU_PERUBAHAN),
  ("baris 10", UNIT_BAKU, JEDA_BAKU, 10, LAJU_PERUBAHAN),
  ("laju 400", UNIT_BAKU, JEDA_BAKU, JUMLAH_BARIS, 400),
)


def daftar_kelas_uji(jumlah_baris: int) -> list:
  """Menyusun nama kelas sebanyak baris yang diminta.

  Nama kelas dibuat sendiri agar jumlah barisnya dapat diatur, sebab jumlah
  baris itulah peubah S pada rumus taksiran. Mengembalikan list berisi kode
  kelas.
  """
  return [f"UJI{nomor:03d}" for nomor in range(jumlah_baris)]


def ubah_baris_acak(grid_unit: modul_grid.DataGrid, kelas_uji: list,
                    benih: int, jeda_antar_perubahan: float,
                    berhenti: threading.Event, pencacah: list,
                    kunci: threading.Lock) -> None:
  """Mengubah baris acak dengan laju tetap sampai tanda berhenti menyala.

  Pilihan barisnya diacak dengan benih tetap, sehingga putaran yang sama dapat
  diulang. Pencacah bersama dipakai agar laju nyata seluruh unit dapat dihitung
  sesudahnya. Tidak mengembalikan apa pun.
  """
  pengacak = random.Random(benih)
  nomor = 0
  while not berhenti.is_set():
    grid_unit.serap_replikasi()
    kode = pengacak.choice(kelas_uji)
    nomor += 1
    grid_unit.kurangi(domain.Request(nomor, "202600000", kode))
    with kunci:
      pencacah[0] += 1
    time.sleep(jeda_antar_perubahan)


def jalankan_satu_keadaan(nama: str, jumlah_unit: int, jeda: float,
                          jumlah_baris: int, laju: int) -> dict:
  """Menjalankan satu keadaan lalu mencacah tabrakan yang benar-benar terjadi.

  Setiap unit mengubah baris acak dengan laju yang dibagi rata, lalu menyerap
  replikasi dari unit lain. Mengembalikan dict berisi hasil cacahan, taksiran
  rumus, dan peubah yang dipakai.
  """
  saluran = modul_grid.SaluranReplikasi(jeda, jumlah_unit)
  kelas_uji = daftar_kelas_uji(jumlah_baris)
  daftar_grid = []
  for nomor in range(1, jumlah_unit + 1):
    grid_unit = modul_grid.DataGrid(f"unit-{nomor}", saluran, KUOTA_UKUR,
                                    nomor)
    grid_unit.sisa = {kode: KUOTA_UKUR for kode in kelas_uji}
    grid_unit.versi = {kode: domain.VERSI_AWAL for kode in kelas_uji}
    daftar_grid.append(grid_unit)

  berhenti = threading.Event()
  jeda_antar_perubahan = jumlah_unit / laju
  pencacah = [0]
  kunci = threading.Lock()

  daftar_utas = []
  for nomor, grid_unit in enumerate(daftar_grid, start=1):
    utas = threading.Thread(target=ubah_baris_acak,
                            args=(grid_unit, kelas_uji, nomor,
                                  jeda_antar_perubahan, berhenti, pencacah,
                                  kunci), daemon=True)
    utas.start()
    daftar_utas.append(utas)

  time.sleep(LAMA_PUTARAN)
  berhenti.set()
  for utas in daftar_utas:
    utas.join(timeout=1.0)
  time.sleep(jeda + 0.05)
  for grid_unit in daftar_grid:
    grid_unit.serap_replikasi()

  tabrakan = sum(grid_unit.jumlah_tabrakan for grid_unit in daftar_grid)
  perubahan = pencacah[0]
  laju_nyata = perubahan / LAMA_PUTARAN
  taksiran = jumlah_unit * (laju_nyata ** 2 / jumlah_baris) * jeda
  return {
    "nama": nama,
    "unit": jumlah_unit,
    "jeda": jeda,
    "baris": jumlah_baris,
    "laju": laju_nyata,
    "perubahan": perubahan,
    "tabrakan": tabrakan,
    "tabrakan_per_detik": tabrakan / LAMA_PUTARAN,
    "taksiran_per_detik": taksiran,
  }


if __name__ == "__main__":
  print(f"Lama tiap keadaan      : {LAMA_PUTARAN:.1f} detik")
  print("Rumus taksiran         : N x (UR kuadrat / S) x RL\n")
  print(f"{'Keadaan':<12}{'N':>3}{'RL ms':>7}{'S':>6}{'UR/detik':>10}"
        f"{'Tabrakan':>10}{'Per detik':>11}{'Taksiran':>11}")
  for keadaan in KEADAAN:
    hasil = jalankan_satu_keadaan(*keadaan)
    print(f"{hasil['nama']:<12}{hasil['unit']:>3}"
          f"{hasil['jeda'] * MILIDETIK:>7.0f}{hasil['baris']:>6}"
          f"{hasil['laju']:>10.1f}{hasil['tabrakan']:>10}"
          f"{hasil['tabrakan_per_detik']:>11.1f}"
          f"{hasil['taksiran_per_detik']:>11.1f}")
