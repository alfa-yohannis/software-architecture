"""Mengukur pemakaian sumber daya saat menganggur lalu menghitung tagihannya.

Tiga hal diukur berturut-turut. Pertama, memori yang ditahan penjalan fungsi
ketika sudah turun ke nol, dibandingkan dengan memori yang ditahan layanan yang
hidup terus. Kedua, waktu prosesor yang terpakai kedua jalur selama satu
jendela diam tanpa permintaan sama sekali. Ketiga, satuan tagihan yang dipakai
penyedia, yaitu gigabita detik.

Gigabita detik dihitung sebagai memori yang dipesan dikalikan lama eksekusi,
mengikuti dokumentasi AWS Lambda. Lama eksekusinya dibulatkan ke atas menjadi
kelipatan satu milidetik, juga mengikuti dokumentasi tersebut, dan pembulatan
itulah yang membuat fungsi yang sangat cepat tetap ditagih satu milidetik
penuh.

Modul layanan hidup sengaja diimpor belakangan, bukan di puncak berkas ini.
Impor di puncak akan menahan ketiga modul fungsi sejak awal, sehingga penjalan
tidak pernah benar-benar kembali ke nol dan angka memorinya tidak jujur.

Cara menjalankan: python ukur_sumber_daya.py
"""

import gc
import importlib
import math
import statistics
import sys
import time
import tracemalloc

import penjalan as modul_penjalan

KIBIBYTE = 1024.0
MILIDETIK = 1000.0
MEGABITA_PER_GIGABITA = 1024.0
# Lama jendela diam yang diamati, yaitu waktu tanpa satu permintaan pun.
JENDELA_DIAM_DETIK = 1.0
BATAS_DIAM_UKUR = 0.02
DIAM_PAKSA_DETIK = 0.03
# Jumlah contoh pengukuran lama eksekusi, dipakai sebagai masukan tagihan.
PANGGILAN_DINGIN = 40
PANGGILAN_HANGAT = 200
# Beban yang ditagih, yaitu satu permintaan setiap lima detik selama satu jam.
JENDELA_TAGIHAN_DETIK = 3600
PERMINTAAN_PER_JAM = 720
# Memori yang dipesan satu proses layanan hidup, menampung ketiga penangan.
MEMORI_LAYANAN_MB = 512
PERISTIWA_DIUKUR = "pajak"
MUATAN = {
  "kurs": {"asal": "USD", "tujuan": "IDR", "nominal": 100.0},
  "pesanan": {"barang": "kopi", "jumlah": 3, "harga_usd": 12.5},
  "pajak": {"penghasilan": 120_000_000.0},
}


def muat_layanan_hidup():
  """Mengimpor modul layanan hidup pada saat dibutuhkan, bukan lebih awal.

  Penundaan ini bukan gaya penulisan, melainkan syarat agar pengukurannya jujur.
  Mengembalikan modul layanan_hidup yang sudah terimpor.
  """
  return importlib.import_module("layanan_hidup")


def hitung_modul_fungsi() -> int:
  """Mengembalikan int jumlah modul fungsi yang sedang dipegang Python.

  Angka ini dibaca dari sys.modules, sehingga memperlihatkan langsung apakah
  sebuah jalur benar-benar melepaskan kodenya atau hanya melepaskan objeknya.
  """
  return sum(1 for nama in sys.modules if nama.startswith("fungsi."))


def memori_terpakai_kib() -> float:
  """Mengembalikan float memori sisi Python yang sedang tercatat, dalam KiB.

  Sampah dikumpulkan lebih dahulu, sebab objek yang sudah tidak dirujuk masih
  terhitung sampai pengumpul sampah menjalankan tugasnya.
  """
  gc.collect()
  return tracemalloc.get_traced_memory()[0] / KIBIBYTE


def lama_tertagih_detik(lama_ms: float) -> float:
  """Membulatkan lama eksekusi ke atas menjadi kelipatan satu milidetik.

  Pembulatan ini mengikuti cara penyedia menagih, dan akibatnya besar bagi
  fungsi yang selesai dalam hitungan mikrodetik. Mengembalikan float lama
  tertagih dalam detik.
  """
  return math.ceil(lama_ms) / MILIDETIK


def gigabita_detik(memori_mb: float, lama_detik: float) -> float:
  """Mengalikan memori yang dipesan dengan lama pemakaiannya.

  Inilah satuan tagihan yang dipakai AWS Lambda. Mengembalikan float berisi
  jumlah gigabita detik yang terpakai.
  """
  return memori_mb / MEGABITA_PER_GIGABITA * lama_detik


class PengukurSumberDaya:
  """Pengukur memori, waktu menganggur, dan tagihan kedua jalur bab ini."""

  def __init__(self) -> None:
    """Menyiapkan penjalan berbatas diam pendek beserta penampung hasilnya.

    Layanan hidupnya belum dibuat di sini, sebab pembuatannya harus terjadi
    sesudah seluruh pengukuran penjalan selesai.
    """
    self.penjalan = modul_penjalan.rakit_penjalan(batas_diam=BATAS_DIAM_UKUR)
    self.layanan = None
    self.hasil = {}

  def panaskan_seluruh_fungsi(self) -> None:
    """Memanggil ketiga fungsi sekali, agar seluruh contohnya menjadi hangat."""
    for peristiwa, muatan in MUATAN.items():
      self.penjalan.panggil(peristiwa, muatan)

  def ukur_memori_penjalan(self) -> None:
    """Mencatat memori penjalan pada keadaan hangat lalu pada keadaan nol.

    Selisih keduanya adalah memori yang benar-benar dilepas ketika penjalan
    turun ke nol, dan angka itulah yang tidak dimiliki layanan yang hidup terus.
    """
    self.hasil["memori_awal_kib"] = memori_terpakai_kib()
    self.panaskan_seluruh_fungsi()
    self.hasil["memori_hangat_kib"] = memori_terpakai_kib()
    self.hasil["modul_saat_hangat"] = hitung_modul_fungsi()
    self.hasil["contoh_hangat"] = self.penjalan.jumlah_hangat()
    self.penjalan.turunkan_ke_nol()
    self.hasil["memori_nol_kib"] = memori_terpakai_kib()
    self.hasil["modul_saat_nol"] = hitung_modul_fungsi()
    self.hasil["contoh_saat_nol"] = self.penjalan.jumlah_hangat()

  def ukur_memori_layanan(self) -> None:
    """Mencatat memori yang ditahan layanan hidup sesudah seluruhnya siap.

    Seluruh pengukuran memori penjalan harus sudah selesai sebelum metode ini
    dipanggil, sebab impor modul layanannya menahan ketiga modul fungsi.
    """
    modul_layanan = muat_layanan_hidup()
    sebelum = memori_terpakai_kib()
    layanan = modul_layanan.LayananHidup()
    layanan.siapkan()
    self.hasil["memori_layanan_kib"] = memori_terpakai_kib() - sebelum
    self.hasil["modul_layanan"] = hitung_modul_fungsi()
    self.hasil["penangan_layanan"] = layanan.jumlah_penangan()

  def ukur_jendela_diam_penjalan(self) -> None:
    """Mencatat waktu prosesor penjalan selama satu jendela tanpa permintaan.

    Pemanggilan pertama sesudah jendela itu ikut diukur, sebab di situlah
    ongkos menganggur sebenarnya muncul, yaitu sebagai mulai dingin.
    """
    self.penjalan.turunkan_ke_nol()
    mulai = time.process_time()
    time.sleep(JENDELA_DIAM_DETIK)
    self.hasil["prosesor_penjalan_ms"] = (time.process_time() - mulai) * MILIDETIK
    hasil = self.penjalan.panggil(PERISTIWA_DIUKUR, MUATAN[PERISTIWA_DIUKUR])
    self.hasil["pertama_penjalan_ms"] = hasil.lama_total()
    self.hasil["pertama_penjalan_dingin"] = hasil.dingin
    self.penjalan.turunkan_ke_nol()

  def ukur_lama_eksekusi(self) -> None:
    """Mengumpulkan lama pemanggilan dingin dan hangat sebagai masukan tagihan.

    Pemanggilan dingin dipaksa dengan cara mendiamkan penjalan melewati batas
    diamnya, sedangkan pemanggilan hangat dikerjakan berturut-turut tanpa jeda.
    """
    dingin, hangat = [], []
    for _ in range(PANGGILAN_DINGIN):
      time.sleep(DIAM_PAKSA_DETIK)
      dingin.append(
        self.penjalan.panggil(PERISTIWA_DIUKUR,
                              MUATAN[PERISTIWA_DIUKUR]).lama_total())
    for _ in range(PANGGILAN_HANGAT):
      hangat.append(
        self.penjalan.panggil(PERISTIWA_DIUKUR,
                              MUATAN[PERISTIWA_DIUKUR]).lama_total())
    self.hasil["lama_dingin_ms"] = statistics.median(dingin)
    self.hasil["lama_hangat_ms"] = statistics.median(hangat)
    self.penjalan.turunkan_ke_nol()

  def ukur_waktu_layanan(self) -> None:
    """Mencatat lama penyiapan, waktu menganggur, dan permintaan pertamanya.

    Layanannya dibuat ulang di sini agar lama penyiapannya terukur tanpa beban
    pencatat alokasi, sama seperti pengukuran waktu pada penjalan.
    """
    modul_layanan = muat_layanan_hidup()
    self.layanan = modul_layanan.LayananHidup()
    self.hasil["siap_layanan_ms"] = self.layanan.siapkan()
    mulai = time.process_time()
    time.sleep(JENDELA_DIAM_DETIK)
    self.hasil["prosesor_layanan_ms"] = (time.process_time() - mulai) * MILIDETIK
    hasil = self.layanan.panggil(PERISTIWA_DIUKUR, MUATAN[PERISTIWA_DIUKUR])
    self.hasil["pertama_layanan_ms"] = hasil.lama_total()

  def hitung_tagihan(self) -> None:
    """Mengubah lama eksekusi terukur menjadi gigabita detik per jam.

    Dua keadaan dihitung untuk penjalan, yaitu seluruh permintaan mulai dingin
    dan seluruhnya mulai hangat, sebab beban yang jarang memaksa keadaan
    pertama. Titik impasnya adalah jumlah permintaan per jam yang membuat kedua
    jalur menagih sama besar.
    """
    memori_fungsi = self.penjalan.pendaftar.memori_dipesan_mb(PERISTIWA_DIUKUR)
    tertagih_dingin = lama_tertagih_detik(self.hasil["lama_dingin_ms"])
    tertagih_hangat = lama_tertagih_detik(self.hasil["lama_hangat_ms"])
    per_dingin = gigabita_detik(memori_fungsi, tertagih_dingin)
    per_hangat = gigabita_detik(memori_fungsi, tertagih_hangat)
    layanan = gigabita_detik(MEMORI_LAYANAN_MB, JENDELA_TAGIHAN_DETIK)
    self.hasil["memori_fungsi_mb"] = memori_fungsi
    self.hasil["tertagih_dingin_ms"] = tertagih_dingin * MILIDETIK
    self.hasil["tertagih_hangat_ms"] = tertagih_hangat * MILIDETIK
    self.hasil["gbs_penjalan_dingin"] = per_dingin * PERMINTAAN_PER_JAM
    self.hasil["gbs_penjalan_hangat"] = per_hangat * PERMINTAAN_PER_JAM
    self.hasil["gbs_layanan"] = layanan
    self.hasil["impas_dingin"] = layanan / per_dingin
    self.hasil["impas_hangat"] = layanan / per_hangat

  def cetak_ringkasan(self) -> None:
    """Mencetak seluruh angka hasil pengukuran beserta hitungan tagihannya."""
    isi = self.hasil
    print(f"Contoh hangat sebelum dilepas : {isi['contoh_hangat']}")
    print(f"Contoh hangat sesudah dilepas : {isi['contoh_saat_nol']}")
    print(f"Modul fungsi saat hangat      : {isi['modul_saat_hangat']}")
    print(f"Modul fungsi saat nol         : {isi['modul_saat_nol']}")
    print(f"Modul fungsi pada layanan     : {isi['modul_layanan']}")
    print(f"Memori penjalan saat hangat   : "
          f"{isi['memori_hangat_kib'] - isi['memori_awal_kib']:.1f} KiB")
    print(f"Memori penjalan saat nol      : "
          f"{isi['memori_nol_kib'] - isi['memori_awal_kib']:.1f} KiB")
    print(f"Memori layanan saat menganggur: {isi['memori_layanan_kib']:.1f} KiB")
    print(f"Prosesor penjalan saat diam   : {isi['prosesor_penjalan_ms']:.3f} ms")
    print(f"Prosesor layanan saat diam    : {isi['prosesor_layanan_ms']:.3f} ms")
    print(f"Permintaan pertama penjalan   : {isi['pertama_penjalan_ms']:.4f} ms"
          f" (dingin={isi['pertama_penjalan_dingin']})")
    print(f"Permintaan pertama layanan    : {isi['pertama_layanan_ms']:.4f} ms")
    print(f"Lama penyiapan layanan        : {isi['siap_layanan_ms']:.3f} ms")
    print()
    print(f"Memori dipesan fungsi         : {isi['memori_fungsi_mb']} MB")
    print(f"Memori dipesan layanan        : {MEMORI_LAYANAN_MB} MB")
    print(f"Permintaan per jam            : {PERMINTAAN_PER_JAM}")
    print(f"Lama terukur dingin           : {isi['lama_dingin_ms']:.4f} ms")
    print(f"Lama tertagih dingin          : {isi['tertagih_dingin_ms']:.0f} ms")
    print(f"Lama terukur hangat           : {isi['lama_hangat_ms']:.4f} ms")
    print(f"Lama tertagih hangat          : {isi['tertagih_hangat_ms']:.0f} ms")
    print(f"Gigabita detik penjalan dingin: {isi['gbs_penjalan_dingin']:.2f}")
    print(f"Gigabita detik penjalan hangat: {isi['gbs_penjalan_hangat']:.2f}")
    print(f"Gigabita detik layanan hidup  : {isi['gbs_layanan']:.2f}")
    print(f"Titik impas bila dingin       : "
          f"{isi['impas_dingin']:,.0f} permintaan per jam")
    print(f"Titik impas bila hangat       : "
          f"{isi['impas_hangat']:,.0f} permintaan per jam")


if __name__ == "__main__":
  pengukur = PengukurSumberDaya()
  print("Tahap satu, mengukur memori kedua jalur.", flush=True)
  tracemalloc.start()
  pengukur.ukur_memori_penjalan()
  pengukur.ukur_memori_layanan()
  tracemalloc.stop()
  print("Tahap dua, mengukur waktu tanpa pencatat alokasi.", flush=True)
  pengukur.ukur_jendela_diam_penjalan()
  pengukur.ukur_lama_eksekusi()
  pengukur.ukur_waktu_layanan()
  pengukur.hitung_tagihan()
  print(flush=True)
  pengukur.cetak_ringkasan()
  # Keluarannya: Titik impas bila dingin       : 27,376 permintaan per jam
