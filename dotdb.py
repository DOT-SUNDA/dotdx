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
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Panel API & Link</title>
  <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
  <style>
    body {
      background-color: #121212;
      color: #ffffff;
      min-height: 100vh;
      padding-top: 2rem;
      padding-bottom: 2rem;
    }
    .modal-content {
      background-color: #1e1e1e;
      color: #ffffff;
      border: none;
    }
    .form-label {
      color: #ffffff;
    }
    .btn-primary {
      background-color: #0d6efd;
      border: none;
    }
    .btn-primary:hover {
      background-color: #0b5ed7;
    }
    textarea.form-control {
      background-color: #2c2c2c;
      color: #ffffff;
      border: 1px solid #444;
      resize: vertical;
    }
  </style>
</head>
<body>
<div class="container">
  <h1 class="mb-4 text-center">Panel API & Link</h1>

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
    <button class="btn btn-primary" data-bs-toggle="modal" data-bs-target="#downloadModal">Unduh & Bagi Link</button>
  </div>

  <div class="card mb-4 p-3">
    <h4>2. Update Waktu</h4>
    <button class="btn btn-primary" data-bs-toggle="modal" data-bs-target="#updateTimeModal">Update Waktu</button>
  </div>

  <div class="card mb-4 p-3">
    <h4>3. Update Link ke Semua API</h4>
    <button class="btn btn-primary" data-bs-toggle="modal" data-bs-target="#updateLinkModal">Update Link</button>
  </div>

  <div class="card mb-4 p-3">
    <h4>4. Tambah / Update API List & Link List (otomatis split)</h4>
    <button class="btn btn-primary" data-bs-toggle="modal" data-bs-target="#addListsModal">Tambah / Update List</button>
  </div>

  <!-- Download Modal -->
  <div class="modal fade" id="downloadModal" tabindex="-1" aria-hidden="true">
    <div class="modal-dialog">
      <div class="modal-content">
        <div class="modal-header">
          <h5 class="modal-title">Unduh & Bagi Link</h5>
          <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
        </div>
        <div class="modal-body">
          <form action="{{ url_for('download_split') }}" method="post">
            <button class="btn btn-primary w-100" type="submit">Unduh & Bagi Link</button>
          </form>
        </div>
      </div>
    </div>
  </div>

  <!-- Update Time Modal -->
  <div class="modal fade" id="updateTimeModal" tabindex="-1" aria-hidden="true">
    <div class="modal-dialog">
      <div class="modal-content">
        <div class="modal-header">
          <h5 class="modal-title">Update Waktu</h5>
          <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
        </div>
        <div class="modal-body">
          <form action="{{ url_for('update_waktu') }}" method="post" class="row g-3 align-items-center">
            <div class="col-12">
              <label for="buka_jam" class="form-label">Jam Buka (0-23)</label>
              <input type="number" min="0" max="23" id="buka_jam" name="buka_jam" class="form-control" required>
            </div>
            <div class="col-12">
              <label for="tutup_jam" class="form-label">Jam Tutup (0-23)</label>
              <input type="number" min="0" max="23" id="tutup_jam" name="tutup_jam" class="form-control" required>
            </div>
            <div class="col-12 pt-3">
              <button type="submit" class="btn btn-primary w-100">Update Waktu</button>
            </div>
          </form>
        </div>
      </div>
    </div>
  </div>

  <!-- Update Link Modal -->
  <div class="modal fade" id="updateLinkModal" tabindex="-1" aria-hidden="true">
    <div class="modal-dialog">
      <div class="modal-content">
        <div class="modal-header">
          <h5 class="modal-title">Update Link ke Semua API</h5>
          <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
        </div>
        <div class="modal-body">
          <form action="{{ url_for('update_link') }}" method="post">
            <button class="btn btn-primary w-100" type="submit">Update Link</button>
          </form>
        </div>
      </div>
    </div>
  </div>

  <!-- Add Lists Modal -->
  <div class="modal fade" id="addListsModal" tabindex="-1" aria-hidden="true">
    <div class="modal-dialog">
      <div class="modal-content">
        <div class="modal-header">
          <h5 class="modal-title">Tambah / Update API List & Link List</h5>
          <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
        </div>
        <div class="modal-body">
          <form action="{{ url_for('add_lists') }}" method="post">
            <div class="mb-3">
              <label for="api_list_text" class="form-label">API List (1 IP/API per baris)</label>
              <textarea id="api_list_text" name="api_list_text" rows="5" class="form-control" placeholder="contoh: 192.168.1.1" required>{{ api_text }}</textarea>
            </div>
            <div class="mb-3">
              <label for="link_list_text" class="form-label">Link List (1 link per baris)</label>
              <textarea id="link_list_text" name="link_list_text" rows="8" class="form-control" placeholder="contoh: http://example.com/link1" required>{{ link_text }}</textarea>
            </div>
            <button type="submit" class="btn btn-primary w-100">Simpan & Split Otomatis</button>
          </form>
        </div>
      </div>
    </div>
  </div>
</div>
<script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
"""

def split_links(apis, links):
    # Hapus file link*.txt lama
    for file in os.listdir():
        if file.startswith('link') and file.endswith('.txt'):
            os.remove(file)
    # Bagi link ke file baru sesuai jumlah API
    for i, link in enumerate(links):
        idx = i % len(apis)
        with open(f'link{idx+1}.txt', 'a') as f:
            f.write(link + '\n')

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
    # Load text area default content:
    api_text = "\n".join(api_list)
    link_text = ""
    if os.path.exists('link_list.txt'):
        with open('link_list.txt') as f:
            link_text = f.read()
    return render_template_string(TEMPLATE, api_list=api_list, links=links, api_text=api_text, link_text=link_text)

@app.route('/download_split', methods=['POST'])
def download_split():
    try:
        subprocess.run(['curl', '-s', '-o', 'api_list.txt', API_LIST_URL], check=True)
        subprocess.run(['curl', '-s', '-o', 'link_list.txt', LINK_LIST_URL], check=True)
        with open('api_list.txt') as f:
            apis = [line.strip() for line in f if line.strip()]
        with open('link_list.txt') as f:
            links = [line.strip() for line in f if line.strip()]
        split_links(apis, links)
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

@app.route('/add_lists', methods=['POST'])
def add_lists():
    api_list_text = request.form.get('api_list_text')
    link_list_text = request.form.get('link_list_text')

    if not (api_list_text and link_list_text):
        flash("Kedua field harus diisi!", "warning")
        return redirect(url_for('index'))

    api_lines = [line.strip() for line in api_list_text.strip().splitlines() if line.strip()]
    link_lines = [line.strip() for line in link_list_text.strip().splitlines() if line.strip()]

    if not api_lines:
        flash("API list kosong!", "warning")
        return redirect(url_for('index'))
    if not link_lines:
        flash("Link list kosong!", "warning")
        return redirect(url_for('index'))

    # Simpan file
    with open('api_list.txt', 'w') as f:
        f.write('\n'.join(api_lines) + '\n')

    with open('link_list.txt', 'w') as f:
        f.write('\n'.join(link_lines) + '\n')

    # Split link otomatis
    split_links(api_lines, link_lines)
    flash("Berhasil simpan API dan Link serta membagi link secara otomatis.", "success")
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
