#!/bin/bash

# URL GitHub untuk daftar API dan daftar link
API_LIST_URL="https://dot-store.biz.id/api_list.txt"
LINK_LIST_URL="https://dot-store.biz.id/link_list.txt"

# Fungsi untuk mengunduh daftar API
download_api_list() {
    echo "Mengunduh daftar API..."
    curl -s -o api_list.txt "$API_LIST_URL"
    if [[ $? -ne 0 || ! -f api_list.txt ]]; then
        echo "Gagal mengunduh daftar API. Periksa URL: $API_LIST_URL"
        exit 1
    fi
    echo "Berhasil mengunduh daftar API."
}

# Fungsi untuk mengunduh daftar link dan membagi menjadi file terpisah
split_links() {
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
    links_per_file=$(( (${#links[@]} + api_count - 1) / api_count ))

    rm -f link*.txt  # Hapus file sebelumnya
    for ((i=0; i<api_count; i++)); do
        start=$((i * links_per_file))
        end=$((start + links_per_file - 1))
        end=$((end > ${#links[@]} ? ${#links[@]} : end))
        printf "%s\n" "${links[@]:start:links_per_file}" > "link$((i + 1)).txt"
    done
    echo "Berhasil membagi link menjadi $api_count file."
}

# Fungsi untuk mengganti link.txt pada semua API
update_link_massal() {
    echo "=== Update link.txt Massal ==="

    mapfile -t api_list < api_list.txt

    for i in "${!api_list[@]}"; do
        api_url="${api_list[$i]}"
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

        echo "Mengirim ke API: $api_url dengan file $link_file"
        curl -s -X POST "$api_url/update-files" \
             -H "Content-Type: application/json" \
             -d "$json_payload"
        echo -e "\nLink berhasil diperbarui untuk $api_url."
    done
}

# Menu utama
while true; do
    clear
    echo "=== Menu API Manager Massal ==="
    echo "1. Unduh daftar API dan file link dari GitHub"
    echo "2. Bagi link menjadi file terpisah"
    echo "3. Update link.txt pada semua API"
    echo "4. Keluar"
    echo "================================"
    read -p "Pilih opsi [1-4]: " choice

    case $choice in
        1)
            download_api_list
            read -p "Tekan Enter untuk kembali ke menu..."
            ;;
        2)
            if [[ ! -f api_list.txt ]]; then
                echo "Daftar API tidak ditemukan. Silakan pilih opsi 1 terlebih dahulu untuk mengunduh."
                read -p "Tekan Enter untuk kembali ke menu..."
            else
                split_links
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
