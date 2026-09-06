#!/usr/bin/env bash
# Menghasilkan ulang diagram PlantUML Bab 2 menjadi PDF di direktori figures/.
#
# Cara menjalankan, dari direktori mana pun:
#   bash sources/chapter02/diagram/buat_diagram.sh
#
# Keluaran PlantUML diambil sebagai SVG lebih dahulu, lalu diubah menjadi PDF
# dengan rsvg-convert. Jalur langsung ke PDF tidak dipakai sebab pengubahnya
# tidak mengenali font Titillium Web dan menggantinya dengan Times. Melalui
# SVG, fontnya dicari lewat fontconfig lalu ditanam ke dalam PDF.
#
# Berkas PDF hasilnya diletakkan di figures/ agar naskah bab dan slide memakai
# berkas yang sama persis, dan ikut dilacak Git sehingga modul tetap dapat
# dikompilasi pada mesin yang belum memasang PlantUML.
set -euo pipefail

DIREKTORI_SKRIP="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
AKAR_REPO="$(cd "$DIREKTORI_SKRIP/../../.." && pwd)"
DIREKTORI_KELUARAN="$AKAR_REPO/figures"
DIREKTORI_SEMENTARA="$(mktemp -d)"
trap 'rm -rf "$DIREKTORI_SEMENTARA"' EXIT

for perkakas in plantuml rsvg-convert; do
  if ! command -v "$perkakas" > /dev/null 2>&1; then
    echo "$perkakas tidak ditemukan. Pasang lebih dahulu." >&2
    exit 1
  fi
done

# Pemeriksaan memakai fc-match, bukan pipa ke grep, sebab grep yang berhenti
# lebih awal membuat pipefail menganggap seluruh pipa gagal.
if [ "$(fc-match --format='%{family}' 'Titillium Web')" != "Titillium Web" ]; then
  echo "Peringatan: font Titillium Web belum terpasang di sistem." >&2
  echo "  Salin berkas dari module/fonts/ ke ~/.local/share/fonts lalu" >&2
  echo "  jalankan fc-cache -f, agar diagramnya memakai font yang benar." >&2
fi

for berkas in "$DIREKTORI_SKRIP"/*.puml; do
  nama="$(basename "${berkas%.puml}")"
  echo "Menghasilkan $nama.pdf"
  plantuml -tsvg -output "$DIREKTORI_SEMENTARA" "$berkas"
  rsvg-convert --format=pdf \
    --output "$DIREKTORI_KELUARAN/$nama.pdf" \
    "$DIREKTORI_SEMENTARA/$nama.svg"
done

echo "Selesai. Berkas PDF tersimpan di $DIREKTORI_KELUARAN"
