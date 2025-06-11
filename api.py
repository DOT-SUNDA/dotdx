from flask import Flask, request, render_template_string, redirect, url_for, session
import requests
import json
import os
import time
from functools import wraps

app = Flask(__name__)
app.secret_key = 'rahasia-super-aman'

PORT = 5000
IP_FILE = "ip_list.json"
USERNAME = "admin"
PASSWORD = "admin123"

def load_ips():
    if os.path.exists(IP_FILE):
        with open(IP_FILE, "r") as f:
            return json.load(f)
    return []

def save_ips(ip_list):
    with open(IP_FILE, "w") as f:
        json.dump(ip_list, f, indent=4)

ip_list = load_ips()

LOGIN_TEMPLATE = '''
<!DOCTYPE html>
<html lang="id">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Login</title>
  <link href="https://cdn.jsdelivr.net/npm/tailwindcss@2.2.19/dist/tailwind.min.css" rel="stylesheet" />
</head>
<body class="bg-gray-900 text-white flex items-center justify-center h-screen font-mono">
  <form method="POST" action="/login" class="bg-gray-800 p-8 rounded-xl shadow-2xl w-full max-w-sm border border-gray-700">
    <h2 class="text-2xl font-bold mb-6 text-center text-green-400">🔐 Panel Login</h2>
    {% if error %}
      <p class="text-red-500 mb-4">{{ error }}</p>
    {% endif %}
    <label class="block mb-1">Username:</label>
    <input name="username" class="bg-gray-700 text-white border border-gray-600 w-full p-2 rounded mb-4" required />
    <label class="block mb-1">Password:</label>
    <input name="password" type="password" class="bg-gray-700 text-white border border-gray-600 w-full p-2 rounded mb-4" required />
    <button type="submit" class="w-full bg-green-600 hover:bg-green-700 text-white p-2 rounded">Login</button>
  </form>
</body>
</html>
'''

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="id">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Control Panel</title>
  <link href="https://cdn.jsdelivr.net/npm/tailwindcss@2.2.19/dist/tailwind.min.css" rel="stylesheet" />
</head>
<body class="bg-gray-900 text-gray-200 font-mono min-h-screen">
  <div class="max-w-5xl mx-auto p-6">
    <div class="flex justify-between items-center mb-6">
      <h2 class="text-3xl font-bold text-green-400">🖥️ Multi-RDP Control</h2>
      <form action="/logout" method="POST">
        <button class="text-sm text-red-400 hover:text-red-300">Logout</button>
      </form>
    </div>

    <form method="POST" action="/add_ip" class="mb-4">
      <label class="block font-semibold mb-1 text-blue-300">Tambah IP (satu per baris):</label>
      <textarea name="ips" class="w-full bg-gray-800 border border-gray-700 p-2 rounded text-white mb-2" rows="3"></textarea>
      <button class="bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded">Tambah</button>
    </form>

    <h3 class="text-xl font-bold mb-2 text-blue-400">Daftar IP:</h3>
    <ul class="list-disc list-inside mb-6">
      {% for ip in ip_list %}
        <li>{{ ip }}
          <form method="POST" action="/delete_ip" class="inline">
            <input type="hidden" name="ip" value="{{ ip }}">
            <button class="text-red-400 text-sm ml-2 hover:text-red-300">Hapus</button>
          </form>
        </li>
      {% endfor %}
    </ul>
    <form method="POST" action="/clear_ip" class="mb-6">
      <button class="bg-yellow-600 hover:bg-yellow-700 text-white px-4 py-2 rounded">Hapus Semua</button>
    </form>

    <form method="POST" action="/send_link" class="mb-6">
      <label class="block font-semibold mb-1 text-blue-300">Link per baris:</label>
      <textarea name="links" class="w-full bg-gray-800 border border-gray-700 p-2 rounded text-white mb-2" rows="4"></textarea>
      <button class="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded">Kirim Link</button>
    </form>

    <form method="POST" action="/send_waktu">
      <label class="block font-semibold mb-1 text-blue-300">Waktu Operasi (Jam & Menit):</label>
      <div class="flex flex-wrap gap-2 mb-2">
        <input name="buka_jam" placeholder="Buka Jam" class="bg-gray-800 border border-gray-700 p-2 rounded w-24 text-white">
        <input name="buka_menit" placeholder="Buka Menit" class="bg-gray-800 border border-gray-700 p-2 rounded w-24 text-white">
        <input name="tutup_jam" placeholder="Tutup Jam" class="bg-gray-800 border border-gray-700 p-2 rounded w-24 text-white">
        <input name="tutup_menit" placeholder="Tutup Menit" class="bg-gray-800 border border-gray-700 p-2 rounded w-24 text-white">
      </div>
      <button class="bg-indigo-600 hover:bg-indigo-700 text-white px-4 py-2 rounded">Kirim Waktu</button>
    </form>

    {% if results %}
    <div id="toast-container" class="fixed bottom-5 right-5 space-y-2 z-50">
      {% for res in results %}
      <div class="bg-gray-800 border border-gray-700 rounded-lg shadow-lg px-4 py-3 text-sm text-green-300 animate-slide-in">
        {{ res }}
      </div>
      {% endfor %}
    </div>
    <script>
      setTimeout(() => {
        const container = document.getElementById('toast-container');
        if (container) container.remove();
      }, 6000);
    </script>
    <style>
      @keyframes slideIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
      }
      .animate-slide-in {
        animation: slideIn 0.4s ease-out;
      }
    </style>
    {% endif %}
  </div>
</body>
</html>
'''

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get("logged_in"):
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if request.form['username'] == USERNAME and request.form['password'] == PASSWORD:
            session['logged_in'] = True
            return redirect(url_for('index'))
        return render_template_string(LOGIN_TEMPLATE, error="Login gagal.")
    return render_template_string(LOGIN_TEMPLATE)

@app.route('/logout', methods=['POST'])
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/')
@login_required
def index():
    results = session.pop('results', [])
    return render_template_string(HTML_TEMPLATE, ip_list=ip_list, results=results)

@app.route('/add_ip', methods=['POST'])
@login_required
def add_ip():
    ips = request.form.get('ips', '').strip().splitlines()
    ips = [ip.strip() for ip in ips if ip.strip()]
    for ip in ips:
        if ip and ip not in ip_list:
            ip_list.append(ip)
    save_ips(ip_list)
    return redirect(url_for('index'))

@app.route('/delete_ip', methods=['POST'])
@login_required
def delete_ip():
    ip = request.form.get('ip')
    if ip in ip_list:
        ip_list.remove(ip)
        save_ips(ip_list)
    return redirect(url_for('index'))

@app.route('/clear_ip', methods=['POST'])
@login_required
def clear_ip():
    ip_list.clear()
    save_ips(ip_list)
    return redirect(url_for('index'))

@app.route('/send_link', methods=['POST'])
@login_required
def send_link():
    links = request.form.get('links', '').strip().splitlines()
    links = [l.strip() for l in links if l.strip()]
    results = []

    if not ip_list:
        results.append("❌ Tidak ada IP yang ditambahkan.")
        return render_template_string(HTML_TEMPLATE, ip_list=ip_list, results=results)

    ip_links_map = {ip: [] for ip in ip_list}
    for i, link in enumerate(links):
        target_ip = ip_list[i % len(ip_list)]
        ip_links_map[target_ip].append(link)

    for ip in ip_list:
        combined_links = "\n".join(ip_links_map[ip])
        url = f"http://{ip}:{PORT}/update-link"
        try:
            r = requests.post(url, json={"link": combined_links}, timeout=5)
            msg = r.json().get("message", r.text)
            results.append(f"{ip} ← {len(ip_links_map[ip])} link → {msg}")
        except Exception as e:
            results.append(f"{ip} ← link → Error: {str(e)}")
        time.sleep(0.5)

    session['results'] = results
    return redirect(url_for('index'))

@app.route('/send_waktu', methods=['POST'])
@login_required
def send_waktu():
    waktu = {
        "buka_jam": int(request.form.get('buka_jam', 0)),
        "buka_menit": int(request.form.get('buka_menit', 0)),
        "tutup_jam": int(request.form.get('tutup_jam', 0)),
        "tutup_menit": int(request.form.get('tutup_menit', 0)),
    }

    results = []
    for ip in ip_list:
        url = f"http://{ip}:{PORT}/update-waktu"
        try:
            r = requests.post(url, json=waktu, timeout=5)
            msg = r.json().get("message", r.text)
            results.append(f"{ip} ← waktu → {msg}")
        except Exception as e:
            results.append(f"{ip} ← waktu → Error: {str(e)}")
        time.sleep(0.5)

    session['results'] = results
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
