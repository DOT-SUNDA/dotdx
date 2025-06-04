#!/bin/bash

# URL GitHub untuk daftar API dan daftar link
API_LIST_URL="https://dot-store.biz.id/api_list.txt"
LINK_LIST_URL="https://dot-store.biz.id/link_list.txt"
BASE_URL="http://:8080" # Base URL tanpa domain/IP, tambahkan port atau endpoint di sini

# Fungsi untuk mengunduh daftar API dan daftar link, lalu membaginya
download_and_split_links() {
    echo "Mengunduh daftar API..."
    curl -s -o api_list.txt "$API_LIST_URL" || { echo "Gagal mengunduh daftar API."; exit 1; }

    echo "Mengunduh daftar link..."
    curl -s -o link_list.txt "$LINK_LIST_URL" || { echo "Gagal mengunduh daftar link."; exit 1; }

    echo "Membagi daftar link berdasarkan pola..."
    mapfile -t links < link_list.txt
    mapfile -t apis < api_list.txt
    api_count=${#apis[@]} # Hitung jumlah API

    # Hapus file link sebelumnya
    rm -f link*.txt

    # Distribusikan link sesuai pola
    for ((i=0; i<${#links[@]}; i++)); do
        group_index=$((i % api_count)) # Tentukan grup berdasarkan indeks
        echo "${links[i]}" >> "link$((group_index + 1)).txt"
    done

    echo "Berhasil membagi link menjadi $api_count file dengan pola yang ditentukan."
}

# Fungsi untuk mengganti waktu.json pada semua API
update_time_massal() {
    echo "=== Update waktu.json Massal ==="
    read -p "Masukkan tutup jam: " tutup_jam
    read -p "Masukkan buka jam: " buka_jam

    # Buat payload JSON menggunakan jq
    json_payload=$(jq -n --arg buka "$buka_jam" --arg tutup "$tutup_jam" \
        '{buka_jam: ($buka|tonumber), buka_menit: 30, tutup_jam: ($tutup|tonumber), tutup_menit: 0}')

    mapfile -t api_list < api_list.txt
    for domain_or_ip in "${api_list[@]}"; do
        api_url="${BASE_URL//:/http://$domain_or_ip}" # Bangun URL lengkap
        echo "Mengirim waktu.json ke $api_url"
        response=$(curl -s -X POST "$api_url/update-waktu" \
            -H "Content-Type: application/json" \
            -d "$json_payload")
        echo "Response: $response"
    done
}

# Fungsi untuk mengganti link.txt pada semua API
update_link_massal() {
    echo "=== Update link.txt Massal ==="
    mapfile -t api_list < api_list.txt

    for i in "${!api_list[@]}"; do
        link_file="link$((i + 1)).txt"
        [[ -f "$link_file" ]] || { echo "File $link_file tidak ditemukan."; continue; }

        links=$(<"$link_file")
        json_payload=$(jq -n --arg link "$links" '{link: $link}')

        domain_or_ip="${api_list[$i]}"
        api_url="${BASE_URL//:/http://$domain_or_ip}" # Bangun URL lengkap

        echo "Mengirim $link_file ke $api_url"
        response=$(curl -s -X POST "$api_url/update-link" \
            -H "Content-Type: application/json" \
            -d "$json_payload")
        echo "Response: $response"
    done
}

# Menu utama
while true; do
    clear
    echo "=== Menu API Manager Massal ==="
    echo "1. Unduh daftar API, daftar link, dan bagi link otomatis"
    echo "2. Update waktu.json pada semua API"
    echo "3. Update link.txt pada semua API"
    echo "4. Keluar"
    echo "================================"
    read -p "Pilih opsi [1-4]: " choice

    case $choice in
        1)
            download_and_split_links
            read -p "Tekan Enter untuk kembali ke menu..."
            ;;
        2)
            if [[ ! -f api_list.txt ]]; then
                echo "Daftar API tidak ditemukan. Silakan pilih opsi 1 terlebih dahulu untuk mengunduh."
                read -p "Tekan Enter untuk kembali ke menu..."
            else
                update_time_massal
                read -p "Tekan Enter untuk kembali ke menu..."
            fi
            ;;
        3)
            if [[ ! -f api_list.txt ]]; then
                echo "Daftar API tidak ditemukan. Silakan pilih opsi 1 terlebih dahulu untuk mengunduh."
                read -p "Tekan Enter untuk kembali ke menu..."
            else
                update_link_massal
                read -p "Tekan Enter untuk kembali ke menu..."
            fi
            ;;
        4)
            echo "Keluar dari program."
            exit 0
            ;;
        *)
            echo "Pilihan tidak valid, coba lagi."
            read -p "Tekan Enter untuk kembali ke menu..."
            ;;
    esac
done
