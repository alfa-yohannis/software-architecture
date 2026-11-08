"""Varian susunan sinkron sesudah recorder audit disisipkan.

File ini adalah salinan sinkron.py yang sudah memuat satu pemroses baru,
yaitu AuditRecorder dari audit.py. Perbandingannya dengan file aslinya
dihitung skrip ukur_perubahan.py, sehingga biaya perubahannya berupa angka,
bukan perkiraan.

Perhatikan bahwa penyisipannya menyentuh badan kirim(), yaitu alur bisnis yang
dijalankan pada setiap request, bukan sekadar bagian perakitannya.

Cara menjalankan: python -m varian_audit.sinkron
"""

import audit
import domain
import pemroses

# Jumlah langkah yang dilalui satu request. Angkanya ditulis di sini sebab
# susunan ini tidak punya daftar subscriber yang dapat dihitung, dan angka itu
# ikut berubah setiap kali satu pemroses disisipkan.
JUMLAH_LANGKAH = 4


class AlurSinkron:
  """Pemanggil yang menjalankan ketiga pemroses berurutan di thread sendiri.

  Urutan langkahnya tertulis di dalam badan kirim(), sehingga mengubah urutan
  atau menambah langkah berarti menyunting alur bisnisnya. Error dari pemroses
  mana pun dibiarkan naik ke pemanggil, sebab susunan ini memang tidak punya
  tempat lain untuk menampungnya.
  """

  def __init__(self, recorder, validator, notifier, recorder_audit) -> None:
    """Menerima ketiga pemroses sebagai ketergantungan yang sudah jadi.

    Validator sengaja dapat diganti dari luar, sebab uji ketahanan memasang
    validator yang gagal maupun yang lambat pada susunan yang sama.
    """
    self.recorder = recorder
    self.validator = validator
    self.notifier = notifier
    self.recorder_audit = recorder_audit

  def jumlah_langkah(self) -> int:
    """Mengembalikan int jumlah langkah yang harus dilalui satu request."""
    return JUMLAH_LANGKAH

  def pemroses_bernama(self, nama: str):
    """Mengembalikan objek pemroses yang namanya diminta, untuk pemeriksaan.

    Dipakai skrip pengujian agar riwayat dan pencacah setiap pemroses dapat
    dibaca dengan cara yang sama pada ketiga susunan.
    """
    return getattr(self, nama)

  def kirim(self, request: domain.Request) -> domain.Request:
    """Menjalankan ketiga langkah berurutan, lalu mengembalikan request-nya.

    Fungsi ini baru kembali sesudah pemberitahuan tersusun, sehingga waktu
    kembalinya sama dengan latensi ujung ke ujungnya.
    """
    self.recorder.tangani(request)
    self.validator.tangani(request)
    self.notifier.tangani(request)
    self.recorder_audit.tangani(request)
    return request

  def pesan_terkirim(self) -> int:
    """Mengembalikan int nol, sebab susunan ini tidak memakai antrean.

    Ketiga langkahnya dilalui sebagai pemanggilan langsung, sehingga tidak ada
    message yang dapat dihitung maupun ditahan.
    """
    return 0

  def antrean_backlog(self) -> int:
    """Mengembalikan int nol, sebab tidak ada antrean yang dapat menumpuk.

    Tekanan beban langsung dirasakan pemanggil dalam bentuk waktu tunggu.
    """
    return 0

  def galat_tercatat(self) -> int:
    """Mengembalikan int nol, sebab error tidak disimpan di mana pun.

    Error pemroses naik ke pemanggil lalu menghentikan pekerjaan berikutnya,
    sehingga tidak ada daftar yang dapat dihitung sesudahnya.
    """
    return 0

  def contoh_galat(self):
    """Mengembalikan None, sebab susunan ini tidak menyimpan catatan error."""
    return None

  def tutup(self) -> None:
    """Tidak melakukan apa pun, sebab susunan ini tidak menyalakan thread."""


def rakit(validator=None) -> AlurSinkron:
  """Merangkai susunan sinkron beserta ketiga pemrosesnya.

  Mengembalikan objek AlurSinkron yang siap menerima request. Validator
  pengganti dipakai uji ketahanan, sedangkan pengukuran latensi memakai
  validator biasa.
  """
  return AlurSinkron(pemroses.Recorder(), validator or pemroses.Validator(),
                     pemroses.Notifier(), audit.AuditRecorder())


if __name__ == "__main__":
  susunan = rakit()
  contoh = domain.buat_request(31, susunan.jumlah_langkah())
  susunan.kirim(contoh)
  print(contoh.pemberitahuan)
  # Keluarannya: Request 31 senilai Rp520,000,000 menunggu tinjauan
  print(f"Message lewat antrean: {susunan.pesan_terkirim()}")
  # Keluarannya: Message lewat antrean: 0
