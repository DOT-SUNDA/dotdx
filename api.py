from flask import Flask, request, render_template_string, redirect, url_for, session
import requests
import json
import os
import time

app = Flask(__name__)
app.secret_key = 'ganti_ini_dengan_kunci_rahasia'

PORT = 5000
IP_FILE = "ip_list.json"
USERNAME = "admin"
PASSWORD = "admin123"

# ===== IP Management =====
def load_ips():
    if os.path.exists(IP_FILE):
        with open(IP_FILE, "r") as f:
            return json.load(f)
    return []

def save_ips(ip_list):
    with open(IP_FILE, "w") as f:
        json.dump(ip_list, f, indent=4)

ip_list = load_ips()

# ===== HTML TEMPLATE =====
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="id">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
  <title>Control Panel</title>
  <link href="https://cdn.jsdelivr.net/npm/tailwindcss@2.2.19/dist/tailwind.min.css" rel="stylesheet">
  <style>.modal { display: none; }</style>
</head>
<body class="bg-gray-100 font-sans">
  {% if not session.get('logged_in') %}
    <div class="flex items-center justify-center h-screen">
      <form method="POST" action="/login" class="bg-white p-8 rounded shadow-md w-full max-w-sm">
        <h2 class="text-2xl font-bold mb-4 text-center">Login</h2>
        <input type="text" name="username" placeholder="Username" class="w-full mb-3 px-3 py-2 border rounded" required>
        <input type="password" name="password" placeholder="Password" class="w-full mb-4 px-3 py-2 border rounded" required>
        <button class="w-full bg-blue-500 text-white py-2 rounded hover:bg-blue-600" type="submit">Login</button>
      </form>
    </div>
  {% else %}
  <div class="container mx-auto p-6 bg-white rounded-lg shadow-lg mt-6">
    <div class="flex justify-between items-center">
      <h2 class="text-2xl font-bold text-gray-800">Control Panel Multi RDP</h2>
      <form method="POST" action="/logout">
        <button type="submit" class="bg-gray-500 text-white px-3 py-1 rounded hover:bg-gray-600">Logout</button>
      </form>
    </div>

    <div class="mt-4 space-x-2">
      <button id="addIpBtn" class="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600">Tambah IP</button>
      <button id="sendLinkBtn" class="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600">Kirim Link</button>
      <button id="sendWaktuBtn" class="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600">Kirim Waktu</button>
    </div>

    {% if ip_list %}
      <div class="mt-6">
        <h4 class="text-lg font-semibold text-gray-700">Daftar IP:</h4>
        <ul class="list-disc pl-5">
          {% for ip in ip_list %}
            <li class="flex justify-between items-center py-2">
              <span>{{ loop.index }}. {{ ip }}</span>
              <form method="POST" action="/delete_ip" class="inline">
                <input type="hidden" name="ip" value="{{ ip }}">
                <button class="bg-red-500 text-white px-2 py-1 rounded hover:bg-red-600">Hapus</button>
              </form>
            </li>
          {% endfor %}
        </ul>
        <form method="POST" action="/clear_ip" class="mt-4">
          <button class="bg-red-500 text-white px-4 py-2 rounded hover:bg-red-600">Hapus Semua</button>
        </form>
      </div>
    {% endif %}

    {% if results %}
    <div class="mt-6 bg-blue-100 border-l-4 border-blue-500 text-blue-700 p-4 rounded">
      <h4 class="font-bold">Hasil:</h4>
      {% for res in results %}
        <p>{{ res }}</p>
      {% endfor %}
    </div>
    {% endif %}
  </div>

  <!-- Modals: IP, Link, Waktu -->
  <div id="addIpModal" class="modal fixed inset-0 bg-gray-600 bg-opacity-50 flex items-center justify-center">
    <div class="bg-white rounded-lg p-6 w-11/12 md:w-1/3">
      <span class="close cursor-pointer float-right text-gray-500" id="closeAddIpModal">&times;</span>
      <form method="POST" action="/add_ip">
        <label class="block mb-2">IP RDP (satu per baris):</label>
        <textarea name="ips" rows="5" class="w-full border rounded p-2" placeholder="192.168.1.10&#10;192.168.1.11"></textarea>
        <button class="bg-blue-500 text-white px-4 py-2 rounded mt-4 hover:bg-blue-600">Tambah</button>
      </form>
    </div>
  </div>

  <div id="sendLinkModal" class="modal fixed inset-0 bg-gray-600 bg-opacity-50 flex items-center justify-center">
    <div class="bg-white rounded-lg p-6 w-11/12 md:w-1/3">
      <span class="close cursor-pointer float-right text-gray-500" id="closeSendLinkModal">&times;</span>
      <form method="POST" action="/send_link">
        <label class="block mb-2">Link (satu per baris):</label>
        <textarea name="links" rows="5" class="w-full border rounded p-2" placeholder="https://..."></textarea>
        <button class="bg-blue-500 text-white px-4 py-2 rounded mt-4 hover:bg-blue-600">Kirim</button>
      </form>
    </div>
  </div>

  <div id="sendWaktuModal" class="modal fixed inset-0 bg-gray-600 bg-opacity-50 flex items-center justify-center">
    <div class="bg-white rounded-lg p-6 w-11/12 md:w-1/3">
      <span class="close cursor-pointer float-right text-gray-500" id="closeSendWaktuModal">&times;</span>
      <form method="POST" action="/send_waktu">
        <label>Jam Buka:</label>
        <input name="buka_jam" type="number" class="w-full mb-2 border p-2 rounded" min="0" max="23">
        <label>Menit Buka:</label>
        <input name="buka_menit" type="number" class="w-full mb-2 border p-2 rounded" min="0" max="59">
        <label>Jam Tutup:</label>
        <input name="tutup_jam" type="number" class="w-full mb-2 border p-2 rounded" min="0" max="23">
        <label>Menit Tutup:</label>
        <input name="tutup_menit" type="number" class="w-full mb-2 border p-2 rounded" min="0" max="59">
        <button class="bg-blue-500 text-white px-4 py-2 rounded mt-4 hover:bg-blue-600">Kirim</button>
      </form>
    </div>
  </div>

  <script>
    document.getElementById('addIpBtn').onclick = () => document.getElementById('addIpModal').style.display = "flex";
    document.getElementById('sendLinkBtn').onclick = () => document.getElementById('sendLinkModal').style.display = "flex";
    document.getElementById('sendWaktuBtn').onclick = () => document.getElementById('sendWaktuModal').style.display = "flex";
    document.getElementById('closeAddIpModal').onclick = () => document.getElementById('addIpModal').style.display = "none";
    document.getElementById('closeSendLinkModal').onclick = () => document.getElementById('sendLinkModal').style.display = "none";
    document.getElementById('closeSendWaktuModal').onclick = () => document.getElementById('sendWaktuModal').style.display = "none";
    window.onclick = e => { if (e.target.classList.contains('modal')) e.target.style.display = "none"; }
  </script>
  {% endif %}
</body>
</html>
'''

# ===== Routes =====
@app.route('/')
def index():
    results = session.pop('results', [])
    return render_template_string(HTML_TEMPLATE, ip_list=ip_list, results=results)

@app.route('/login', methods=['POST'])
def login():
    if request.form['username'] == USERNAME and request.form['password'] == PASSWORD:
        session['logged_in'] = True
    return redirect(url_for('index'))

@app.route('/logout', methods=['POST'])
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('index'))

@app.route('/add_ip', methods=['POST'])
def add_ip():
    ips = request.form.get('ips', '').strip().splitlines()
    for ip in [i.strip() for i in ips if i.strip()]:
        if ip not in ip_list:
            ip_list.append(ip)
    save_ips(ip_list)
    return redirect(url_for('index'))

@app.route('/delete_ip', methods=['POST'])
def delete_ip():
    ip = request.form['ip']
    if ip in ip_list:
        ip_list.remove(ip)
        save_ips(ip_list)
    return redirect(url_for('index'))

@app.route('/clear_ip', methods=['POST'])
def clear_ip():
    ip_list.clear()
    save_ips(ip_list)
    return redirect(url_for('index'))

@app.route('/send_link', methods=['POST'])
def send_link():
    links = [l.strip() for l in request.form.get('links', '').splitlines() if l.strip()]
    results = []
    ip_links_map = {ip: [] for ip in ip_list}
    for i, link in enumerate(links):
        ip_links_map[ip_list[i % len(ip_list)]].append(link)

    for ip in ip_list:
        time.sleep(0.5)
        try:
            r = requests.post(f"http://{ip}:{PORT}/update-link", json={"link": "\n".join(ip_links_map[ip])}, timeout=5)
            msg = r.json().get("message", r.text)
            results.append(f"{ip} ← {len(ip_links_map[ip])} link → {msg}")
        except Exception as e:
            results.append(f"{ip} ← link → Error: {e}")

    session['results'] = results
    return redirect(url_for('index'))

@app.route('/send_waktu', methods=['POST'])
def send_waktu():
    waktu = {
        "buka_jam": int(request.form.get("buka_jam", 0)),
        "buka_menit": int(request.form.get("buka_menit", 0)),
        "tutup_jam": int(request.form.get("tutup_jam", 0)),
        "tutup_menit": int(request.form.get("tutup_menit", 0)),
    }
    results = []
    for ip in ip_list:
        time.sleep(0.5)
        try:
            r = requests.post(f"http://{ip}:{PORT}/update-waktu", json=waktu, timeout=5)
            msg = r.json().get("message", r.text)
            results.append(f"{ip} ← waktu → {msg}")
        except Exception as e:
            results.append(f"{ip} ← waktu → Error: {e}")
    session['results'] = results
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
