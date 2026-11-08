"""Subscriber baru yang disisipkan pada Latihan 3, yaitu recorder audit.

File ini berdiri sendiri dan tidak diimpor oleh satu pun susunan bawaan.
Ketiga file di dalam varian_audit/ adalah salinan susunan yang sudah
menyisipkannya, dan skrip ukur_perubahan.py menghitung selisih baris antara
keduanya.

Event processor ini sengaja menyalin request apa adanya, tanpa mengubah
isinya, sebab tugas audit memang hanya merekam. Ketiadaan perubahan itu pula
yang membuatnya aman dijalankan berbarengan dengan pemroses lain.

Cara menjalankan: python audit.py
"""

import threading

import domain

# Baris jurnal disimpan dalam memori saja, sama seperti riwayat pada Recorder,
# agar latihan tidak membutuhkan basis data.
AWALAN_JURNAL = "AUDIT"


class AuditRecorder:
  """Perekam jurnal audit bagi setiap request yang masuk.

  Event processor ini tidak mengubah isi request sama sekali. Tuntutannya
  satu, yaitu tidak ada request yang boleh lewat tanpa tercatat, sehingga
  jurnalnya dapat dibandingkan dengan riwayat recorder bila terjadi selisih.
  """

  nama = "audit"

  def __init__(self) -> None:
    """Menyiapkan jurnal kosong beserta kunci yang menjaga penambahannya."""
    self.jurnal = []
    self.kunci = threading.Lock()

  def tangani(self, request: domain.Request) -> str:
    """Menyalin request menjadi satu baris jurnal, lalu menandai langkahnya.

    Mengembalikan str berisi baris jurnal yang baru saja disimpan, sehingga
    pemanggil dapat memeriksanya tanpa membuka seluruh jurnal.
    """
    baris = (f"{AWALAN_JURNAL};{request.nomor};{request.kode_asal};"
             f"{request.nominal:.2f}")
    with self.kunci:
      self.jurnal.append(baris)
    request.catat_langkah(self.nama)
    return baris


if __name__ == "__main__":
  contoh = domain.buat_request(31, 1)
  recorder_audit = AuditRecorder()
  print(recorder_audit.tangani(contoh))
  # Keluarannya: AUDIT;31;USD;32000.00
