"""Menjalankan ulang satu layanan, lalu menghitung permintaan yang gagal.

Kurs berubah setiap hari kerja, sehingga layanan kurs adalah bagian yang paling
sering dirilis ulang. Pada versi mikroservis, merilisnya berarti menjalankan
ulang satu proses saja. Pada versi monolit, kurs tinggal di dalam proses yang
sama dengan nasabah dan pesanan, sehingga merilisnya berarti menjalankan ulang
seluruhnya.

Lalu lintas dikirim dengan jarak tetap dua puluh lima milidetik selama
pengukuran, sehingga jumlah permintaan yang tidak terlayani penuh dapat dibaca
langsung sebagai lama padam. Jaraknya dipilih lebih longgar daripada permintaan
yang paling lambat, agar jadwalnya tidak tergeser oleh permintaan itu sendiri.
Rilisnya sendiri dijalankan pada utas terpisah, agar lalu lintasnya tetap
mengalir selama proses lama mati dan proses baru dinyalakan.

Satu kali rilis tidak cukup, sebab lama nyala sebuah proses Python bergantung
pada kesibukan mesin. Karena itu rilisnya diulang beberapa kali, lalu yang
dilaporkan adalah mediannya beserta nilai terbesarnya.

Cara menjalankan: python ukur_rilis.py
"""

import statistics
import threading
import time

import alamat
import penjalan
import uji_kegagalan

JUMLAH_PERMINTAAN = 200
PERMINTAAN_SEBELUM_RILIS = 50
JEDA_PERMINTAAN_DETIK = 0.025
PUTARAN_RILIS = 7

JALUR_UJI = (
  ("nasabah", "/nasabah/N-001"),
  ("laporan", "/laporan/N-001"),
)

GOLONGAN = (uji_kegagalan.STATUS_PENUH, uji_kegagalan.STATUS_SEBAGIAN,
            uji_kegagalan.STATUS_GAGAL)


def rilis_di_latar(berjalan: dict, nama: str, catatan: dict) -> None:
  """Menjalankan ulang satu proses pada utas terpisah dari lalu lintasnya.

  Dijalankan di latar agar pengukur lalu lintas tidak ikut berhenti selama
  proses baru dinyalakan. Lama padamnya dititipkan ke dict catatan, sebab utas
  tidak dapat mengembalikan nilai kepada pemanggilnya. Fungsi ini tidak
  mengembalikan nilai.
  """
  catatan["padam_ms"] = penjalan.nyalakan_ulang(berjalan, nama)


def kirim_terjadwal(induk: str, jalur: str, nomor: int, mulai: float) -> str:
  """Mengirim satu permintaan tepat pada jadwalnya, lalu menggolongkan hasilnya.

  Jadwal dihitung dari waktu mulai, bukan dari permintaan sebelumnya, sehingga
  permintaan yang lambat tidak menggeser seluruh sisanya. Mengembalikan str
  berisi golongan hasil menurut uji_kegagalan.
  """
  jadwal = mulai + nomor * JEDA_PERMINTAAN_DETIK
  sisa = jadwal - time.perf_counter()
  if sisa > 0:
    time.sleep(sisa)
  return uji_kegagalan.golongkan(induk, jalur)


def satu_jendela(induk: str, jalur: str, berjalan: dict,
                 nama_dirilis: str) -> dict:
  """Mengalirkan lalu lintas sambil satu proses dirilis ulang di tengahnya.

  Lima puluh permintaan pertama mengalir sebelum rilis dimulai, agar terlihat
  jelas bahwa kegagalannya memang berawal dari rilis itu. Mengembalikan dict
  berisi cacah tiap golongan beserta lama padam dalam milidetik.
  """
  hitungan = {golongan: 0 for golongan in GOLONGAN}
  catatan = {}
  utas = threading.Thread(target=rilis_di_latar,
                          args=(berjalan, nama_dirilis, catatan))
  mulai = time.perf_counter()
  for nomor in range(JUMLAH_PERMINTAAN):
    if nomor == PERMINTAAN_SEBELUM_RILIS:
      utas.start()
    hitungan[kirim_terjadwal(induk, jalur, nomor, mulai)] += 1
  utas.join()
  hitungan["padam_ms"] = catatan["padam_ms"]
  return hitungan


def ulangi_rilis(induk: str, jalur: str, berjalan: dict,
                 nama_dirilis: str) -> dict:
  """Mengulang rilis beberapa kali lalu merangkum hasilnya menjadi median.

  Nilai terbesar ikut dilaporkan, sebab rilis yang kebetulan bertepatan dengan
  mesin sedang sibuk membuat padamnya jauh lebih lama daripada biasanya.
  Mengembalikan dict berisi median tiap golongan, median lama padam, dan lama
  padam terbesar.
  """
  jendela = []
  for nomor in range(1, PUTARAN_RILIS + 1):
    jendela.append(satu_jendela(induk, jalur, berjalan, nama_dirilis))
    print(f"    rilis {nomor}/{PUTARAN_RILIS}"
          f"  padam {jendela[-1]['padam_ms']:4.0f} ms", flush=True)
  rangkuman = {golongan: statistics.median([satu[golongan] for satu in jendela])
               for golongan in GOLONGAN}
  rangkuman["padam_ms"] = statistics.median([satu["padam_ms"] for satu in jendela])
  rangkuman["padam_terbesar_ms"] = max(satu["padam_ms"] for satu in jendela)
  return rangkuman


def uji_satu_versi(nama_versi: str, daftar_proses: tuple, induk: str,
                   nama_dirilis: str) -> dict:
  """Menyalakan satu versi, lalu merilis ulang satu prosesnya pada dua jalur.

  Kedua jalur diukur berurutan pada versi yang sama, sehingga keduanya
  menghadapi keadaan mesin yang serupa. Mengembalikan dict yang memetakan nama
  jalur ke rangkuman hasilnya.
  """
  print(f"Menyalakan versi {nama_versi}.", flush=True)
  berjalan = penjalan.nyalakan(daftar_proses)
  hasil = {}
  try:
    for nama_jalur, jalur in JALUR_UJI:
      print(f"  merilis ulang {nama_dirilis} sambil melayani {nama_jalur}.",
            flush=True)
      hasil[nama_jalur] = ulangi_rilis(induk, jalur, berjalan, nama_dirilis)
  finally:
    penjalan.matikan(berjalan)
  return hasil


def cetak_baris(nama_versi: str, nama_jalur: str, rangkuman: dict) -> None:
  """Mencetak satu baris laporan berisi cacah tiap golongan dan lama padam.

  Susunan kolomnya dibuat sama dengan susunan tabel pada naskah bab, sehingga
  angkanya tinggal disalin. Fungsi ini tidak mengembalikan nilai.
  """
  tidak_penuh = (rangkuman[uji_kegagalan.STATUS_SEBAGIAN]
                 + rangkuman[uji_kegagalan.STATUS_GAGAL])
  print(f"{nama_versi:<12} {nama_jalur:<9}"
        f" {rangkuman[uji_kegagalan.STATUS_PENUH]:6.0f}"
        f" {rangkuman[uji_kegagalan.STATUS_SEBAGIAN]:9.0f}"
        f" {rangkuman[uji_kegagalan.STATUS_GAGAL]:6.0f}"
        f" {tidak_penuh:11.0f}"
        f" {rangkuman['padam_ms']:9.0f}"
        f" {rangkuman['padam_terbesar_ms']:9.0f}")


if __name__ == "__main__":
  hasil_monolit = uji_satu_versi("monolit", penjalan.NAMA_MONOLIT,
                                 alamat.MONOLIT, "monolit")
  hasil_mikro = uji_satu_versi("mikroservis", penjalan.NAMA_MIKROSERVIS,
                               alamat.GERBANG, "kurs")

  print(f"\nRilis per jalur      : {PUTARAN_RILIS}, angka di bawah adalah median")
  print(f"Permintaan per rilis : {JUMLAH_PERMINTAAN},"
        f" satu tiap {JEDA_PERMINTAAN_DETIK * 1000:.0f} ms")
  print(f"{'Versi':<12} {'Jalur':<9} {'Penuh':>6} {'Sebagian':>9} {'Gagal':>6}"
        f" {'Tidak penuh':>11} {'Padam ms':>9} {'Terbesar':>9}")
  for nama in hasil_monolit:
    cetak_baris("monolit", nama, hasil_monolit[nama])
  for nama in hasil_mikro:
    cetak_baris("mikroservis", nama, hasil_mikro[nama])
  # Keluarannya baris mikroservis nasabah: tidak penuh 0 dari 200
