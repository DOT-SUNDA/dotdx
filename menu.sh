from flask import Flask, render_template_string, request, redirect, url_for, flash
import os
import subprocess
import requests

app = Flask(__name__)
app.secret_key = 'secret-key-flask-panel'  # Ganti kalau mau

API_LIST_URL = "https://dot-store.biz.id/api_list.txt"
LINK_LIST_URL = "https://dot-store.biz.id/link_list.txt"
PORT = 5000

# Template HTML satu file, menggunakan Bootstrap 5 Dark
TEMPLATE = """
<!DOCTYPE html>
<html lang="en" >
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Panel API & Link</title>
  <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet" />
  <style>
    body {
      background-color: #121212;
      color: #eee;
      min-height: 100vh;
      padding-top: 2rem;
      padding-bottom: 2rem;
    }
    .container {
      max-width: 900px;
    }
    .form-label {
      color: #ddd;
    }
    .card {
      background-color: #1e1e1e;
      border: none;
    }
    .btn-primary {
      background-color: #0d6efd;
      border: none;
    }
    .btn-primary:hover {
      background-color: #0b5ed7;
    }
    pre {
      background-color: #2c2c2c;
      padding: 1rem;
      border-radius: 0.3rem;
      overflow-x: auto;
      color: #ddd;
    }
  </style>
</head>
<body>
<div class="container">
  <h1 class="mb-4 text-center">Panel API & Link (Dark Mode)</h1>

  {% with messages = get_flashed_messages(with_categories=true) %}
    {% if messages %}
      {% for category, message in messages %}
        <div class="alert alert-{{ category }} alert-dismissible fade show" role="alert">
          {{ message }}
          <button type="button" class="btn-close btn-close-white" data-bs-dismiss="alert" aria-label="Close"></button>
        </div>
      {% endfor %}
    {% endif %}
  {% endwith %}

  <div class="card mb-4 p-3">
    <h4>1. Unduh Daftar API & Link dan Bagi Link Otomatis</h4>
    <form action="{{ url_for('download_split') }}" method="post">
      <button class="btn btn-primary" type="submit">Unduh & Bagi Link</button>
    </form>
  </div>

  <div class="card mb-4 p-3">
    <h4>2. Update Waktu</h4>
    <form action="{{ url_for('update_waktu') }}" method="post" class="row g-3 align-items-center">
      <div class="col-auto">
        <label for="buka_jam" class="form-label">Jam Buka (0-23)</label>
        <input type="number" min="0" max="23" id="buka_jam" name="buka_jam" class="form-control" required />
      </div>
      <div class="col-auto">
        <label for="tutup_jam" class="form-label">Jam Tutup (0-23)</label>
        <input type="number" min="0" max="23" id="tutup_jam" name="tutup_jam" class="form-control" required />
      </div>
      <div class="col-auto pt-4">
        <button type="submit" class="btn btn-primary">Update Waktu</button>
      </div>
    </form>
  </div>

  <div class="card mb-4 p-3">
    <h4>3. Update Link ke Semua API</h4>
    <form action="{{ url_for('update_link') }}" method="post">
      <button class="btn btn-primary" type="submit">Update Link</button>
    </form>
  </div>

  <div class="card mb-4 p-3">
    <h4>Daftar API</h4>
    {% if api_list %}
      <pre>{{ api_list|join('\\n') }}</pre>
    {% else %}
      <p>Tidak ada data API.</p>
    {% endif %}
  </div>

  <div class="card mb-4 p-3">
    <h4>Daftar Link Terbagi</h4>
    {% if links %}
      {% for filename, linkgroup in links.items() %}
        <strong>{{ filename }}</strong>
        <pre>{{ linkgroup|join('\\n') }}</pre>
      {% endfor %}
    {% else %}
      <p>Tidak ada link terbagi.</p>
    {% endif %}
  </div>
</div>

<script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
"""

@app.route('/')
def index():
    api_list = []
    if os.path.exists('api_list.txt'):
        with open('api_list.txt') as f:
            api_list = [line.strip() for line in f if line.strip()]
    link_files = [f for f in os.listdir() if f.startswith('link') and f.endswith('.txt')]
    links = {}
    for lf in link_files:
        with open(lf) as f:
            links[lf] = [line.strip() for line in f if line.strip()]
    return render_template_string(TEMPLATE, api_list=api_list, links=links)

@app.route('/download_split', methods=['POST'])
def download_split():
    try:
        subprocess.run(['curl', '-s', '-o', 'api_list.txt', API_LIST_URL], check=True)
        subprocess.run(['curl', '-s', '-o', 'link_list.txt', LINK_LIST_URL], check=True)
        # Baca isi
        with open('api_list.txt') as f:
            apis = [line.strip() for line in f if line.strip()]
        with open('link_list.txt') as f:
            links = [line.strip() for line in f if line.strip()]
        # Hapus file link*.txt lama
        for file in os.listdir():
            if file.startswith('link') and file.endswith('.txt'):
                os.remove(file)
        # Bagi link ke file baru sesuai jumlah API
        for i, link in enumerate(links):
            idx = i % len(apis)
            with open(f'link{idx+1}.txt', 'a') as f:
                f.write(link + '\n')
        flash("Berhasil unduh dan bagi link.", "success")
    except Exception as e:
        flash(f"Gagal unduh dan bagi link: {e}", "danger")
    return redirect(url_for('index'))

@app.route('/update_waktu', methods=['POST'])
def update_waktu():
    tutup_jam = request.form.get('tutup_jam')
    buka_jam = request.form.get('buka_jam')
    if not (tutup_jam and buka_jam):
        flash("Jam buka dan tutup harus diisi", "warning")
        return redirect(url_for('index'))
    try:
        buka_jam_int = int(buka_jam)
        tutup_jam_int = int(tutup_jam)
        if not (0 <= buka_jam_int <= 23 and 0 <= tutup_jam_int <= 23):
            flash("Jam harus antara 0 sampai 23", "warning")
            return redirect(url_for('index'))
    except ValueError:
        flash("Input jam harus angka", "warning")
        return redirect(url_for('index'))

    if not os.path.exists('api_list.txt'):
        flash("File api_list.txt tidak ditemukan. Unduh daftar API terlebih dahulu.", "warning")
        return redirect(url_for('index'))

    with open('api_list.txt') as f:
        apis = [line.strip() for line in f if line.strip()]

    json_payload = {
        "buka_jam": buka_jam_int,
        "buka_menit": 30,
        "tutup_jam": tutup_jam_int,
        "tutup_menit": 0
    }

    success = []
    failed = []
    for api_ip in apis:
        url = f"http://{api_ip}:{PORT}/update-waktu"
        try:
            r = requests.post(url, json=json_payload, timeout=5)
            if r.status_code == 200:
                success.append(api_ip)
            else:
                failed.append(api_ip)
        except Exception:
            failed.append(api_ip)
    flash(f"Update waktu selesai. Berhasil: {len(success)}, Gagal: {len(failed)}", "info")
    return redirect(url_for('index'))

@app.route('/update_link', methods=['POST'])
def update_link():
    if not os.path.exists('api_list.txt'):
        flash("File api_list.txt tidak ditemukan. Unduh daftar API terlebih dahulu.", "warning")
        return redirect(url_for('index'))

    with open('api_list.txt') as f:
        apis = [line.strip() for line in f if line.strip()]

    success = []
    failed = []
    for i, api_ip in enumerate(apis):
        url = f"http://{api_ip}:{PORT}/update-link"
        link_file = f"link{i+1}.txt"
        if not os.path.exists(link_file):
            # Tidak ada link untuk API ini, skip
            continue
        with open(link_file) as f:
            links_text = f.read()
        json_payload = {
            "link": links_text.replace('\n', '\\n')
        }
        try:
            r = requests.post(url, json=json_payload, timeout=5)
            if r.status_code == 200:
                success.append(api_ip)
            else:
                failed.append(api_ip)
        except Exception:
            failed.append(api_ip)
    flash(f"Update link selesai. Berhasil: {len(success)}, Gagal: {len(failed)}", "info")
    return redirect(url_for('index'))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
