#!/bin/bash
set -euo pipefail

DOMAIN="vpsdot.biz.id"
APP_NAME="api"
APP_USER="flaskuser"
APP_PORT=8000
PROJECT_DIR="/opt/$APP_NAME"

echo "➡️ Update paket & install dependency..."
sudo apt update
sudo apt install -y python3 python3-venv python3-pip nginx certbot python3-certbot-nginx

echo "➡️ Download aplikasi dari GitHub..."
sudo mkdir -p $PROJECT_DIR
sudo chown $USER:$USER $PROJECT_DIR
curl -sL https://raw.githubusercontent.com/DOT-SUNDA/dotdx/refs/heads/main/api.py -o $PROJECT_DIR/$APP_NAME.py

echo "➡️ Buat user khusus (tanpa password)..."
sudo adduser --system --group --no-create-home $APP_USER

echo "➡️ Setup virtualenv & install dependencies..."
python3 -m venv $PROJECT_DIR/venv
$PROJECT_DIR/venv/bin/pip install --upgrade pip flask requests

echo "➡️ Setup systemd service untuk Gunicorn..."
sudo tee /etc/systemd/system/$APP_NAME.service > /dev/null <<EOF
[Unit]
Description=Gunicorn for $APP_NAME
After=network.target

[Service]
User=$APP_USER
Group=www-data
WorkingDirectory=$PROJECT_DIR
Environment="PATH=$PROJECT_DIR/venv/bin"
ExecStart=$PROJECT_DIR/venv/bin/gunicorn --workers 3 --bind 127.0.0.1:$APP_PORT $APP_NAME:app

[Install]
WantedBy=multi-user.target
EOF

echo "➡️ Enable & start Gunicorn service..."
sudo systemctl daemon-reload
sudo systemctl enable $APP_NAME
sudo systemctl restart $APP_NAME

echo "➡️ Setup Nginx config..."
sudo tee /etc/nginx/sites-available/$APP_NAME > /dev/null <<EOF
server {
    listen 80;
    server_name $DOMAIN;

    location / {
        proxy_pass http://127.0.0.1:$APP_PORT;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
    }
}
EOF

sudo ln -sf /etc/nginx/sites-available/$APP_NAME /etc/nginx/sites-enabled/
sudo nginx -t && sudo systemctl reload nginx

echo "➡️ Pasang SSL Certbot (otomatis konfigurasi Nginx)..."
sudo certbot --nginx -d $DOMAIN --non-interactive --agree-tos -m admin@$DOMAIN

echo "✅ Selesai! Panel Flask berjalan di https://$DOMAIN"
