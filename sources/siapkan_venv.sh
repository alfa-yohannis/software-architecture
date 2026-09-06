#!/usr/bin/env bash
# Menyiapkan venv lokal dan memasang kebutuhan pustaka untuk seluruh skrip
# Python pada direktori sources/.
#
# Cara menjalankan, dari direktori mana pun:
#   bash sources/siapkan_venv.sh
#
# Venv dibuat di .venv pada akar repositori, sehingga satu venv dipakai
# bersama oleh semua bab. Direktori .venv sudah tercantum di .gitignore,
# sehingga tidak ikut terlacak. Penerjemah Python lain dapat dipilih lewat
# peubah lingkungan PYTHON, misalnya PYTHON=python3.12 bash siapkan_venv.sh.
set -euo pipefail

DIREKTORI_SKRIP="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
AKAR_REPO="$(dirname "$DIREKTORI_SKRIP")"
DIREKTORI_VENV="$AKAR_REPO/.venv"
BERKAS_KEBUTUHAN="$DIREKTORI_SKRIP/requirements.txt"
PYTHON="${PYTHON:-python3}"

if ! command -v "$PYTHON" > /dev/null 2>&1; then
  echo "Penerjemah $PYTHON tidak ditemukan. Pasang Python 3.10 atau lebih baru." >&2
  exit 1
fi

if [ ! -d "$DIREKTORI_VENV" ]; then
  echo "Membuat venv di $DIREKTORI_VENV"
  "$PYTHON" -m venv "$DIREKTORI_VENV"
else
  echo "Venv sudah ada di $DIREKTORI_VENV, pembuatan dilewati."
fi

PYTHON_VENV="$DIREKTORI_VENV/bin/python"

echo "Memutakhirkan pip"
"$PYTHON_VENV" -m pip install --quiet --upgrade pip

echo "Memasang kebutuhan dari $BERKAS_KEBUTUHAN"
"$PYTHON_VENV" -m pip install --quiet --requirement "$BERKAS_KEBUTUHAN"

# tkinter termasuk pustaka standar, tetapi pada Debian dan Ubuntu modulnya
# dipisah ke paket python3-tk. Bab 3 memakainya untuk antarmuka MV*, sehingga
# ketiadaannya diperiksa lebih awal daripada saat latihan berjalan.
if ! "$PYTHON_VENV" -c "import tkinter" > /dev/null 2>&1; then
  echo "Peringatan: modul tkinter tidak tersedia pada penerjemah ini." >&2
  echo "  Latihan Bab 3 membutuhkannya. Pada Debian dan Ubuntu, pasang" >&2
  echo "  paket python3-tk lalu jalankan ulang skrip ini." >&2
fi

echo
echo "Selesai. Aktifkan venv dengan:"
echo "  source $DIREKTORI_VENV/bin/activate"
echo "Lalu jalankan skrip dari direktori babnya, misalnya:"
echo "  cd sources/chapter02 && python basis_data.py"
