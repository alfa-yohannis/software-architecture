"""Plugin yang sengaja gagal saat diimpor, dipakai pada Latihan 2.

Galatnya dibuat terjadi pada tingkat modul, sehingga kegagalannya muncul saat
impor, bukan saat kelasnya diinstansiasi. Kegagalan seperti inilah yang paling
berbahaya, sebab pada eager activation satu file rusak dapat menghentikan
seluruh aplikasi.

Cara menjalankan: python inti.py rusak
"""

import domain

# Baris berikut sengaja dibiarkan salah. Pasangan mata uang ini tidak ada di
# dalam tabel, sehingga pembacaannya gagal saat modul diimpor.
KURS_TIDAK_ADA = domain.KURS[("JPY", "IDR")]


class BrokenPlugin:
  """Tidak pernah terbentuk, sebab modulnya gagal lebih dahulu."""

  def __init__(self, inti) -> None:
    """Tidak pernah dipanggil, sebab modulnya gagal sebelum kelas ini dibaca."""
    self.inti = inti

  def jalankan(self, argumen: list[str]) -> str:
    """Tidak pernah tercapai, dan keberadaannya hanya melengkapi contract.

    Kegagalan plugin ini terjadi pada tingkat modul, sehingga core berhenti
    jauh sebelum metode ini sempat dipanggil.
    """
    return "Plugin ini seharusnya tidak pernah berjalan"
