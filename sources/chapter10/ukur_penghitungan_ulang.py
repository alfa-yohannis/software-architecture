"""Mengukur waktu menyusun kembali model baca dari event log.

Tiga panjang log diuji, yaitu seribu, sepuluh ribu, dan seratus ribu event.
Setiap panjang diukur dua kali, yaitu tanpa snapshot dan dengan snapshot.
Snapshot dipasang pada event ke-(n minus 250), sehingga jalur bersnapshot
selalu menyisakan dua ratus lima puluh event untuk dilipat, berapa pun
panjang lognya.

Pengukuran diulang seratus putaran untuk setiap keadaan, sebab satu putaran
tidak cukup untuk menyimpulkan apa pun.

Cara menjalankan: python ukur_penghitungan_ulang.py
"""

import time

import domain
import sebaran
import versi_event

UKURAN_LOG = (1_000, 10_000, 100_000)
EVENT_SESUDAH_SNAPSHOT = 250
PUTARAN = 100
MILIDETIK = 1000.0
LEBAR_LABEL = 36
# Perintah dibangkitkan berlebih lalu disaring, sebab sebagian ditolak aturan
# bisnis. Pengali berikut cukup untuk menutupi penolakan tersebut.
PENGALI_CADANGAN = 1.4


def angka_id(nilai: int) -> str:
  """Menulis bilangan dengan titik sebagai pemisah ribuan.

  Bentuk ini disamakan dengan penulisan angka pada naskah bab, sehingga baris
  keluaran dapat disalin apa adanya ke lembar isian. Mengembalikan str berisi
  bilangan yang sudah berpemisah.
  """
  return f"{nilai:,}".replace(",", ".")


def pilih_perintah_sah(jumlah: int) -> list[domain.Perintah]:
  """Menyaring perintah yang lolos aturan bisnis sampai jumlahnya tercapai.

  Log event hanya boleh memuat perintah yang benar-benar diterima, sebab
  event adalah fakta yang sudah terjadi, bukan permintaan. Mengembalikan
  list berisi perintah yang lolos, sepanjang jumlah yang diminta.
  """
  calon = domain.bangkitkan_perintah(int(jumlah * PENGALI_CADANGAN) + 100)
  saldo = 0
  lolos = []
  for perintah in calon:
    try:
      saldo = domain.periksa_perintah(saldo, perintah)
    except domain.SaldoTidakCukup:
      continue
    lolos.append(perintah)
    if len(lolos) == jumlah:
      break
  return lolos


def susun_log(buku: versi_event.BukuBesarEvent, jumlah: int) -> int:
  """Mengisi event log lalu memasang snapshot di dekat ujungnya.

  Snapshot sengaja dipasang sebelum dua ratus lima puluh event terakhir,
  agar jalur bersnapshot tetap punya pekerjaan yang harus dilipat. Snapshot
  yang dipasang tepat di ujung membuat pengukurannya kehilangan makna.
  Mengembalikan int berisi nomor urut event yang tercakup snapshot.
  """
  daftar = pilih_perintah_sah(jumlah)
  batas = jumlah - EVENT_SESUDAH_SNAPSHOT
  buku.siapkan()
  for perintah in daftar[:batas]:
    buku.catat_event(perintah)
  buku.koneksi.commit()
  urutan = buku.simpan_snapshot(domain.PEMILIK_BAKU)
  for perintah in daftar[batas:]:
    buku.catat_event(perintah)
  buku.koneksi.commit()
  return urutan


def ukur_satu_jalur(buku: versi_event.BukuBesarEvent,
                    pakai_snapshot: bool) -> tuple[list[float], int]:
  """Menghitung ulang model baca berulang kali pada log yang sama.

  Berkas basis datanya tidak disentuh di antara putaran, sehingga kedua jalur
  membaca log yang sama persis. Mengembalikan tuple berisi list latensi dalam
  milidetik beserta saldo hasil penghitungannya.
  """
  buku.pakai_snapshot = pakai_snapshot
  latensi = []
  saldo = 0
  for _ in range(PUTARAN):
    mulai = time.perf_counter()
    _, ringkasan = buku.susun_ringkasan(domain.PEMILIK_BAKU)
    latensi.append((time.perf_counter() - mulai) * MILIDETIK)
    saldo = ringkasan.saldo
  return latensi, saldo


def ukur_satu_ukuran(jumlah: int) -> dict:
  """Menyusun log sepanjang jumlah tertentu lalu mengukur kedua jalurnya.

  Mengembalikan dict berisi sebaran kedua jalur, saldo masing-masing, dan
  ukuran berkas lognya dalam KiB.
  """
  buku = versi_event.BukuBesarEvent()
  susun_log(buku, jumlah)
  tanpa, saldo_tanpa = ukur_satu_jalur(buku, False)
  dengan, saldo_dengan = ukur_satu_jalur(buku, True)
  ukuran = buku.ukuran_kib()
  buku.tutup()
  return {
    "tanpa": tanpa, "dengan": dengan, "saldo_tanpa": saldo_tanpa,
    "saldo_dengan": saldo_dengan, "ukuran": ukuran,
  }


def laporkan(jumlah: int, hasil: dict) -> None:
  """Mencetak sebaran kedua jalur beserta perbandingan mediannya."""
  tanpa = sebaran.Sebaran(hasil["tanpa"])
  dengan = sebaran.Sebaran(hasil["dengan"])
  nama = angka_id(jumlah)
  print(tanpa.baris(f"Tanpa snapshot {nama} event", LEBAR_LABEL))
  print(dengan.baris(f"Dengan snapshot {nama} event", LEBAR_LABEL))
  cocok = "sama" if hasil["saldo_tanpa"] == hasil["saldo_dengan"] else "berbeda"
  print(f"{'Snapshot mempercepat':<{LEBAR_LABEL}}"
        f": {tanpa.median() / dengan.median():.1f} kali")
  print(f"{'Saldo kedua jalur':<{LEBAR_LABEL}}: {cocok}")
  print(f"{'Ukuran event log':<{LEBAR_LABEL}}: {hasil['ukuran']:.1f} KiB")
  print()


if __name__ == "__main__":
  print(f"Menghitung ulang model baca {PUTARAN} putaran untuk setiap keadaan.",
        flush=True)
  print(f"Snapshot menyisakan {EVENT_SESUDAH_SNAPSHOT} event terakhir.\n",
        flush=True)
  for ukuran_log in UKURAN_LOG:
    print(f"Menyusun log {angka_id(ukuran_log)} event.", flush=True)
    laporkan(ukuran_log, ukur_satu_ukuran(ukuran_log))
  # Keluarannya baris terakhir: Ukuran event log   : 4192.0 KiB
