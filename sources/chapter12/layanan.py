"""Pabrik layanan pasif untuk versi orkestrasi Bab 12.

Layanan pada versi ini tidak mengenal satu pun layanan lain. Isinya hanya satu
endpoint, yaitu /langkah, yang menjalankan satu fungsi langkah lalu
mengembalikan tambahan konteksnya. Karena tidak ada pengetahuan tentang urutan,
ketujuh layanan dapat dibuat oleh satu pabrik yang sama.

Kesamaan itu bukan kebetulan. Seluruh pengetahuan tentang urutan langkah
disimpan mesin orkestrasi, sehingga yang tersisa pada layanan hanyalah
kemampuannya sendiri.

Cara menjalankan: python layanan.py
"""

import functools

import flask

import data
import konfigurasi
import langkah


def tangani_langkah(nama_langkah: str):
  """Menjalankan satu langkah atas konteks yang dikirim pemanggil.

  Galat bisnis dibalas dengan kode 400 beserta keterangannya, sebab pemanggil
  perlu membedakan penolakan aturan dari layanan yang mati. Mengembalikan
  balasan Flask berisi dict tambahan konteks.
  """
  data.hitung_permintaan()
  konteks = flask.request.get_json(silent=True) or {}
  try:
    tambahan = langkah.jalankan_langkah(nama_langkah, konteks)
  except langkah.LangkahGagal as kesalahan:
    return flask.jsonify({"galat": str(kesalahan),
                          "langkah": nama_langkah}), 400
  return flask.jsonify(tambahan)


def buat_layanan(nama_langkah: str) -> flask.Flask:
  """Membentuk satu aplikasi Flask yang melayani satu langkah saja.

  Nama endpoint dibuat berbeda per langkah agar Flask tidak menolak pendaftaran
  kedua. Mengembalikan objek Flask yang siap dijalankan pada portnya.
  """
  aplikasi = flask.Flask(f"layanan-{nama_langkah}")
  aplikasi.add_url_rule(
    "/langkah",
    f"langkah-{nama_langkah}",
    functools.partial(tangani_langkah, nama_langkah),
    methods=["POST"],
  )
  return aplikasi


def buat_semua_layanan() -> dict:
  """Membentuk seluruh layanan pasif yang tercantum pada peta port.

  Mengembalikan dict dari nama layanan ke objek Flask miliknya.
  """
  return {nama: buat_layanan(nama) for nama in konfigurasi.PORT_ORKESTRASI}


if __name__ == "__main__":
  daftar = buat_semua_layanan()
  print(f"Layanan pasif terbentuk: {len(daftar)}")
  for nama_layanan in daftar:
    print(f"  {nama_layanan:<11} lapisan {konfigurasi.LAPISAN[nama_layanan]}")
  # Keluarannya: Layanan pasif terbentuk: 7
