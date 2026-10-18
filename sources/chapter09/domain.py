"""Permintaan konversi kurs beserta aturan bisnis yang dipakai ketiga susunan.

Berkas ini menyimpan satu-satunya sumber kebenaran tentang pekerjaan yang
diukur pada bab ini. Ketiga susunan, yaitu panggilan berantai langsung,
topologi broker, dan topologi mediator, memanggil fungsi yang sama persis dari
sini. Karena pekerjaannya sama, selisih waktu yang terukur hanya berasal dari
cara pesannya disampaikan.

Setiap permintaan membawa tanda selesai berupa threading.Event. Tanda itu
dibuka ketika seluruh langkah yang diharapkan sudah tercatat, dan skrip
pengukuran memakainya untuk menghitung latensi ujung ke ujung pada susunan yang
bekerja di thread lain.

Cara menjalankan: berkas ini diimpor, bukan dijalankan langsung.
"""

import threading

# Kurs contoh, sama dengan tabel pada Bab 5 agar angkanya dapat dibandingkan
# antar bab. Nilainya tetap, sebab bab ini mengukur penyampaian pesan, bukan
# ketepatan kursnya.
KURS = {
  ("USD", "IDR"): 16250.0,
  ("EUR", "IDR"): 17600.0,
  ("SGD", "IDR"): 12100.0,
}

# Permintaan yang nilainya menyamai atau melampaui batas ini ditandai untuk
# ditinjau petugas. Batasnya adalah aturan contoh bab ini, bukan kutipan aturan
# lembaga mana pun.
BATAS_TINJAUAN = 500_000_000.0

# Nominal permintaan diputar pada rentang ini agar sebagian melewati batas
# tinjauan dan sebagian lagi tidak.
NOMINAL_DASAR = 1000.0
PANJANG_PUTARAN_NOMINAL = 50


class Permintaan:
  """Satu permintaan konversi yang menempuh beberapa langkah pemrosesan.

  Objek ini berpindah antar thread pada susunan broker dan mediator, sehingga
  pencatatan langkahnya dijaga sebuah Lock. Tanda selesai berupa Event dibuka
  sekali saja, yaitu ketika langkah terakhir yang diharapkan sudah tercatat.
  """

  def __init__(self, nomor: int, kode_asal: str, kode_tujuan: str,
               nominal: float, langkah_diharapkan: int) -> None:
    """Menyiapkan satu permintaan beserta jumlah langkah yang harus dilaluinya.

    Jumlah langkah diterima dari susunan yang akan menanganinya, sebab susunan
    yang sama dapat berjalan dengan tiga atau empat pemroses. Tanpa angka itu,
    tanda selesai tidak tahu kapan harus dibuka.
    """
    self.nomor = nomor
    self.kode_asal = kode_asal
    self.kode_tujuan = kode_tujuan
    self.nominal = nominal
    self.langkah_diharapkan = langkah_diharapkan
    self.jejak = []
    self.nilai_rupiah = None
    self.perlu_tinjauan = False
    self.pemberitahuan = None
    self.kunci = threading.Lock()
    self.selesai = threading.Event()

  def catat_langkah(self, nama: str) -> int:
    """Menandai satu langkah selesai, lalu membuka tanda selesai bila genap.

    Pemanggilnya adalah pemroses yang baru saja menuntaskan bagiannya.
    Mengembalikan int berisi jumlah langkah yang sudah tercatat sampai saat
    itu, sehingga pemanggil dapat mengetahui posisinya di dalam rangkaian.
    """
    with self.kunci:
      self.jejak.append(nama)
      genap = len(self.jejak) >= self.langkah_diharapkan
      jumlah = len(self.jejak)
    if genap:
      self.selesai.set()
    return jumlah

  def tunggu(self, batas_detik: float) -> bool:
    """Menunggu seluruh langkah selesai, paling lama selama batas yang diberi.

    Mengembalikan bool bernilai True bila seluruh langkah selesai sebelum batas
    waktunya habis, dan False bila rangkaiannya putus di tengah jalan.
    """
    return self.selesai.wait(batas_detik)


def nilai_kurs(kode_asal: str, kode_tujuan: str):
  """Mengembalikan float kurs satu pasangan mata uang, atau None bila kosong."""
  return KURS.get((kode_asal, kode_tujuan))


def hitung_konversi(kode_asal: str, kode_tujuan: str, nominal: float) -> float:
  """Mengalikan nominal dengan kursnya, lalu menolak masukan yang tidak wajar.

  Mengembalikan float berisi nilai hasil konversi. Pasangan mata uang yang
  tidak ada di dalam tabel dijawab dengan LookupError, sebab menebak kurs jauh
  lebih berbahaya daripada berhenti.
  """
  if nominal <= 0:
    raise ValueError("Nominal harus lebih besar dari nol")
  kurs = nilai_kurs(kode_asal, kode_tujuan)
  if kurs is None:
    raise LookupError(f"Kurs {kode_asal} ke {kode_tujuan} tidak tersedia")
  return nominal * kurs


def buat_permintaan(nomor: int, langkah_diharapkan: int) -> Permintaan:
  """Membuat satu permintaan contoh yang nominalnya berputar pada rentang tetap.

  Nominalnya sengaja berputar agar sebagian permintaan melewati batas tinjauan
  dan sebagian lagi tidak, sehingga pemeriksa benar-benar mengambil keputusan.
  Mengembalikan objek Permintaan yang siap dikirim ke susunan mana pun.
  """
  kelipatan = 1 + nomor % PANJANG_PUTARAN_NOMINAL
  return Permintaan(nomor, "USD", "IDR", NOMINAL_DASAR * kelipatan,
                    langkah_diharapkan)
