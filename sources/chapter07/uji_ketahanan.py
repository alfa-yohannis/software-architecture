"""Mematikan satu node, lalu menghitung berapa lookup yang masih terjawab.

Percobaan diulang untuk setiap node, yaitu setiap node bergiliran menjadi
node yang mati. Pada susunan client-server, giliran node nol berarti
indeksnya yang mati, dan di situlah perbedaan client-server dengan peer-to-peer
muncul sebagai angka.

Lookup yang pemintanya sendiri yang mati tidak ikut dinilai, sebab node
mati memang tidak dapat bertanya. Penyebutnya karena itu ikut menyusut pada
giliran tersebut, dan hasilnya dilaporkan sebagai persen agar tetap dapat
dibandingkan.

Cara menjalankan: python uji_ketahanan.py
"""

import sebaran
import susunan
import ukur_pencarian

PERSEN_PENUH = 100.0


def hitung_terjawab(jaringan_ini, bahan: list) -> tuple:
  """Menjalankan seluruh lookup lalu mencacah yang terjawab.

  Mengembalikan tupel (terjawab, dinilai). Lookup yang pemintanya sudah mati
  tidak masuk hitungan, baik pada pembilang maupun pada penyebutnya.
  """
  terjawab = 0
  dinilai = 0
  for nomor, kunci in bahan:
    if not jaringan_ini.simpul[nomor].hidup:
      continue
    dinilai += 1
    if jaringan_ini.cari(nomor, kunci).terjawab:
      terjawab += 1
  return terjawab, dinilai


def uji_satu_kematian(jaringan_ini, bahan: list, nomor_mati: int) -> float:
  """Mematikan satu node, mengukur, lalu menghidupkannya kembali.

  Mengembalikan persentase lookup yang masih terjawab pada keadaan itu.
  """
  jaringan_ini.hidupkan_semua()
  jaringan_ini.matikan(nomor_mati)
  terjawab, dinilai = hitung_terjawab(jaringan_ini, bahan)
  jaringan_ini.hidupkan_semua()
  return terjawab / dinilai * PERSEN_PENUH if dinilai else 0.0


def laporkan(jaringan_ini, bahan: list) -> None:
  """Mencetak ketahanan satu susunan pada keadaan utuh dan keadaan berkurang."""
  jaringan_ini.hidupkan_semua()
  utuh, dinilai_utuh = hitung_terjawab(jaringan_ini, bahan)
  persen = [uji_satu_kematian(jaringan_ini, bahan, nomor)
            for nomor in range(jaringan_ini.jumlah_simpul)]
  terburuk = min(persen)
  nomor_terburuk = persen.index(terburuk)
  print(f"Susunan {jaringan_ini.nama}")
  sebaran.cetak_baris("Seluruh node hidup", f"{utuh} dari {dinilai_utuh}")
  sebaran.cetak_baris("Node 0 mati", f"{persen[0]:.1f} persen")
  sebaran.cetak_baris("Rata-rata satu node mati",
                      f"{sum(persen) / len(persen):.1f} persen")
  sebaran.cetak_baris("Terburuk satu node mati",
                      f"{terburuk:.1f} persen (node {nomor_terburuk})")
  sebaran.cetak_baris("Kunci pada node terburuk",
                      f"{len(jaringan_ini.simpul[nomor_terburuk].simpanan)}")
  print()


def uji(jumlah_simpul: int = susunan.JUMLAH_SIMPUL_BAKU) -> None:
  """Menguji ketahanan ketiga susunan memakai bahan lookup yang sama."""
  bahan = ukur_pencarian.susun_bahan(jumlah_simpul)
  print(f"Lookup per percobaan       : {len(bahan)}")
  print(f"Node per jaringan          : {jumlah_simpul}")
  print(f"Giliran node yang mati     : 0 sampai {jumlah_simpul - 1}\n")
  for jaringan_ini in susunan.bangun_semua(jumlah_simpul).values():
    laporkan(jaringan_ini, bahan)


if __name__ == "__main__":
  uji()
  # Keluarannya pada susunan client-server: Node 0 mati : 0.0 persen
