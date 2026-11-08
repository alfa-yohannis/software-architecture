"""Server konversi mata uang yang melayani request lewat HTTP.

Server menyimpan tabel kurs dan menjalankan seluruh perhitungan. Klien tidak
menyimpan apa pun, sehingga tabel kurs cukup diperbarui di satu tempat.

Cara menjalankan: python server.py
"""

import json
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qs, urlparse

ALAMAT = "127.0.0.1"
PORT = 8000

KURS = {
  ("USD", "IDR"): 16250.0,
  ("EUR", "IDR"): 17600.0,
}


def hitung_konversi(kode_asal, kode_tujuan, nominal):
  """Menghitung konversi memakai tabel kurs yang hanya ada di server.

  Mengembalikan float berisi hasil konversi, atau None bila pasangan kursnya
  tidak ada di tabel.
  """
  nilai = KURS.get((kode_asal, kode_tujuan))
  return None if nilai is None else nominal * nilai


class Penangan(BaseHTTPRequestHandler):
  """Menangani satu request HTTP dari klien mana pun."""

  def do_GET(self):
    """Membaca parameter request, menghitung, lalu membalas dalam JSON."""
    alamat = urlparse(self.path)
    parameter = parse_qs(alamat.query)
    asal = parameter.get("asal", ["USD"])[0]
    tujuan = parameter.get("tujuan", ["IDR"])[0]
    teks_nominal = parameter.get("nominal", ["1"])[0]
    nominal = float(teks_nominal)

    hasil = hitung_konversi(asal, tujuan, nominal)
    if hasil is None:
      self.kirim(404, {"galat": "Kurs tidak tersedia"})
    else:
      self.kirim(200, {"asal": asal, "tujuan": tujuan, "hasil": hasil})

  def kirim(self, kode, isi):
    """Mengirim balasan JSON beserta kode statusnya."""
    teks = json.dumps(isi)
    badan = teks.encode("utf-8")
    panjang = len(badan)
    self.send_response(kode)
    self.send_header("Content-Type", "application/json")
    self.send_header("Content-Length", str(panjang))
    self.end_headers()
    self.wfile.write(badan)

  def log_message(self, format, *args):
    """Mematikan catatan bawaan agar keluaran pengukuran tetap bersih."""


if __name__ == "__main__":
  print(f"Server berjalan di http://{ALAMAT}:{PORT}")
  # Keluarannya: Server berjalan di http://127.0.0.1:8000
  server = HTTPServer((ALAMAT, PORT), Penangan)
  try:
    server.serve_forever()
  except KeyboardInterrupt:
    # Ctrl+C adalah cara mematikan server pada Latihan 1, bukan sebuah error.
    print("Server dihentikan.")
  finally:
    server.server_close()
