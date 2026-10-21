"""Mematikan satu layanan di tengah alur kerja lalu mengukur pemulihannya.

Layanan yang dimatikan adalah layanan transaksi, yaitu langkah keempat dari
enam. Tempatnya dipilih sesudah saldo terpotong, sebab di situlah selisih
kedua versi paling terasa. Mengulang alur kerja dari awal berarti memotong
saldo untuk kedua kalinya.

Versi orkestrasi mencatat keadaan setiap proses sesudah tiap langkah, sehingga
proses yang tertahan dapat dilanjutkan dari langkah yang gagal. Versi tanpa
orkestrasi tidak memiliki tempat menyimpan keadaan, sebab konteksnya hanya ada
di dalam panggilan HTTP yang sudah selesai.

Seluruh angka pada laporan diukur, bukan diperkirakan. Saldo nasabah dibaca
sebelum dan sesudah pemulihan, sedangkan langkah yang benar-benar dijalankan
dihitung dari pencacah permintaan HTTP.

Cara menjalankan: python uji_kegagalan.py
"""

import data
import klien
import orkestrator
import server

JUMLAH_PROSES = 20
LAYANAN_MATI = "transaksi"
NAMA_ALUR = "pesan-valas"


def jalankan_gagal_orkestrasi() -> dict:
  """Menjalankan sejumlah alur kerja saat layanan transaksi sedang mati.

  Mengembalikan dict berisi jumlah proses tertahan, jumlah balasan yang
  membawa konteks proses, jumlah langkah yang sempat selesai, saldo nasabah,
  dan daftar nomor proses yang tertahan.
  """
  data.nolkan_pencacah()
  balasan = [klien.jalankan_orkestrasi(NAMA_ALUR)[0]
             for _ in range(JUMLAH_PROSES)]
  return {
    "tertahan": sum(1 for isi in balasan
                    if isi.get("keadaan") == "tertahan"),
    "dapat_dilanjutkan": sum(1 for isi in balasan
                             if "nomor" in isi and "konteks" in isi),
    "langkah_selesai": sum(len(isi.get("selesai", [])) for isi in balasan),
    "permintaan": data.baca_pencacah(),
    "saldo": data.SALDO["N001"],
    "nomor": [isi["nomor"] for isi in balasan if "nomor" in isi],
  }


def jalankan_gagal_berantai() -> dict:
  """Menjalankan sejumlah alur kerja berantai saat layanan transaksi mati.

  Balasan galatnya hanya menyebut langkah yang gagal, tanpa konteks proses,
  sehingga tidak ada satu balasan pun yang dapat dipakai melanjutkan.
  Mengembalikan dict berbentuk sama dengan versi orkestrasi.
  """
  data.nolkan_pencacah()
  balasan = [klien.jalankan_berantai()[0] for _ in range(JUMLAH_PROSES)]
  permintaan = data.baca_pencacah()
  return {
    "tertahan": sum(1 for isi in balasan if isi.get("putus")),
    "dapat_dilanjutkan": sum(1 for isi in balasan
                             if "nomor" in isi and "konteks" in isi),
    "langkah_selesai": permintaan,
    "permintaan": permintaan,
    "saldo": data.SALDO["N001"],
    "nomor": [],
  }


def pulihkan_orkestrasi(kumpulan, gagal: dict) -> dict:
  """Melanjutkan seluruh proses yang tertahan sesudah layanannya hidup lagi.

  Langkah yang benar-benar dijalankan dihitung dari permintaan HTTP dikurangi
  permintaan ke mesin, lalu dibandingkan dengan langkah yang baru selesai.
  Selisihnya adalah langkah yang terpaksa diulang. Mengembalikan dict berisi
  jumlah proses selesai, langkah diulang, permintaan HTTP, dan saldo.
  """
  kumpulan.nyalakan("orkestrasi", LAYANAN_MATI)
  data.nolkan_pencacah()
  selesai, langkah_baru = 0, 0
  for nomor in gagal["nomor"]:
    sebelum = len(kumpulan.mesin.riwayat[nomor]["selesai"])
    hasil, _ = klien.lanjutkan_orkestrasi(nomor)
    langkah_baru += len(hasil["selesai"]) - sebelum
    selesai += 1 if hasil["keadaan"] == "selesai" else 0
  permintaan = data.baca_pencacah()
  return {
    "selesai": selesai,
    "diulang": (permintaan - JUMLAH_PROSES) - langkah_baru,
    "permintaan": permintaan,
    "saldo": data.SALDO["N001"],
  }


def pulihkan_berantai(kumpulan, gagal: dict) -> dict:
  """Mengulang seluruh alur kerja dari langkah pertama, satu-satunya pilihan.

  Tidak ada catatan yang menyatakan langkah mana yang sudah selesai, sehingga
  ketiga langkah awal ikut dijalankan lagi, termasuk pemotongan saldo.
  Mengembalikan dict berbentuk sama dengan pemulihan versi orkestrasi.
  """
  kumpulan.nyalakan("berantai", LAYANAN_MATI)
  jumlah_langkah = len(orkestrator.DEFINISI_ALUR[NAMA_ALUR])
  sudah_selesai = gagal["langkah_selesai"] // JUMLAH_PROSES
  data.nolkan_pencacah()
  selesai = 0
  for _ in range(JUMLAH_PROSES):
    _, kode = klien.jalankan_berantai()
    selesai += 1 if kode == 200 else 0
  permintaan = data.baca_pencacah()
  langkah_baru = (jumlah_langkah - sudah_selesai) * JUMLAH_PROSES
  return {
    "selesai": selesai,
    "diulang": permintaan - langkah_baru,
    "permintaan": permintaan,
    "saldo": data.SALDO["N001"],
  }


def uji_versi_orkestrasi(kumpulan) -> tuple:
  """Menjalankan percobaan kegagalan lengkap pada versi orkestrasi.

  Mengembalikan tuple berisi dict hasil saat gagal dan dict hasil pemulihan.
  """
  data.setel_ulang()
  kumpulan.matikan("orkestrasi", LAYANAN_MATI)
  gagal = jalankan_gagal_orkestrasi()
  return gagal, pulihkan_orkestrasi(kumpulan, gagal)


def uji_versi_berantai(kumpulan) -> tuple:
  """Menjalankan percobaan kegagalan lengkap pada versi tanpa orkestrasi.

  Mengembalikan tuple berisi dict hasil saat gagal dan dict hasil pemulihan.
  """
  data.setel_ulang()
  kumpulan.matikan("berantai", LAYANAN_MATI)
  gagal = jalankan_gagal_berantai()
  return gagal, pulihkan_berantai(kumpulan, gagal)


def cetak_ringkasan(orkestrasi: tuple, berantai: tuple) -> None:
  """Mencetak hasil kedua versi berdampingan beserta potongan saldo gandanya.

  Tidak mengembalikan nilai.
  """
  gagal_o, pulih_o = orkestrasi
  gagal_b, pulih_b = berantai
  urutan = orkestrator.DEFINISI_ALUR[NAMA_ALUR]
  nomor_langkah = urutan.index(LAYANAN_MATI) + 1
  ganda_o = gagal_o["saldo"] - pulih_o["saldo"]
  ganda_b = gagal_b["saldo"] - pulih_b["saldo"]

  print(f"Layanan yang dimatikan       : {LAYANAN_MATI} "
        f"(langkah ke-{nomor_langkah} dari {len(urutan)})")
  print(f"Alur kerja dijalankan        : {JUMLAH_PROSES} per versi")
  print(f"Proses tertahan              : {gagal_o['tertahan']} lawan "
        f"{gagal_b['tertahan']}")
  print(f"Proses dapat dilanjutkan     : {gagal_o['dapat_dilanjutkan']} lawan "
        f"{gagal_b['dapat_dilanjutkan']}")
  print(f"Langkah selesai sebelum mati : "
        f"{gagal_o['langkah_selesai'] // JUMLAH_PROSES} lawan "
        f"{gagal_b['langkah_selesai'] // JUMLAH_PROSES}")
  print(f"Langkah diulang saat pulih   : {pulih_o['diulang']} lawan "
        f"{pulih_b['diulang']}")
  print(f"Permintaan HTTP saat pulih   : {pulih_o['permintaan']} lawan "
        f"{pulih_b['permintaan']}")
  print(f"Proses selesai akhirnya      : {pulih_o['selesai']} lawan "
        f"{pulih_b['selesai']}")
  print(f"Saldo terpotong ulang        : {ganda_o:,.0f} lawan {ganda_b:,.0f} "
        f"rupiah")


if __name__ == "__main__":
  kelompok = server.KumpulanLayanan()
  kelompok.nyalakan_semua()
  try:
    hasil_orkestrasi = uji_versi_orkestrasi(kelompok)
    hasil_berantai = uji_versi_berantai(kelompok)
    cetak_ringkasan(hasil_orkestrasi, hasil_berantai)
  finally:
    data.setel_ulang()
    kelompok.matikan_semua()
  # Keluarannya: Proses dapat dilanjutkan     : 20 lawan 0
