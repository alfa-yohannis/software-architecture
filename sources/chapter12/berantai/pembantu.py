"""Pabrik bersama bagi seluruh layanan pada versi tanpa orkestrasi.

Pabrik ini menerima nama langkah beserta nama penerusnya. Sesudah langkahnya
selesai, konteks yang sudah bertambah dikirim langsung ke layanan penerus, lalu
balasan penerus itu diteruskan apa adanya ke pemanggil. Layanan terakhir
mengembalikan konteksnya sendiri.

Perhatikan bahwa penerusnya tidak dibaca dari berkas pengaturan bersama,
melainkan diserahkan berkas layanan masing-masing. Itulah sebabnya alur
kerjanya tersebar, sebab tidak ada satu tempat pun yang memuat urutannya.

Cara menjalankan: python -c "from berantai import pembantu"
"""

import functools

import flask
import requests

import data
import konfigurasi
import langkah

# Satu sesi dipakai ulang agar biaya membuka koneksi tidak dihitung berulang
# pada setiap lompatan. Versi orkestrasi memakai sesi dengan cara yang sama.
SESI = requests.Session()


def teruskan(nama_langkah: str, berikutnya):
  """Menjalankan satu langkah lalu mengirim konteksnya ke layanan penerus.

  Galat jaringan dibalas dengan kode 503 dan ditandai putus, sebab pemanggil
  tidak dapat mengetahui sampai langkah mana alur kerjanya sempat berjalan.
  Mengembalikan balasan Flask berisi konteks akhir atau keterangan galat.
  """
  data.hitung_permintaan()
  konteks = flask.request.get_json(silent=True) or {}
  try:
    konteks.update(langkah.jalankan_langkah(nama_langkah, konteks))
  except langkah.LangkahGagal as kesalahan:
    return flask.jsonify({"galat": str(kesalahan),
                          "langkah": nama_langkah}), 400
  if berikutnya is None:
    return flask.jsonify(konteks)
  alamat = konfigurasi.alamat_langkah(konfigurasi.PORT_BERANTAI[berikutnya])
  try:
    balasan = SESI.post(alamat, json=konteks,
                        timeout=konfigurasi.BATAS_TUNGGU)
  except requests.RequestException as kesalahan:
    return flask.jsonify({"galat": str(kesalahan), "langkah": berikutnya,
                          "putus": True, "sudah_jalan": nama_langkah}), 503
  return flask.jsonify(balasan.json()), balasan.status_code


def buat_layanan(nama_langkah: str, berikutnya) -> flask.Flask:
  """Membentuk aplikasi Flask satu layanan beserta pengetahuan penerusnya.

  Mengembalikan objek Flask yang siap dijalankan pada port layanan tersebut.
  """
  aplikasi = flask.Flask(f"berantai-{nama_langkah}")
  aplikasi.add_url_rule(
    "/langkah",
    f"langkah-{nama_langkah}",
    functools.partial(teruskan, nama_langkah, berikutnya),
    methods=["POST"],
  )
  return aplikasi
