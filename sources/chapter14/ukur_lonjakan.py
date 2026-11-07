"""Mengirim lonjakan request serentak lalu mencatat akibatnya pada kolam.

Dua belas request dilepas pada saat yang sama memakai penghalang, sehingga
seluruh utas benar-benar berangkat berbarengan. Yang dicatat ada tiga, yaitu
berapa contoh fungsi yang dibuat, berapa request yang harus menunggu giliran,
dan bagaimana sebaran latensinya.

Tiga keadaan dibandingkan. Lonjakan pertama menghantam kolam yang masih kosong,
sehingga setiap contoh baru membayar fase Init. Lonjakan kedua menyusul
seketika, ketika contoh dari lonjakan pertama masih hangat. Ketiga, lonjakan
yang sama dikirim ke layanan yang hidup terus, yang tidak pernah membuat contoh
baru dan tidak pernah membatasi jumlahnya.

Batas jumlah contoh dapat diubah lewat argumen baris perintah, misalnya
python ukur_lonjakan.py 12, dan perubahan itulah yang diminta pada Latihan 3.

Cara menjalankan:
  python ukur_lonjakan.py
  python ukur_lonjakan.py 12
"""

import concurrent.futures
import importlib
import statistics
import sys
import threading
import time

import penjalan as modul_penjalan
import ukur_mulai

JUMLAH_SERENTAK = 12
PUTARAN_LONJAKAN = 10
# Batas diam sengaja dibuat panjang di sini, sebab lonjakan dingin dipaksa
# lewat turunkan_ke_nol. Tanpa itu, lonjakan dingin yang berlangsung lama akan
# melepas contohnya sendiri sebelum lonjakan hangat sempat berangkat.
BATAS_DIAM_UKUR = 5.0
EVENT_DIUKUR = "pajak"
MUATAN = {"penghasilan": 120_000_000.0}


def muat_layanan_hidup():
  """Mengimpor modul layanan hidup sesudah seluruh lonjakan penjalan selesai.

  Impor di puncak file akan menahan ketiga modul fungsi sejak awal, sehingga
  penjalan tidak pernah benar-benar kembali ke nol. Mengembalikan modul
  layanan_hidup yang sudah terimpor.
  """
  return importlib.import_module("layanan_hidup")


class CatatanLonjakan:
  """Kumpulan angka satu jenis lonjakan, dikumpulkan dari seluruh putaran."""

  def __init__(self, nama: str) -> None:
    """Menyiapkan penampung kosong untuk satu jenis lonjakan.

    Namanya dipakai sebagai judul baris pada laporan, sehingga istilah pada
    keluaran skrip sama persis dengan istilah pada naskah bab.
    """
    self.nama = nama
    self.latensi = []
    self.contoh_dibuat = 0
    self.menunggu = 0
    self.putaran = 0

  def tambah(self, latensi: list, contoh_dibuat: int, menunggu: int) -> None:
    """Menggabungkan hasil satu putaran lonjakan ke dalam catatan ini."""
    self.latensi.extend(latensi)
    self.contoh_dibuat += contoh_dibuat
    self.menunggu += menunggu
    self.putaran += 1

  def cetak(self) -> None:
    """Mencetak satu blok laporan berisi cacah contoh beserta sebaran latensi.

    Yang dilaporkan median, persentil ke-95, dan nilai terbesar, sebab gejala
    antrean justru hanya terlihat pada nilai terbesar.
    """
    print(f"Keadaan                       : {self.nama}")
    print(f"Request seluruhnya         : {len(self.latensi)}")
    print(f"Contoh fungsi dibuat          : {self.contoh_dibuat}")
    print(f"Contoh dibuat per lonjakan    : {self.contoh_dibuat / self.putaran:.1f}")
    print(f"Request menunggu           : {self.menunggu}")
    print(f"Menunggu per lonjakan         : {self.menunggu / self.putaran:.1f}")
    median_latensi = statistics.median(self.latensi)
    p95_latensi = ukur_mulai.persentil(self.latensi)
    print(f"Median latensi                : {median_latensi:.4f} ms")
    print(f"Persentil ke-95 latensi       : {p95_latensi:.4f} ms")
    print(f"Latensi terbesar              : {max(self.latensi):.4f} ms")
    print()


class PengirimLonjakan:
  """Pengirim request serentak ke penjalan fungsi maupun layanan hidup."""

  def __init__(self, batas_contoh: int) -> None:
    """Menyiapkan penjalan berbatas contoh tertentu beserta ketiga catatannya.

    Batas contohnya diserahkan dari luar, sebab justru angka itulah yang diubah
    pada langkah terakhir Latihan 3.
    """
    self.batas_contoh = batas_contoh
    self.penjalan = modul_penjalan.rakit_penjalan(batas_diam=BATAS_DIAM_UKUR,
                                                  batas_contoh=batas_contoh)
    self.penghalang = threading.Barrier(JUMLAH_SERENTAK)
    self.catatan_dingin = CatatanLonjakan("penjalan, kolam kosong")
    self.catatan_hangat = CatatanLonjakan("penjalan, kolam hangat")
    self.catatan_layanan = CatatanLonjakan("layanan hidup")

  def satu_request_penjalan(self, nomor: int) -> float:
    """Menunggu di penghalang lalu mengirim satu request ke penjalan.

    Penghalang membuat seluruh utas berangkat pada saat yang sama, sehingga
    lonjakannya benar-benar serentak. Mengembalikan float lama request itu
    dalam milidetik.
    """
    self.penghalang.wait()
    return self.penjalan.panggil(EVENT_DIUKUR, MUATAN).lama_total()

  def satu_request_layanan(self, nomor: int) -> float:
    """Menunggu di penghalang lalu mengirim satu request ke layanan hidup.

    Mengembalikan float lama request itu dalam milidetik.
    """
    self.penghalang.wait()
    return self.layanan.panggil(EVENT_DIUKUR, MUATAN).lama_total()

  def kirim_lonjakan(self, pekerjaan) -> list:
    """Melepas dua belas request serentak lalu memanen seluruh latensinya.

    Mengembalikan list berisi lama setiap request dalam milidetik, dengan
    urutan sesuai nomor request-nya.
    """
    self.penghalang.reset()
    with concurrent.futures.ThreadPoolExecutor(JUMLAH_SERENTAK) as kolam_utas:
      return list(kolam_utas.map(pekerjaan, range(JUMLAH_SERENTAK)))

  def jalankan_penjalan(self) -> None:
    """Menjalankan lonjakan dingin lalu lonjakan hangat sebanyak putarannya.

    Kolam diturunkan ke nol sebelum setiap lonjakan dingin, sedangkan lonjakan
    hangat menyusul seketika sesudahnya tanpa jeda.
    """
    mulai = time.perf_counter()
    for nomor in range(1, PUTARAN_LONJAKAN + 1):
      self.penjalan.turunkan_ke_nol()
      awal_init = self.penjalan.jumlah_init
      awal_tunggu = self.penjalan.jumlah_menunggu
      latensi = self.kirim_lonjakan(self.satu_request_penjalan)
      self.catatan_dingin.tambah(latensi,
                                 self.penjalan.jumlah_init - awal_init,
                                 self.penjalan.jumlah_menunggu - awal_tunggu)
      awal_init = self.penjalan.jumlah_init
      awal_tunggu = self.penjalan.jumlah_menunggu
      latensi = self.kirim_lonjakan(self.satu_request_penjalan)
      self.catatan_hangat.tambah(latensi,
                                 self.penjalan.jumlah_init - awal_init,
                                 self.penjalan.jumlah_menunggu - awal_tunggu)
      print(f"  lonjakan {nomor:2d}/{PUTARAN_LONJAKAN}"
            f"  lewat {time.perf_counter() - mulai:5.1f} detik", flush=True)

  def jalankan_layanan(self) -> None:
    """Mengirim lonjakan yang sama ke layanan yang hidup terus.

    Layanannya baru diimpor di sini, sesudah seluruh lonjakan penjalan selesai,
    agar penjalan sempat benar-benar scale to zero pada pengukuran sebelumnya.
    """
    self.layanan = muat_layanan_hidup().rakit_layanan()
    for _ in range(PUTARAN_LONJAKAN):
      self.catatan_layanan.tambah(
        self.kirim_lonjakan(self.satu_request_layanan), 0, 0)


if __name__ == "__main__":
  batas = int(sys.argv[1]) if len(sys.argv) > 1 else modul_penjalan.BATAS_CONTOH
  pengirim = PengirimLonjakan(batas)
  print(f"Request serentak per lonjakan : {JUMLAH_SERENTAK}")
  print(f"Batas contoh fungsi              : {batas}")
  print(f"Putaran lonjakan                 : {PUTARAN_LONJAKAN}\n", flush=True)
  pengirim.jalankan_penjalan()
  pengirim.jalankan_layanan()
  print()
  pengirim.catatan_dingin.cetak()
  pengirim.catatan_hangat.cetak()
  pengirim.catatan_layanan.cetak()
  # Keluarannya: Contoh dibuat per lonjakan    : 4.0
