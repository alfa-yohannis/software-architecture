"""Varian susunan sinkron sesudah pencatat audit disisipkan.

Berkas ini adalah salinan sinkron.py yang sudah memuat satu pemroses baru,
yaitu PencatatAudit dari audit.py. Perbandingannya dengan berkas aslinya
dihitung skrip ukur_perubahan.py, sehingga biaya perubahannya berupa angka,
bukan perkiraan.

Perhatikan bahwa penyisipannya menyentuh badan kirim(), yaitu alur bisnis yang
dijalankan pada setiap permintaan, bukan sekadar bagian perakitannya.

Cara menjalankan: python -m varian_audit.sinkron
"""

import audit
import domain
import pemroses

# Jumlah langkah yang ditempuh satu permintaan. Angkanya ditulis di sini sebab
# susunan ini tidak punya daftar pelanggan yang dapat dihitung, dan angka itu
# ikut berubah setiap kali satu pemroses disisipkan.
JUMLAH_LANGKAH = 4


class AlurSinkron:
  """Pemanggil yang menjalankan ketiga pemroses berurutan di thread sendiri.

  Urutan langkahnya tertulis di dalam badan kirim(), sehingga mengubah urutan
  atau menambah langkah berarti menyunting alur bisnisnya. Galat dari pemroses
  mana pun dibiarkan naik ke pemanggil, sebab susunan ini memang tidak punya
  tempat lain untuk menampungnya.
  """

  def __init__(self, pencatat, pemeriksa, pemberitahu, pencatat_audit) -> None:
    """Menerima ketiga pemroses sebagai ketergantungan yang sudah jadi.

    Pemeriksa sengaja dapat diganti dari luar, sebab uji ketahanan memasang
    pemeriksa yang gagal maupun yang lambat pada susunan yang sama.
    """
    self.pencatat = pencatat
    self.pemeriksa = pemeriksa
    self.pemberitahu = pemberitahu
    self.pencatat_audit = pencatat_audit

  def jumlah_langkah(self) -> int:
    """Mengembalikan int jumlah langkah yang harus dilalui satu permintaan."""
    return JUMLAH_LANGKAH

  def pemroses_bernama(self, nama: str):
    """Mengembalikan objek pemroses yang namanya diminta, untuk pemeriksaan.

    Dipakai skrip pengujian agar riwayat dan pencacah setiap pemroses dapat
    dibaca dengan cara yang sama pada ketiga susunan.
    """
    return getattr(self, nama)

  def kirim(self, permintaan: domain.Permintaan) -> domain.Permintaan:
    """Menjalankan ketiga langkah berurutan, lalu mengembalikan permintaannya.

    Fungsi ini baru kembali sesudah pemberitahuan tersusun, sehingga waktu
    kembalinya sama dengan latensi ujung ke ujungnya.
    """
    self.pencatat.tangani(permintaan)
    self.pemeriksa.tangani(permintaan)
    self.pemberitahu.tangani(permintaan)
    self.pencatat_audit.tangani(permintaan)
    return permintaan

  def pesan_terkirim(self) -> int:
    """Mengembalikan int nol, sebab susunan ini tidak memakai antrean.

    Ketiga langkahnya ditempuh sebagai pemanggilan langsung, sehingga tidak ada
    pesan yang dapat dihitung maupun ditahan.
    """
    return 0

  def antrean_tertahan(self) -> int:
    """Mengembalikan int nol, sebab tidak ada antrean yang dapat menumpuk.

    Tekanan beban langsung dirasakan pemanggil dalam bentuk waktu tunggu.
    """
    return 0

  def galat_tercatat(self) -> int:
    """Mengembalikan int nol, sebab galat tidak disimpan di mana pun.

    Galat pemroses naik ke pemanggil lalu menghentikan pekerjaan berikutnya,
    sehingga tidak ada daftar yang dapat dihitung sesudahnya.
    """
    return 0

  def contoh_galat(self):
    """Mengembalikan None, sebab susunan ini tidak menyimpan catatan galat."""
    return None

  def tutup(self) -> None:
    """Tidak melakukan apa pun, sebab susunan ini tidak menyalakan thread."""


def rakit(pemeriksa=None) -> AlurSinkron:
  """Merangkai susunan sinkron beserta ketiga pemrosesnya.

  Mengembalikan objek AlurSinkron yang siap menerima permintaan. Pemeriksa
  pengganti dipakai uji ketahanan, sedangkan pengukuran latensi memakai
  pemeriksa biasa.
  """
  return AlurSinkron(pemroses.Pencatat(), pemeriksa or pemroses.Pemeriksa(),
                     pemroses.Pemberitahu(), audit.PencatatAudit())


if __name__ == "__main__":
  susunan = rakit()
  contoh = domain.buat_permintaan(31, susunan.jumlah_langkah())
  susunan.kirim(contoh)
  print(contoh.pemberitahuan)
  # Keluarannya: Permintaan 31 senilai Rp520,000,000 menunggu tinjauan
  print(f"Pesan lewat antrean: {susunan.pesan_terkirim()}")
  # Keluarannya: Pesan lewat antrean: 0
