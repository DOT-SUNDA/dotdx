from flask import Flask, request, render_template_string, redirect, url_for
import math
import json
import requests

app = Flask(__name__)

# List untuk menyimpan API dan link
data = {
    "api_list": [],
    "link_list": []
}
PORT = 5000

# Template HTML untuk panel
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="id">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Manajemen API & Link</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0-alpha3/dist/css/bootstrap.min.css" rel="stylesheet">
</head>
<body>
<div class="container mt-4">
    <h1 class="mb-4">Panel Manajemen API & Link</h1>

    <div class="mb-4">
        <h3>Tambahkan API</h3>
        <form action="/add-api" method="post">
            <div class="mb-3">
                <label for="apiTextarea" class="form-label">Tambahkan API (satu API per baris)</label>
                <textarea name="apis" class="form-control" id="apiTextarea" rows="5" placeholder="192.168.1.1\n192.168.1.2\n192.168.1.3"></textarea>
            </div>
            <button class="btn btn-primary" type="submit">Tambah API</button>
        </form>
    </div>

    <div class="mb-4">
        <h3>Tambahkan Link</h3>
        <form action="/add-link" method="post">
            <div class="mb-3">
                <label for="linkTextarea" class="form-label">Tambahkan Link (satu link per baris)</label>
                <textarea name="links" class="form-control" id="linkTextarea" rows="5" placeholder="https://example.com\nhttps://another.com"></textarea>
            </div>
            <button class="btn btn-success" type="submit">Tambah Link</button>
        </form>
    </div>

    <div class="mb-4">
        <h3>Bagi Link ke API</h3>
        <form action="/split-links" method="post">
            <button class="btn btn-warning" type="submit">Bagi Link</button>
        </form>
    </div>

    <div class="mb-4">
        <h3>Update Waktu</h3>
        <form action="/update-waktu" method="post">
            <div class="mb-3">
                <label for="tutupJam" class="form-label">Tutup Jam</label>
                <input type="number" name="tutup_jam" class="form-control" id="tutupJam" required>
            </div>
            <div class="mb-3">
                <label for="bukaJam" class="form-label">Buka Jam</label>
                <input type="number" name="buka_jam" class="form-control" id="bukaJam" required>
            </div>
            <button class="btn btn-info" type="submit">Update Waktu</button>
        </form>
    </div>

    <div class="mb-4">
        <h3>Update Link</h3>
        <form action="/update-link" method="post">
            <button class="btn btn-secondary" type="submit">Update Link</button>
        </form>
    </div>

    <div class="mb-4">
        <h3>Daftar API</h3>
        <ul class="list-group">
            {% for api in api_list %}
            <li class="list-group-item d-flex justify-content-between align-items-center">
                {{ api }}
                <a href="/delete-api/{{ loop.index0 }}" class="btn btn-danger btn-sm">Hapus</a>
            </li>
            {% endfor %}
        </ul>
    </div>

    <div class="mb-4">
        <h3>Daftar Link</h3>
        <ul class="list-group">
            {% for link in link_list %}
            <li class="list-group-item d-flex justify-content-between align-items-center">
                {{ link }}
                <a href="/delete-link/{{ loop.index0 }}" class="btn btn-danger btn-sm">Hapus</a>
            </li>
            {% endfor %}
        </ul>
    </div>
</div>
<script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0-alpha3/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
"""

@app.route("/")
def index():
    return render_template_string(HTML_TEMPLATE, api_list=data["api_list"], link_list=data["link_list"])

@app.route("/add-api", methods=["POST"])
def add_api():
    apis = request.form.get("apis", "")
    if apis:
        for api in apis.splitlines():
            api = api.strip()
            if api and api not in data["api_list"]:
                data["api_list"].append(api)
    return redirect(url_for("index"))

@app.route("/add-link", methods=["POST"])
def add_link():
    links = request.form.get("links", "")
    if links:
        for link in links.splitlines():
            link = link.strip()
            if link and link not in data["link_list"]:
                data["link_list"].append(link)
    return redirect(url_for("index"))

@app.route("/delete-api/<int:index>")
def delete_api(index):
    if 0 <= index < len(data["api_list"]):
        data["api_list"].pop(index)
    return redirect(url_for("index"))

@app.route("/delete-link/<int:index>")
def delete_link(index):
    if 0 <= index < len(data["link_list"]):
        data["link_list"].pop(index)
    return redirect(url_for("index"))

@app.route("/split-links", methods=["POST"])
def split_links():
    if not data["api_list"]:
        return "Tidak ada API yang tersedia untuk pembagian link.", 400

    api_count = len(data["api_list"])
    split_result = [[] for _ in range(api_count)]

    for i, link in enumerate(data["link_list"]):
        split_result[i % api_count].append(link)

    for i, api in enumerate(data["api_list"]):
        with open(f"link{i + 1}.txt", "w") as f:
            f.write("\n".join(split_result[i]))

    return redirect(url_for("index"))

@app.route("/update-waktu", methods=["POST"])
def update_waktu():
    tutup_jam = request.form.get("tutup_jam")
    buka_jam = request.form.get("buka_jam")

    if not tutup_jam or not buka_jam:
        return "Tutup jam dan buka jam harus diisi.", 400

    json_payload = {
        "buka_jam": int(buka_jam),
        "buka_menit": 30,
        "tutup_jam": int(tutup_jam),
        "tutup_menit": 0
    }

    for api_ip in data["api_list"]:
        api_url = f"http://{api_ip}:{PORT}/update-waktu"
        response = requests.post(api_url, json=json_payload)
        print(f"Response from {api_ip}: {response.text}")

    return redirect(url_for("index"))

@app.route("/update-link", methods=["POST"])
def update_link():
    for i, api_ip in enumerate(data["api_list"]):
        api_url = f"http://{api_ip}:{PORT}/update-link"
        link_file = f"link{i + 1}.txt"

        try:
            with open(link_file, "r") as f:
                links = f.read()

            json_payload = {"link": links.replace("\n", "\\n")}
            response = requests.post(api_url, json=json_payload)
            print(f"Response from {api_ip}: {response.text}")
        except FileNotFoundError:
            print(f"File {link_file} tidak ditemukan untuk API {api_ip}. Lewati.")

    return redirect(url_for("index"))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
