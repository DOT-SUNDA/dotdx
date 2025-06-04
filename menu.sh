#!/bin/bash

# URL GitHub untuk daftar API dan daftar link
API_LIST_URL="https://dot-store.biz.id/api_list.txt"
LINK_LIST_URL="https://dot-store.biz.id/link_list.txt"
PORT=5000  # Port yang digunakan untuk semua API

# Fungsi untuk mengunduh daftar API dan daftar link, lalu membaginya
download_and_split_links() {
    echo "Mengunduh daftar API..."
    curl -s -o api_list.txt "$API_LIST_URL"
    if [[ $? -ne 0 || ! -f api_list.txt ]]; then
        echo "Gagal mengunduh daftar API. Periksa URL: $API_LIST_URL"
        exit 1
    fi
    echo "Berhasil mengunduh daftar API."

    echo "Mengunduh daftar link..."
    curl -s -o link_list.txt "$LINK_LIST_URL"
    if [[ $? -ne 0 || ! -f link_list.txt ]]; then
        echo "Gagal mengunduh daftar link. Periksa URL: $LINK_LIST_URL"
        exit 1
    fi
    echo "Berhasil mengunduh daftar link."

    echo "Membagi daftar link menjadi file terpisah..."
    mapfile -t links < link_list.txt
    api_count=$(wc -l < api_list.txt)
    
    rm -f link*.txt  # Hapus file sebelumnya
    for ((i = 0; i < ${#links[@]}; i++)); do
        group_index=$((i % api_count))
        echo "${links[i]}" >> "link$((group_index + 1)).txt"
    done
    echo "Berhasil membagi link menjadi $api_count file."
}

# Fungsi untuk mengganti waktu.json pada semua API
update_time_massal() {
    echo "=== Update waktu.json Massal ==="
    read -p "Masukkan tutup jam: " tutup_jam
    read -p "Masukkan buka jam: " buka_jam
    json_payload=$(cat <<EOF
{
    "buka_jam": $buka_jam,
    "buka_menit": 30,
    "tutup_jam": $tutup_jam,
    "tutup_menit": 0
}
EOF
)

    mapfile -t api_list < api_list.txt
    for api_ip in "${api_list[@]}"; do
        api_url="http://${api_ip}:${PORT}/update-waktu"
        echo "Mengirim waktu.json ke API: $api_url"
        response=$(curl -s -X POST "$api_url" \
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
        api_ip="${api_list[$i]}"
        api_url="http://${api_ip}:${PORT}/update-link"
        link_file="link$((i + 1)).txt"

        if [[ ! -f "$link_file" ]]; then
            echo "File $link_file tidak ditemukan untuk API $api_url. Lewati."
            continue
        fi

        # Baca isi file link
        links=$(<"$link_file")

        # Format data JSON
        json_payload=$(cat <<EOF
{
    "link": "$(echo "$links" | sed ':a;N;$!ba;s/\n/\\n/g')"
}
EOF
)

        echo "Mengirim link.txt ke API: $api_url dengan file $link_file"
        response=$(curl -s -X POST "$api_url" \
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
