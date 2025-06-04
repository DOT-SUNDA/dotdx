#!/bin/bash

# Autoscript untuk setup API Manager dengan Flask
echo "🚀 Mulai setup API Manager..."

# Periksa apakah Python 3 dan pip terinstal
echo "📦 Memeriksa Python3 dan pip..."
if ! command -v python3 &>/dev/null || ! command -v pip3 &>/dev/null; then
    echo "❌ Python3 atau pip3 tidak ditemukan. Silakan instal terlebih dahulu."
    exit 1
fi

# Membuat virtual environment
echo "🐍 Membuat virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Instal Flask dan pustaka lainnya
echo "📚 Menginstal Flask dan pustaka tambahan..."
pip3 install flask requests

# Membuat direktori aplikasi
APP_DIR="api_manager"
TEMPLATES_DIR="$APP_DIR/templates"
STATIC_DIR="$APP_DIR/static"

echo "📂 Membuat struktur direktori aplikasi..."
mkdir -p $TEMPLATES_DIR $STATIC_DIR

# Membuat file aplikasi utama
APP_FILE="$APP_DIR/app.py"
cat <<EOF >$APP_FILE
from flask import Flask, render_template, request, redirect, url_for, jsonify
import os
import requests

app = Flask(__name__)

# Konfigurasi
TEMP_FOLDER = "temp"
os.makedirs(TEMP_FOLDER, exist_ok=True)
API_LIST_FILE = os.path.join(TEMP_FOLDER, "api_list.txt")
LINK_LIST_FILE = os.path.join(TEMP_FOLDER, "link_list.txt")
PORT = 5000

def read_file(filename):
    if os.path.exists(filename):
        with open(filename, 'r') as file:
            return file.read().strip().split('\n')
    return []

def write_file(filename, data):
    with open(filename, 'w') as file:
        file.write('\n'.join(data))

def split_links(api_list, links):
    split_result = {}
    api_count = len(api_list)
    for i, link in enumerate(links):
        group_index = i % api_count
        api = api_list[group_index]
        if api not in split_result:
            split_result[api] = []
        split_result[api].append(link)
    return split_result

@app.route("/")
def index():
    api_list = read_file(API_LIST_FILE)
    link_list = read_file(LINK_LIST_FILE)
    return render_template("index.html", api_list=api_list, link_list=link_list)

@app.route("/add_api", methods=["POST"])
def add_api():
    api = request.form.get("api")
    api_list = read_file(API_LIST_FILE)
    if api and api not in api_list:
        api_list.append(api)
        write_file(API_LIST_FILE, api_list)
    return redirect(url_for("index"))

@app.route("/add_link", methods=["POST"])
def add_link():
    link = request.form.get("link")
    link_list = read_file(LINK_LIST_FILE)
    if link and link not in link_list:
        link_list.append(link)
        write_file(LINK_LIST_FILE, link_list)
    return redirect(url_for("index"))

@app.route("/split", methods=["POST"])
def split():
    api_list = read_file(API_LIST_FILE)
    link_list = read_file(LINK_LIST_FILE)
    if not api_list or not link_list:
        return jsonify({"status": "error", "message": "Daftar API atau Link kosong."})
    
    split_result = split_links(api_list, link_list)
    for api, links in split_result.items():
        file_name = os.path.join(TEMP_FOLDER, f"link_{api}.txt")
        write_file(file_name, links)
    
    return jsonify({"status": "success", "message": "Link berhasil dibagi."})

@app.route("/update_time", methods=["POST"])
def update_time():
    buka_jam = request.form.get("buka_jam")
    tutup_jam = request.form.get("tutup_jam")
    if not buka_jam or not tutup_jam:
        return jsonify({"status": "error", "message": "Jam buka dan tutup diperlukan."})

    api_list = read_file(API_LIST_FILE)
    json_payload = {
        "buka_jam": int(buka_jam),
        "buka_menit": 30,
        "tutup_jam": int(tutup_jam),
        "tutup_menit": 0
    }

    responses = {}
    for api in api_list:
        url = f"http://{api}:{PORT}/update-waktu"
        try:
            response = requests.post(url, json=json_payload)
            responses[api] = response.text
        except requests.RequestException as e:
            responses[api] = str(e)

    return jsonify({"status": "success", "responses": responses})

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=8080)
EOF

# Membuat file HTML template
TEMPLATE_FILE="$TEMPLATES_DIR/index.html"
cat <<EOF >$TEMPLATE_FILE
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>API Manager Panel</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0-alpha3/dist/css/bootstrap.min.css" rel="stylesheet">
</head>
<body class="bg-light">
    <div class="container mt-4">
        <h1 class="mb-4">API Manager Panel</h1>
        <div class="row">
            <div class="col-md-6">
                <h3>Daftar API</h3>
                <form method="POST" action="/add_api" class="mb-3">
                    <div class="input-group">
                        <input type="text" name="api" class="form-control" placeholder="Tambahkan API (IP/Domain)">
                        <button class="btn btn-primary">Tambah</button>
                    </div>
                </form>
                <ul class="list-group">
                    {% for api in api_list %}
                        <li class="list-group-item">{{ api }}</li>
                    {% endfor %}
                </ul>
            </div>
            <div class="col-md-6">
                <h3>Daftar Link</h3>
                <form method="POST" action="/add_link" class="mb-3">
                    <div class="input-group">
                        <input type="text" name="link" class="form-control" placeholder="Tambahkan Link">
                        <button class="btn btn-primary">Tambah</button>
                    </div>
                </form>
                <ul class="list-group">
                    {% for link in link_list %}
                        <li class="list-group-item">{{ link }}</li>
                    {% endfor %}
                </ul>
            </div>
        </div>
    </div>
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0-alpha3/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
EOF

# Jalankan aplikasi Flask
echo "🚀 Menjalankan API Manager..."
cd $APP_DIR
python3 app.py
