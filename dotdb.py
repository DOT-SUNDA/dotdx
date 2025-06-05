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
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
</head>
<body>
<nav class="navbar navbar-expand-lg navbar-dark bg-dark">
    <div class="container-fluid">
        <a class="navbar-brand" href="#">Manajemen API & Link</a>
        <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav">
            <span class="navbar-toggler-icon"></span>
        </button>
        <div class="collapse navbar-collapse" id="navbarNav">
            <ul class="navbar-nav">
                <li class="nav-item"><a class="nav-link active" href="#add-api">Tambah API</a></li>
                <li class="nav-item"><a class="nav-link" href="#add-link">Tambah Link</a></li>
                <li class="nav-item"><a class="nav-link" href="#split-links">Bagi Link</a></li>
            </ul>
        </div>
    </div>
</nav>
<div class="container mt-4">
    <div class="card mb-4" id="add-api">
        <div class="card-header bg-primary text-white">Tambahkan API</div>
        <div class="card-body">
            <form action="/add-api" method="post">
                <div class="mb-3">
                    <label for="apiTextarea" class="form-label">Tambahkan API (satu API per baris)</label>
                    <textarea name="apis" class="form-control" id="apiTextarea" rows="5" placeholder="192.168.1.1\n192.168.1.2"></textarea>
                </div>
                <button class="btn btn-primary" type="submit">Tambah API</button>
            </form>
        </div>
    </div>

    <div class="card mb-4" id="add-link">
        <div class="card-header bg-success text-white">Tambahkan Link</div>
        <div class="card-body">
            <form action="/add-link" method="post">
                <div class="mb-3">
                    <label for="linkTextarea" class="form-label">Tambahkan Link (satu link per baris)</label>
                    <textarea name="links" class="form-control" id="linkTextarea" rows="5" placeholder="https://example.com\nhttps://another.com"></textarea>
                </div>
                <button class="btn btn-success" type="submit">Tambah Link</button>
            </form>
        </div>
    </div>

    <div class="card mb-4" id="split-links">
        <div class="card-header bg-warning text-dark">Bagi Link ke API</div>
        <div class="card-body">
            <form action="/split-links" method="post">
                <button class="btn btn-warning" type="submit">Bagi Link</button>
            </form>
        </div>
    </div>

    <div class="row">
        <div class="col-md-6">
            <div class="card mb-4">
                <div class="card-header bg-info text-white">Daftar API</div>
                <ul class="list-group list-group-flush">
                    {% for api in api_list %}
                    <li class="list-group-item d-flex justify-content-between align-items-center">
                        {{ api }}
                        <a href="/delete-api/{{ loop.index0 }}" class="btn btn-danger btn-sm"><i class="fas fa-trash-alt"></i></a>
                    </li>
                    {% endfor %}
                </ul>
            </div>
        </div>
        <div class="col-md-6">
            <div class="card mb-4">
                <div class="card-header bg-secondary text-white">Daftar Link</div>
                <ul class="list-group list-group-flush">
                    {% for link in link_list %}
                    <li class="list-group-item d-flex justify-content-between align-items-center">
                        {{ link }}
                        <a href="/delete-link/{{ loop.index0 }}" class="btn btn-danger btn-sm"><i class="fas fa-trash-alt"></i></a>
                    </li>
                    {% endfor %}
                </ul>
            </div>
        </div>
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

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
