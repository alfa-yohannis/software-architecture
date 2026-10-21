"""Bidang penagihan, yaitu pemilik tabel tagihan.

Bidang ini menghitung nilai rupiah sebuah pesanan, menambahkan pajak, lalu
menyimpannya sebagai tagihan. Aturan bisnisnya nyata, yaitu pesanan yang
sudah dibatalkan tidak boleh ditagih, dan penolakan itulah yang diuji pada
skrip penjalan.

Satu hal perlu diperhatikan. Fungsi terbitkan_tagihan membaca tabel pesanan
langsung dari basis data bersama, bukan bertanya kepada bidang pemesanan.
Pembacaan silang seperti itu dimungkinkan justru karena basis datanya satu.
Kemudahan itu yang membuat service-based architecture murah, sekaligus yang
membuat perubahan skema menjadi mahal, sebab dua bidang sekaligus ikut
terbawa. Harganya diukur pada skrip biaya_perubahan.py.

Berkas ini tidak dijalankan sendiri, melainkan diimpor monolit.py atau
layanan_penagihan.py.
"""

import datetime

import basis_data
import kesalahan

TARIF_PAJAK = 0.11
PEMBULATAN_RUPIAH = 2

AMBIL_PESANAN_UNTUK_TAGIHAN = """
SELECT nomor, nominal, status
FROM pesanan
WHERE nomor = ?
"""

AMBIL_SATU_TAGIHAN = """
SELECT nomor_pesanan, nominal_rupiah, pajak, total, waktu_terbit
FROM tagihan
WHERE nomor_pesanan = ?
"""

SIMPAN_TAGIHAN = """
INSERT OR REPLACE INTO tagihan
  (nomor_pesanan, nominal_rupiah, pajak, total, waktu_terbit)
VALUES (?, ?, ?, ?, ?)
"""


def ambil_tagihan(nomor_pesanan: int) -> dict:
  """Membaca tagihan yang sudah pernah diterbitkan untuk satu pesanan.

  Melempar kesalahan.TidakDitemukan bila pesanan itu belum pernah ditagih,
  sebab tagihan yang belum ada berbeda maknanya dari tagihan bernilai nol.
  Mengembalikan dict berisi kunci nomor_pesanan, nominal_rupiah, pajak,
  total, dan waktu_terbit.
  """
  koneksi = basis_data.buka_koneksi()
  try:
    baris = koneksi.execute(AMBIL_SATU_TAGIHAN, (nomor_pesanan,)).fetchone()
  finally:
    koneksi.close()
  if baris is None:
    raise kesalahan.TidakDitemukan(f"pesanan {nomor_pesanan} belum ditagih")
  return {
    "nomor_pesanan": baris["nomor_pesanan"],
    "nominal_rupiah": baris["nominal_rupiah"],
    "pajak": baris["pajak"],
    "total": baris["total"],
    "waktu_terbit": baris["waktu_terbit"],
  }


def terbitkan_tagihan(nomor_pesanan: int, nilai_kurs: float) -> dict:
  """Menghitung lalu menyimpan tagihan satu pesanan dalam rupiah.

  Nilai kurs diterima dari pemanggil, sebab bidang ini tidak berhak menebak
  kurs mana yang berlaku. Pesanan yang berstatus batal ditolak dengan
  kesalahan.AturanDilanggar. Baris lama ditimpa bila pesanan yang sama
  ditagih ulang, sehingga pengukuran seratus putaran tidak menggelembungkan
  tabelnya. Mengembalikan dict berisi tagihan yang baru tersimpan.
  """
  koneksi = basis_data.buka_koneksi()
  try:
    baris = koneksi.execute(
      AMBIL_PESANAN_UNTUK_TAGIHAN, (nomor_pesanan,)).fetchone()
    if baris is None:
      raise kesalahan.TidakDitemukan(f"pesanan {nomor_pesanan} tidak terdaftar")
    if baris["status"] == basis_data.STATUS_BATAL:
      raise kesalahan.AturanDilanggar(
        f"pesanan {nomor_pesanan} sudah dibatalkan, tidak dapat ditagih")
    nominal_rupiah = round(baris["nominal"] * nilai_kurs, PEMBULATAN_RUPIAH)
    pajak = round(nominal_rupiah * TARIF_PAJAK, PEMBULATAN_RUPIAH)
    waktu = datetime.datetime.now().isoformat(timespec="seconds")
    tagihan = {
      "nomor_pesanan": nomor_pesanan,
      "nominal_rupiah": nominal_rupiah,
      "pajak": pajak,
      "total": round(nominal_rupiah + pajak, PEMBULATAN_RUPIAH),
      "waktu_terbit": waktu,
    }
    koneksi.execute(SIMPAN_TAGIHAN, (
      tagihan["nomor_pesanan"],
      tagihan["nominal_rupiah"],
      tagihan["pajak"],
      tagihan["total"],
      tagihan["waktu_terbit"],
    ))
    koneksi.commit()
  finally:
    koneksi.close()
  return tagihan
