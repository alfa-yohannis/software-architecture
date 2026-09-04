"""Menguji logika keempat varian tanpa membuat objek antarmuka sungguhan.

Setiap varian diuji dengan cara yang paling sedikit menyentuh View. Jumlah
varian yang berhasil diuji tanpa View sama sekali menjadi ukuran kemudahan
pengujiannya.

Cara menjalankan: python uji_tanpa_antarmuka.py
"""

import mvc
import mvi
import mvp
import mvvm

NOMINAL_UJI = 100
HASIL_DIHARAPKAN = "Hasil: 1,625,000.00"


class ViewTiruan:
  """Pengganti View pasif pada MVP, hanya menyimpan teks yang diterimanya."""

  def __init__(self):
    self.teks = None

  def tampilkan(self, teks):
    """Menyimpan teks tanpa menampilkan apa pun."""
    self.teks = teks


def uji_mvc():
  """MVC tetap membutuhkan objek View, sebab Controller merujuk View."""
  model = mvc.Model()
  tampilan = mvc.View(model)
  hasil = mvc.Controller(model, tampilan).tangani_masukan("USD", "IDR", NOMINAL_UJI)
  return hasil == HASIL_DIHARAPKAN, "butuh View asli"


def uji_mvp():
  """MVP dapat diuji dengan View tiruan, sebab View-nya pasif."""
  tampilan = ViewTiruan()
  hasil = mvp.Presenter(mvp.Model(), tampilan).tangani_masukan("USD", "IDR", NOMINAL_UJI)
  return hasil == HASIL_DIHARAPKAN, "cukup View tiruan"


def uji_mvvm():
  """MVVM dapat diuji tanpa View sama sekali, cukup membaca propertinya."""
  view_model = mvvm.ViewModel(mvvm.Model())
  view_model.tangani_masukan("USD", "IDR", NOMINAL_UJI)
  return view_model.teks.nilai == HASIL_DIHARAPKAN, "tanpa View"


def uji_mvi():
  """MVI dapat diuji tanpa View sama sekali, cukup memanggil fungsi reduksi."""
  intent = mvi.IntentKonversi("USD", "IDR", NOMINAL_UJI)
  keadaan = mvi.reduksi(mvi.Keadaan(), intent)
  return keadaan.teks == HASIL_DIHARAPKAN, "tanpa View"


if __name__ == "__main__":
  for nama, fungsi_uji in [("mvc", uji_mvc), ("mvp", uji_mvp),
                           ("mvvm", uji_mvvm), ("mvi", uji_mvi)]:
    lulus, keterangan = fungsi_uji()
    print(f"{nama:<5} lulus={lulus}  cara uji: {keterangan}")
  # Keluarannya: mvc   lulus=True  cara uji: butuh View asli
