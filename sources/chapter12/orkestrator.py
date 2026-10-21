"""Mesin orkestrasi beserta seluruh definisi alur kerja Bab 12.

Berkas ini adalah satu-satunya tempat urutan langkah tertulis. Lima alur kerja
di bawah memakai ulang layanan yang sama, dan tidak ada satu layanan pun yang
mengetahui urutannya. Menyisipkan langkah baru karena itu berarti menyunting
berkas ini, bukan menyunting layanan yang sedang berjalan.

Mesin juga menyimpan keadaan setiap proses, yaitu langkah mana yang sudah
selesai beserta konteks terakhirnya. Catatan itulah yang membuat sebuah proses
dapat dilanjutkan sesudah satu layanan mati di tengah jalan.

Cara menjalankan:
  python orkestrator.py pesan-valas
  python orkestrator.py laporan-kurs
"""

import functools
import sys
import threading

import flask
import requests

import data
import konfigurasi

# Definisi alur kerja, yaitu business service pada taksonomi bab ini. Isinya
# hanya nama langkah beserta urutannya, tanpa satu baris aturan bisnis pun.
DEFINISI_ALUR = {
  "pesan-valas": ["nasabah", "kurs", "saldo", "transaksi", "bukti", "audit"],
  "kirim-remitansi": ["nasabah", "kurs", "batas", "saldo", "transaksi",
                      "audit"],
  "bayar-tagihan": ["nasabah", "batas", "saldo", "transaksi", "audit"],
  "tukar-poin": ["nasabah", "transaksi", "audit"],
  "laporan-kurs": ["kurs", "audit"],
}

SESI = requests.Session()


class LayananPutus(Exception):
  """Ditandai ketika sebuah layanan tidak dapat dihubungi sama sekali.

  Galat ini tidak menggugurkan prosesnya. Keadaan proses tetap tersimpan,
  sehingga alur kerjanya dapat dilanjutkan sesudah layanannya hidup kembali.
  """


class AlurDitolak(Exception):
  """Ditandai ketika sebuah langkah menolak permintaan atas alasan bisnis.

  Berbeda dengan LayananPutus, penolakan ini memang akhir dari prosesnya,
  sebab mengulangnya akan ditolak dengan alasan yang sama.
  """


class MesinOrkestrasi:
  """Penjalan definisi alur kerja beserta penyimpan keadaan prosesnya.

  Mesin memanggil layanan satu per satu lewat HTTP, lalu menggabungkan balasan
  setiap layanan ke dalam konteks proses. Konteks itu disimpan sesudah setiap
  langkah, sehingga proses yang tertahan tidak perlu diulang dari awal.
  """

  def __init__(self, port_layanan: dict = None) -> None:
    """Menyiapkan riwayat proses yang masih kosong beserta peta port layanan.

    Peta port diterima dari luar agar mesin yang sama dapat diarahkan ke
    kumpulan layanan lain, misalnya saat pengujian. Konstruktor tidak
    mengembalikan nilai.
    """
    self.port_layanan = port_layanan or konfigurasi.PORT_ORKESTRASI
    self.riwayat = {}
    self.kunci = threading.Lock()

  def panggil_layanan(self, nama_langkah: str, konteks: dict) -> dict:
    """Mengirim konteks proses ke satu layanan lalu membaca tambahannya.

    Balasan berkode 400 diubah menjadi AlurDitolak, sedangkan kegagalan koneksi
    diubah menjadi LayananPutus. Mengembalikan dict berisi tambahan konteks
    dari layanan tersebut.
    """
    alamat = konfigurasi.alamat_langkah(self.port_layanan[nama_langkah])
    try:
      balasan = SESI.post(alamat, json=konteks,
                          timeout=konfigurasi.BATAS_TUNGGU)
    except requests.RequestException as kesalahan:
      raise LayananPutus(f"{nama_langkah} tidak dapat dihubungi: {kesalahan}")
    if balasan.status_code != 200:
      raise AlurDitolak(balasan.json().get("galat", "langkah ditolak"))
    return balasan.json()

  def buat_proses(self, nama_alur: str, permintaan: dict) -> dict:
    """Mencatat satu proses baru beserta konteks awalnya ke dalam riwayat.

    Mengembalikan dict berisi catatan proses yang baru dibuat.
    """
    with self.kunci:
      nomor = f"PRC-{len(self.riwayat) + 1:06d}"
      proses = {
        "nomor": nomor,
        "alur": nama_alur,
        "konteks": dict(permintaan, alur=nama_alur, nomor_proses=nomor),
        "selesai": [],
        "tertahan": None,
        "keadaan": "berjalan",
      }
      self.riwayat[nomor] = proses
    return proses

  def jalankan_sisa(self, proses: dict) -> dict:
    """Menjalankan langkah yang belum selesai pada sebuah proses.

    Setiap langkah yang berhasil langsung dicatat, sehingga kegagalan pada
    langkah kelima tidak menghapus hasil empat langkah sebelumnya.
    Mengembalikan dict berisi catatan proses sesudah dijalankan.
    """
    urutan = DEFINISI_ALUR[proses["alur"]]
    for nama_langkah in urutan[len(proses["selesai"]):]:
      try:
        proses["konteks"].update(
          self.panggil_layanan(nama_langkah, proses["konteks"]))
      except LayananPutus as kesalahan:
        proses["tertahan"] = nama_langkah
        proses["keadaan"] = "tertahan"
        proses["pesan"] = str(kesalahan)
        return proses
      except AlurDitolak as kesalahan:
        proses["tertahan"] = nama_langkah
        proses["keadaan"] = "ditolak"
        proses["pesan"] = str(kesalahan)
        return proses
      proses["selesai"].append(nama_langkah)
    proses["tertahan"] = None
    proses["keadaan"] = "selesai"
    return proses

  def mulai(self, nama_alur: str, permintaan: dict) -> dict:
    """Membuat proses baru lalu menjalankannya dari langkah pertama.

    Mengembalikan dict berisi catatan proses beserta keadaan akhirnya.
    """
    if nama_alur not in DEFINISI_ALUR:
      raise AlurDitolak(f"alur kerja {nama_alur} tidak terdaftar")
    return self.jalankan_sisa(self.buat_proses(nama_alur, permintaan))

  def lanjutkan(self, nomor: str) -> dict:
    """Melanjutkan proses yang tertahan dari langkah yang belum selesai.

    Langkah yang sudah selesai tidak diulang, sebab hasilnya sudah tersimpan di
    dalam konteks proses. Mengembalikan dict berisi catatan proses sesudah
    dilanjutkan.
    """
    proses = self.riwayat[nomor]
    if proses["keadaan"] != "tertahan":
      return proses
    return self.jalankan_sisa(proses)

  def daftar_tertahan(self) -> list:
    """Mengumpulkan nomor seluruh proses yang berhenti karena layanan mati.

    Mengembalikan list berisi nomor proses yang masih dapat dilanjutkan.
    """
    return [nomor for nomor, proses in self.riwayat.items()
            if proses["keadaan"] == "tertahan"]


def tangani_alur(mesin: MesinOrkestrasi, nama_alur: str):
  """Menerima permintaan mulai alur kerja lalu membalas keadaan prosesnya.

  Kode balasan dibedakan agar pemanggil tahu apakah prosesnya layak
  dilanjutkan. Mengembalikan balasan Flask berisi catatan proses.
  """
  data.hitung_permintaan()
  permintaan = flask.request.get_json(silent=True) or {}
  try:
    proses = mesin.mulai(nama_alur, permintaan)
  except AlurDitolak as kesalahan:
    return flask.jsonify({"galat": str(kesalahan)}), 400
  kode = {"selesai": 200, "ditolak": 400, "tertahan": 503}[proses["keadaan"]]
  return flask.jsonify(proses), kode


def tangani_lanjutkan(mesin: MesinOrkestrasi, nomor: str):
  """Melanjutkan satu proses yang tertahan atas permintaan pemanggil luar.

  Mengembalikan balasan Flask berisi catatan proses sesudah dilanjutkan.
  """
  data.hitung_permintaan()
  if nomor not in mesin.riwayat:
    return flask.jsonify({"galat": f"proses {nomor} tidak dikenal"}), 404
  proses = mesin.lanjutkan(nomor)
  kode = {"selesai": 200, "ditolak": 400, "tertahan": 503,
          "berjalan": 202}[proses["keadaan"]]
  return flask.jsonify(proses), kode


def buat_aplikasi(mesin: MesinOrkestrasi) -> flask.Flask:
  """Membungkus mesin orkestrasi menjadi satu layanan HTTP tersendiri.

  Mesin sengaja dijadikan layanan, agar jumlah lompatan jaringan kedua versi
  dihitung dengan cara yang sama. Mengembalikan objek Flask siap jalan.
  """
  aplikasi = flask.Flask("mesin-orkestrasi")
  aplikasi.add_url_rule("/alur/<nama_alur>", "alur",
                        functools.partial(tangani_alur, mesin),
                        methods=["POST"])
  aplikasi.add_url_rule("/lanjutkan/<nomor>", "lanjutkan",
                        functools.partial(tangani_lanjutkan, mesin),
                        methods=["POST"])
  return aplikasi


def hitung_pemakaian_layanan() -> dict:
  """Menghitung berapa alur kerja yang memakai setiap layanan.

  Perhitungannya membaca definisi alur kerja saja, tanpa menjalankan satu
  layanan pun. Mengembalikan dict dari nama layanan ke jumlah alur kerja
  pemakainya.
  """
  pemakaian = {nama: 0 for nama in konfigurasi.LAPISAN}
  for urutan in DEFINISI_ALUR.values():
    for nama_langkah in urutan:
      pemakaian[nama_langkah] += 1
  return pemakaian


def alur_pemakai(nama_layanan: str) -> list:
  """Mengumpulkan nama alur kerja yang menyebut satu layanan tertentu.

  Mengembalikan list berisi nama alur kerja pemakai layanan tersebut.
  """
  return [nama for nama, urutan in DEFINISI_ALUR.items()
          if nama_layanan in urutan]


if __name__ == "__main__":
  import klien
  import server

  nama_diminta = sys.argv[1] if len(sys.argv) > 1 else "pesan-valas"
  kumpulan = server.KumpulanLayanan()
  kumpulan.nyalakan_semua()
  try:
    hasil, kode_balasan = klien.jalankan_orkestrasi(nama_diminta)
    print(f"Alur kerja       : {nama_diminta}")
    print(f"Langkah terdaftar: {len(DEFINISI_ALUR[nama_diminta])}")
    print(f"Keadaan proses   : {hasil['keadaan']} (kode {kode_balasan})")
    print(f"Permintaan HTTP  : {data.baca_pencacah()}")
  finally:
    kumpulan.matikan_semua()
  # Keluarannya: Permintaan HTTP  : 7
