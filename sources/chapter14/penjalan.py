"""Penjalan fungsi kecil yang meniru daur hidup Init, Invoke, dan Shutdown.

Penjalan ini tidak menyebut nama satu fungsi pun. Yang diketahuinya hanya
registri manifes beserta bentuk kontrak pada kontrak.py. Ketika sebuah
peristiwa datang, modulnya diimpor lalu objeknya dibuat, dan itulah fase Init.
Objeknya disimpan selama masih hangat, sehingga peristiwa berikutnya langsung
masuk fase Invoke. Contoh yang diam melebihi batas dilepas, dan ketika contoh
terakhir sebuah fungsi dilepas, modulnya dikeluarkan dari cache impor Python
sehingga penjalan benar-benar kembali ke nol.

Ketiga nama fasenya diambil dari dokumentasi AWS Lambda. Satu contoh fungsi
melayani satu peristiwa pada satu waktu, sehingga peristiwa serentak menuntut
contoh yang berbeda-beda. Batas jumlah contoh meniru batas kesertaan yang
dipasang penyedia.

Cara menjalankan:
  python penjalan.py
  python penjalan.py kurs USD IDR 100
  python penjalan.py pajak 120000000
"""

import importlib
import sys
import threading
import time

import pendaftar as modul_pendaftar

MILIDETIK = 1000.0
# Lama diam sebelum satu contoh dilepas. Penyedia memakai hitungan menit,
# sedangkan angka sekecil ini dipilih agar perilakunya terlihat saat demo.
BATAS_DIAM_DETIK = 2.0
# Batas jumlah contoh yang boleh hidup bersamaan untuk satu fungsi.
BATAS_CONTOH = 4
# Lama diam pada demo daur hidup, sengaja melewati BATAS_DIAM_DETIK.
DIAM_DEMO_DETIK = 2.2


class ContohFungsi:
  """Satu lingkungan eksekusi yang memegang objek fungsi selama masih hangat."""

  def __init__(self, nomor: int, peristiwa: str) -> None:
    """Menandai contoh yang baru dipesan, sebelum objek fungsinya dibuat.

    Objeknya sengaja belum diisi di sini, sebab fase Init dikerjakan di luar
    kunci agar beberapa mulai dingin yang serentak tidak saling menunggu.
    """
    self.nomor = nomor
    self.peristiwa = peristiwa
    self.objek = None
    self.sibuk = True
    self.terakhir_dipakai = time.monotonic()
    self.jumlah_panggilan = 0


class HasilPanggilan:
  """Catatan satu pemanggilan, dipakai seluruh skrip pengukuran bab ini."""

  def __init__(self, peristiwa, isi, dingin, menunggu, nomor_contoh,
               lama_init, lama_tunggu, lama_tangani) -> None:
    """Menyimpan hasil fungsinya sekaligus tiga bagian waktu yang terukur.

    Ketiga bagian waktunya dipisah, yaitu lama Init, lama menunggu contoh yang
    bebas, dan lama penangan bekerja. Pemisahan itu membuat biaya mulai dingin
    dapat dibaca sendiri, persis seperti kolom Init Duration pada catatan
    AWS Lambda.
    """
    self.peristiwa = peristiwa
    self.isi = isi
    self.dingin = dingin
    self.menunggu = menunggu
    self.nomor_contoh = nomor_contoh
    self.lama_init = lama_init
    self.lama_tunggu = lama_tunggu
    self.lama_tangani = lama_tangani

  def lama_total(self) -> float:
    """Mengembalikan float lama seluruh pemanggilan dalam milidetik."""
    return self.lama_init + self.lama_tunggu + self.lama_tangani


class PenjalanFungsi:
  """Pemuat, penyimpan, dan pelepas contoh fungsi atas dasar peristiwa."""

  def __init__(self, pendaftar, batas_diam: float = BATAS_DIAM_DETIK,
               batas_contoh: int = BATAS_CONTOH) -> None:
    """Menyiapkan kolam contoh yang masih kosong beserta batas-batasnya.

    Kolamnya kosong pada awalnya, sehingga penjalan yang baru dibuat berada di
    angka nol. Kunci beserta kondisinya dipakai agar peristiwa serentak tetap
    tertib berbagi contoh yang sama.
    """
    self.pendaftar = pendaftar
    self.batas_diam = batas_diam
    self.batas_contoh = batas_contoh
    self.kolam = {}
    self.tersedia = threading.Condition()
    self.jumlah_init = 0
    self.jumlah_shutdown = 0
    self.jumlah_menunggu = 0

  def bangun_objek(self, peristiwa: str):
    """Mengimpor modul fungsinya lalu membuat objeknya, yaitu fase Init.

    Impor dan pembuatan objek sengaja disatukan di sini, sebab keduanyalah yang
    dibayar sebuah mulai dingin. Mengembalikan objek pemenuh kontrak.Fungsi.
    """
    manifes = self.pendaftar.manifes_untuk(peristiwa)
    modul = importlib.import_module(manifes["modul"])
    kelas = getattr(modul, manifes["kelas"])
    return kelas()

  def lupakan_modul(self, peristiwa: str) -> None:
    """Mengeluarkan modul fungsinya dari cache impor Python.

    Tanpa langkah ini, contoh berikutnya hanya membaca cache, sehingga mulai
    dingin terlihat jauh lebih murah daripada yang sebenarnya. Langkah ini
    hanya dijalankan ketika contoh terakhir sebuah fungsi sudah dilepas.

    Menghapus dari sys.modules saja ternyata belum cukup. Paket induknya masih
    memegang modul itu sebagai atribut, sehingga modulnya tetap hidup dan
    bentuk impor from paket import modul tidak pernah memuat ulang. Karena itu
    atributnya ikut dihapus.
    """
    nama = self.pendaftar.manifes_untuk(peristiwa)["modul"]
    sys.modules.pop(nama, None)
    nama_paket, _, nama_anak = nama.rpartition(".")
    paket = sys.modules.get(nama_paket)
    if paket is not None and hasattr(paket, nama_anak):
      delattr(paket, nama_anak)

  def lepas_yang_diam(self, paksa: bool = False) -> int:
    """Melepas contoh yang diam melebihi batas, yaitu fase Shutdown.

    Pemanggilnya wajib sedang memegang kunci. Contoh yang sedang sibuk tidak
    pernah dilepas. Mengembalikan int berisi jumlah contoh yang dilepas pada
    pemanggilan ini.
    """
    sekarang = time.monotonic()
    jumlah = 0
    for peristiwa, daftar in self.kolam.items():
      bertahan = []
      for contoh in daftar:
        diam = sekarang - contoh.terakhir_dipakai
        if not contoh.sibuk and (paksa or diam >= self.batas_diam):
          jumlah += 1
        else:
          bertahan.append(contoh)
      self.kolam[peristiwa] = bertahan
      if not bertahan:
        self.lupakan_modul(peristiwa)
    self.jumlah_shutdown += jumlah
    return jumlah

  def turunkan_ke_nol(self) -> int:
    """Melepas seluruh contoh yang tidak sibuk tanpa menunggu batas diamnya.

    Skrip pengukuran memakai jalan pintas ini agar keadaan awal setiap putaran
    sama persis. Mengembalikan int berisi jumlah contoh yang dilepas.
    """
    with self.tersedia:
      return self.lepas_yang_diam(paksa=True)

  def ambil_contoh(self, peristiwa: str):
    """Mencari contoh yang bebas, membuat yang baru, atau menunggu giliran.

    Contoh yang bebas selalu dipakai ulang lebih dahulu. Contoh baru hanya
    dibuat selama jumlahnya masih di bawah batas, dan sesudah batas tercapai
    permintaannya menunggu sampai ada contoh yang selesai. Mengembalikan tuple
    berisi contoh, penanda dingin, penanda menunggu, dan lama Init dalam
    milidetik.
    """
    menunggu = False
    contoh = None
    while contoh is None:
      with self.tersedia:
        self.lepas_yang_diam()
        daftar = self.kolam.setdefault(peristiwa, [])
        bebas = [satu for satu in daftar if not satu.sibuk]
        if bebas:
          bebas[0].sibuk = True
          return bebas[0], False, menunggu, 0.0
        if len(daftar) < self.batas_contoh:
          self.jumlah_init += 1
          contoh = ContohFungsi(self.jumlah_init, peristiwa)
          daftar.append(contoh)
          break
        if not menunggu:
          menunggu = True
          self.jumlah_menunggu += 1
        self.tersedia.wait()
    mulai = time.perf_counter()
    contoh.objek = self.bangun_objek(peristiwa)
    return contoh, True, menunggu, (time.perf_counter() - mulai) * MILIDETIK

  def kembalikan_contoh(self, contoh: ContohFungsi) -> None:
    """Membekukan contoh sesudah fase Invoke, lalu membangunkan penunggunya.

    Pembekuan di sini berarti contohnya tetap hangat, hanya berhenti sibuk.
    Waktu terakhir dipakai diperbarui, sebab waktu itulah yang menentukan kapan
    contohnya kelak dilepas.
    """
    with self.tersedia:
      contoh.sibuk = False
      contoh.jumlah_panggilan += 1
      contoh.terakhir_dipakai = time.monotonic()
      self.tersedia.notify()

  def panggil(self, peristiwa: str, muatan: dict) -> HasilPanggilan:
    """Melayani satu peristiwa dari fase Init sampai penangannya selesai.

    Mengembalikan objek HasilPanggilan yang memuat hasil fungsinya beserta
    ketiga bagian waktunya, sehingga pemanggil dapat memisahkan pemanggilan
    dingin dari pemanggilan hangat tanpa menebak.
    """
    mulai = time.perf_counter()
    contoh, dingin, menunggu, lama_init = self.ambil_contoh(peristiwa)
    siap = time.perf_counter()
    try:
      isi = contoh.objek.tangani(muatan)
    finally:
      self.kembalikan_contoh(contoh)
    lama_tunggu = (siap - mulai) * MILIDETIK - lama_init
    lama_tangani = (time.perf_counter() - siap) * MILIDETIK
    return HasilPanggilan(peristiwa, isi, dingin, menunggu, contoh.nomor,
                          lama_init, lama_tunggu, lama_tangani)

  def jumlah_hangat(self, peristiwa: str = None) -> int:
    """Mengembalikan int jumlah contoh yang sedang hangat, seluruhnya atau satu.

    Angka nol berarti penjalan sedang berada di angka nol untuk fungsi itu,
    sehingga peristiwa berikutnya pasti membayar mulai dingin.
    """
    with self.tersedia:
      if peristiwa is not None:
        return len(self.kolam.get(peristiwa, []))
      return sum(len(daftar) for daftar in self.kolam.values())


def rakit_penjalan(batas_diam: float = BATAS_DIAM_DETIK,
                   batas_contoh: int = BATAS_CONTOH) -> PenjalanFungsi:
  """Merangkai pendaftar dan penjalan sekaligus pada satu tempat.

  Seluruh skrip pengukuran memakai fungsi ini, sehingga susunan yang diukur
  persis sama dengan yang dijalankan. Mengembalikan objek PenjalanFungsi yang
  registrinya sudah terisi dan kolam contohnya masih kosong.
  """
  return PenjalanFungsi(modul_pendaftar.rakit_pendaftar(), batas_diam,
                        batas_contoh)


def muatan_contoh(peristiwa: str, argumen: list[str]) -> dict:
  """Menyusun peristiwa dari argumen baris perintah agar demo mudah dijalankan.

  Fungsi ini hanya melayani antarmuka baris perintah, dan tidak dipakai skrip
  pengukuran. Mengembalikan dict yang siap diserahkan kepada penangan.
  """
  if peristiwa == "kurs":
    return {"asal": argumen[0], "tujuan": argumen[1],
            "nominal": float(argumen[2])}
  if peristiwa == "pesanan":
    return {"barang": argumen[0], "jumlah": int(argumen[1]),
            "harga_usd": float(argumen[2])}
  return {"penghasilan": float(argumen[0])}


def jalankan_demo_daur_hidup(penjalan: PenjalanFungsi) -> None:
  """Memperagakan perjalanan satu fungsi dari nol ke hangat lalu kembali ke nol.

  Tiga pemanggilan dikerjakan berurutan, yaitu satu saat nol, satu saat hangat,
  dan satu lagi sesudah didiamkan melewati batas. Keluarannya dipakai
  Gambar daur hidup pada naskah bab ini.
  """
  peristiwa = {"penghasilan": 120_000_000}
  print(f"Contoh hangat sebelum mulai : {penjalan.jumlah_hangat('pajak')}")
  pertama = penjalan.panggil("pajak", peristiwa)
  print(f"Panggilan 1 dingin={pertama.dingin} "
        f"Init {pertama.lama_init:.3f} ms  "
        f"tangani {pertama.lama_tangani:.3f} ms  "
        f"total {pertama.lama_total():.3f} ms")
  kedua = penjalan.panggil("pajak", peristiwa)
  print(f"Panggilan 2 dingin={kedua.dingin} "
        f"Init {kedua.lama_init:.3f} ms  "
        f"tangani {kedua.lama_tangani:.3f} ms  "
        f"total {kedua.lama_total():.3f} ms")
  print(f"Contoh hangat sesudah dua panggilan : "
        f"{penjalan.jumlah_hangat('pajak')}")
  print(f"Didiamkan {DIAM_DEMO_DETIK} detik, batas diam "
        f"{penjalan.batas_diam} detik.")
  time.sleep(DIAM_DEMO_DETIK)
  ketiga = penjalan.panggil("pajak", peristiwa)
  print(f"Panggilan 3 dingin={ketiga.dingin} "
        f"Init {ketiga.lama_init:.3f} ms  "
        f"tangani {ketiga.lama_tangani:.3f} ms  "
        f"total {ketiga.lama_total():.3f} ms")
  print(f"Contoh dibuat seluruhnya : {penjalan.jumlah_init}")
  print(f"Contoh dilepas seluruhnya: {penjalan.jumlah_shutdown}")
  print(f"Pajak terutang           : {ketiga.isi['pajak']:,.0f} rupiah")


if __name__ == "__main__":
  mesin = rakit_penjalan()
  if len(sys.argv) < 2:
    jalankan_demo_daur_hidup(mesin)
    # Keluarannya: Panggilan 1 dingin=True Init 275.773 ms  tangani 0.038 ms
  else:
    hasil = mesin.panggil(sys.argv[1], muatan_contoh(sys.argv[1], sys.argv[2:]))
    print(f"dingin={hasil.dingin}  Init {hasil.lama_init:.3f} ms  "
          f"tangani {hasil.lama_tangani:.3f} ms")
    print(hasil.isi)
