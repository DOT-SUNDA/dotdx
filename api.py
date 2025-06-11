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
<html lang="id"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Login</title><link href="https://cdn.jsdelivr.net/npm/tailwindcss@2.2.19/dist/tailwind.min.css" rel="stylesheet"></head>
<body class="bg-gray-100 flex items-center justify-center h-screen">
    <form method="POST" action="/login" class="bg-white p-8 rounded-lg shadow-lg w-full max-w-sm">
        <h2 class="text-2xl font-bold mb-6 text-center">Login Panel</h2>
        {% if error %}<p class="text-red-500">{{ error }}</p>{% endif %}
        <label>Username:</label>
        <input name="username" class="border w-full p-2 rounded mb-4" required>
        <label>Password:</label>
        <input name="password" type="password" class="border w-full p-2 rounded mb-4" required>
        <button type="submit" class="w-full bg-blue-500 text-white p-2 rounded hover:bg-blue-600">Login</button>
    </form>
</body></html>
'''

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="id">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Control Panel</title>
    <link href="https://cdn.jsdelivr.net/npm/tailwindcss@2.2.19/dist/tailwind.min.css" rel="stylesheet">
</head>
<body class="bg-gray-100 text-gray-800">
    <div class="max-w-4xl mx-auto p-4">
        <div class="flex justify-between items-center">
            <h2 class="text-2xl font-bold text-gray-800">Control Panel Multi RDP</h2>
            <form action="/logout" method="POST">
                <button class="text-sm text-red-500 hover:underline">Logout</button>
            </form>
        </div>

        <form method="POST" action="/add_ip" class="mt-6">
            <label class="block font-bold">Tambah IP (satu per baris):</label>
            <textarea name="ips" class="w-full border p-2 rounded mt-1"></textarea>
            <button class="mt-2 bg-green-500 text-white px-4 py-2 rounded">Tambah</button>
        </form>

        <form method="POST" action="/clear_ip" class="mt-2">
            <button class="bg-yellow-500 text-white px-4 py-2 rounded">Bersihkan Semua IP</button>
        </form>

        <h3 class="mt-6 font-bold">Daftar IP:</h3>
        <ul class="list-disc list-inside">
            {% for ip in ip_list %}
                <li>{{ ip }}
                    <form method="POST" action="/delete_ip" style="display:inline">
                        <input type="hidden" name="ip" value="{{ ip }}">
                        <button class="text-red-500 text-sm ml-2">Hapus</button>
                    </form>
                </li>
            {% endfor %}
        </ul>

        <form method="POST" action="/send_link" class="mt-6">
            <label class="block font-bold">Link per baris:</label>
            <textarea name="links" class="w-full border p-2 rounded mt-1"></textarea>
            <button class="mt-2 bg-blue-500 text-white px-4 py-2 rounded">Kirim Link</button>
        </form>

        <form method="POST" action="/send_waktu" class="mt-6">
            <label class="block font-bold">Waktu Operasi (Jam & Menit):</label>
            <div class="flex space-x-2 mt-1">
                <input name="buka_jam" placeholder="Buka Jam" class="border p-2 rounded w-1/4">
                <input name="buka_menit" placeholder="Buka Menit" class="border p-2 rounded w-1/4">
                <input name="tutup_jam" placeholder="Tutup Jam" class="border p-2 rounded w-1/4">
                <input name="tutup_menit" placeholder="Tutup Menit" class="border p-2 rounded w-1/4">
            </div>
            <button class="mt-2 bg-indigo-500 text-white px-4 py-2 rounded">Kirim Waktu</button>
        </form>

        {% if results %}
        <div class="mt-6">
            <h3 class="font-bold">Hasil:</h3>
            <ul class="list-disc list-inside">
                {% for res in results %}<li>{{ res }}</li>{% endfor %}
            </ul>
        </div>
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
    return render_template_string(HTML_TEMPLATE, ip_list=ip_list, results=[])

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

    return render_template_string(HTML_TEMPLATE, ip_list=ip_list, results=results)

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

    return render_template_string(HTML_TEMPLATE, ip_list=ip_list, results=results)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
