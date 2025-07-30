#!/bin/bash

# Warna teks
green='\e[32m'
red='\e[31m'
cyan='\e[36m'
nc='\e[0m' # no color

# Nama direktori dan file
REPO_NAME="stratum-ethproxy"
REPO_DIR="$HOME/$REPO_NAME"
ENV_FILE="$REPO_DIR/.env"
LOG_FILE="$REPO_DIR/npm-debug.log"

function install_dependencies() {
    echo -e "${cyan}➤ Menginstal Docker dan NPM...${nc}"
    sudo apt update && sudo apt install -y docker.io npm screen
    echo -e "${green}✓ Selesai menginstal dependensi.${nc}"
}

function clone_and_install() {
    if [ -d "$REPO_DIR" ]; then
        echo -e "${red}✗ Repositori sudah ada. Lewati clone.${nc}"
    else
        git clone https://github.com/oneevil/stratum-ethproxy "$REPO_DIR"
    fi

    cd "$REPO_DIR" || exit
    echo -e "${cyan}➤ Menginstal dependensi NPM...${nc}"
    npm install
    echo -e "${green}✓ Selesai menginstal dependensi NPM.${nc}"
}

function setup_env() {
    mkdir -p "$REPO_DIR"
    LOCAL_IP=$(hostname -I | awk '{print $1}')
    cat > "$ENV_FILE" <<EOL
REMOTE_HOST=nomp.mofumofu.me
REMOTE_PORT=3391
REMOTE_PASSWORD=x
LOCAL_HOST=$LOCAL_IP
LOCAL_PORT=443
EOL
    echo -e "${green}✓ File .env berhasil dibuat.${nc}"
}

function start_stratum() {
    if screen -list | grep -q "GULA"; then
        echo -e "${red}✗ Proses sudah berjalan. Stop dulu sebelum menjalankan ulang.${nc}"
    else
        cd "$REPO_DIR" || exit
        echo -e "${cyan}➤ Menjalankan proses di screen 'GULA'...${nc}"
        screen -dmS GULA npm start
        echo -e "${green}✓ Proses berhasil dijalankan di screen.${nc}"
    fi
}

function update_remote_target() {
    if [ ! -f "$ENV_FILE" ]; then
        echo -e "${red}✗ File .env belum ditemukan. Jalankan opsi setup dulu.${nc}"
        return
    fi

    echo -e "${cyan}➤ Format input: host:port (contoh: power2b.asia.mine.zergpool.com:7445)${nc}"
    read -rp "Masukkan Remote Target: " input

    new_host=$(echo "$input" | cut -d':' -f1)
    new_port=$(echo "$input" | cut -d':' -f2)

    if [[ -z "$new_host" || -z "$new_port" ]]; then
        echo -e "${red}✗ Format salah. Gunakan host:port${nc}"
        return
    fi

    sed -i "s/^REMOTE_HOST=.*/REMOTE_HOST=$new_host/" "$ENV_FILE"
    sed -i "s/^REMOTE_PORT=.*/REMOTE_PORT=$new_port/" "$ENV_FILE"
    echo -e "${green}✓ Konfigurasi REMOTE_HOST dan REMOTE_PORT diperbarui.${nc}"

    echo -e "${cyan}➤ Restart proses dengan konfigurasi baru...${nc}"
    screen -S GULA -X quit 2>/dev/null
    cd "$REPO_DIR" || exit
    screen -dmS GULA npm start
    echo -e "${green}✓ Proses berhasil dijalankan ulang.${nc}"
}

function check_status() {
    echo -e "${cyan}➤ Status proses GULA:${nc}"
    if screen -list | grep -q "GULA"; then
        echo -e "${green}✓ Proses sedang berjalan.${nc}"
    else
        echo -e "${red}✗ Proses tidak berjalan.${nc}"
    fi
}

function show_env() {
    if [ -f "$ENV_FILE" ]; then
        echo -e "${cyan}➤ Isi file .env:${nc}"
        cat "$ENV_FILE"
    else
        echo -e "${red}✗ File .env tidak ditemukan.${nc}"
    fi
}

function view_logs() {
    if screen -list | grep -q "GULA"; then
        echo -e "${cyan}➤ Menampilkan log real-time (Ctrl+C untuk keluar):${nc}"
        sleep 1
        screen -r GULA
    else
        echo -e "${red}✗ Proses GULA tidak berjalan.${nc}"
    fi
}

function show_menu() {
    echo -e "${cyan}"
    echo "========== MENU STRATUM GULA =========="
    echo "1. Install dependensi (Docker, NPM)"
    echo "2. Clone dan Install stratum-ethproxy"
    echo "3. Setup konfigurasi .env"
    echo "4. Jalankan stratum-gula"
    echo "5. Ganti Remote Host & Port"
    echo "6. Cek Status Proses"
    echo "7. Tampilkan Isi .env"
    echo "8. Lihat Log Proses"
    echo "0. Keluar"
    echo "========================================"
    echo -e "${nc}"
}

while true; do
    show_menu
    read -rp "Pilih opsi [0-8]: " opt
    case $opt in
        1) install_dependencies ;;
        2) clone_and_install ;;
        3) setup_env ;;
        4) start_stratum ;;
        5) update_remote_target ;;
        6) check_status ;;
        7) show_env ;;
        8) view_logs ;;
        0) echo "Keluar..."; break ;;
        *) echo -e "${red}✗ Pilihan tidak valid.${nc}" ;;
    esac
    echo
done
