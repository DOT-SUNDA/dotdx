from flask import Flask, request, render_template_string, redirect, url_for
import requests
import json
import os

app = Flask(__name__)

# ====== Konfigurasi ======
PORT = 5000
IP_FILE = "ip_list.json"

# ====== Load IP ======
def load_ips():
    if os.path.exists(IP_FILE):
        with open(IP_FILE, "r") as f:
            return json.load(f)
    return []

def save_ips(ip_list):
    with open(IP_FILE, "w") as f:
        json.dump(ip_list, f, indent=4)

ip_list = load_ips()

# ====== HTML ======
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="id">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Control Panel Multi RDP</title>
    <link href="https://cdn.jsdelivr.net/npm/tailwindcss@2.2.19/dist/tailwind.min.css" rel="stylesheet">
    <style>
        .modal { display: none; }
    </style>
</head>
<body class="bg-gray-100 font-sans">
<div class="container mx-auto p-6 bg-white rounded-lg shadow-lg">
    <h2 class="text-2xl font-bold text-gray-800">Control Panel Multi RDP</h2>
    
    <div class="mt-4">
        <button id="addIpBtn" class="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600">Tambah IP RDP</button>
        <button id="sendLinkBtn" class="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600">Kirim Link</button>
        <button id="sendWaktuBtn" class="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600">Kirim Waktu</button>
    </div>

    {% if ip_list %}
    <div class="mt-6">
        <h4 class="text-lg font-semibold text-gray-700">Daftar IP Aktif:</h4>
        <ul class="list-disc pl-5">
            {% for ip in ip_list %}
                <li class="flex justify-between items-center py-2">
                    <span class="text-gray-600">{{ loop.index }}. {{ ip }}</span>
                    <form method="POST" action="/delete_ip" class="inline">
                        <input type="hidden" name="ip" value="{{ ip }}">
                        <button type="submit" class="bg-red-500 text-white px-2 py-1 rounded hover:bg-red-600">Hapus</button>
                    </form>
                </li>
            {% endfor %}
        </ul>
        <form method="POST" action="/clear_ip" class="mt-4">
            <button type="submit" class="bg-red-500 text-white px-4 py-2 rounded hover:bg-red-600">Hapus Semua</button>
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

<!-- Modal untuk Tambah IP -->
<div id="addIpModal" class="modal fixed inset-0 bg-gray-600 bg-opacity-50 flex items-center justify-center">
    <div class="bg-white rounded-lg p-6 w-11/12 md:w-1/3">
        <span class="close cursor-pointer text-gray-500 float-right" id="closeAddIpModal">&times;</span>
        <h4 class="text-lg font-semibold">Tambah IP RDP</h4>
        <form method="POST" action="/add_ip">
            <label class="block mt-4">IP RDP (satu per baris):</label>
            <textarea name="ips" rows="5" class="border border-gray-300 rounded w-full p-2 mt-1" placeholder="192.168.1.10&#10;192.168.1.11"></textarea>
            <button type="submit" class="bg-blue-500 text-white px-4 py-2 rounded mt-4 hover:bg-blue-600">Tambah</button>
        </form>
    </div>
</div>

<!-- Modal untuk Kirim Link -->
<div id="sendLinkModal" class="modal fixed inset-0 bg-gray-600 bg-opacity-50 flex items-center justify-center">
    <div class="bg-white rounded-lg p-6 w-11/12 md:w-1/3">
        <span class="close cursor-pointer text-gray-500 float-right" id="closeSendLinkModal">&times;</span>
        <h4 class="text-lg font-semibold">Kirim Link</h4>
        <form method="POST" action="/send_link">
            <label class="block mt-4">Link (satu per baris):</label>
            <textarea name="links" rows="5" class="border border-gray-300 rounded w-full p-2 mt-1" placeholder="https://example.com/page1&#10;https://example.com/page2"></textarea>
            <button type="submit" class="bg-blue-500 text-white px-4 py-2 rounded mt-4 hover:bg-blue-600">Kirim Link ke IP</button>
        </form>
    </div>
</div>

<!-- Modal untuk Kirim Waktu -->
<div id="sendWaktuModal" class="modal fixed inset-0 bg-gray-600 bg-opacity-50 flex items-center justify-center">
    <div class="bg-white rounded-lg p-6 w-11/12 md:w-1/3">
        <span class="close cursor-pointer text-gray-500 float-right" id="closeSendWaktuModal">&times;</span>
        <h4 class="text-lg font-semibold">Kirim Waktu</h4>
        <form method="POST" action="/send_waktu">
            <label class="block mt-4">Jam Buka:</label>
            <input name="buka_jam" type="number" class="border border-gray-300 rounded w-full p-2 mt-1" placeholder="Jam Buka" min="0" max="23">
            <label class="block mt-4">Menit Buka:</label>
            <input name="buka_menit" type="number" class="border border-gray-300 rounded w-full p-2 mt-1" placeholder="Menit Buka" min="0" max="59">
            <label class="block mt-4">Jam Tutup:</label>
            <input name="tutup_jam" type="number" class="border border-gray-300 rounded w-full p-2 mt-1" placeholder="Jam Tutup" min="0" max="23">
            <label class="block mt-4">Menit Tutup:</label>
            <input name="tutup_menit" type="number" class="border border-gray-300 rounded w-full p-2 mt-1" placeholder="Menit Tutup" min="0" max="59">
            <button type="submit" class="bg-blue-500 text-white px-4 py-2 rounded mt-4 hover:bg-blue-600">Kirim Waktu ke Semua IP</button>
        </form>
    </div>
</div>

<script>
    // Menampilkan modal
    document.getElementById('addIpBtn').onclick = function() {
        document.getElementById('addIpModal').style.display = "flex";
    }
    document.getElementById('sendLinkBtn').onclick = function() {
        document.getElementById('sendLinkModal').style.display = "flex";
    }
    document.getElementById('sendWaktuBtn').onclick = function() {
        document.getElementById('sendWaktuModal').style.display = "flex";
    }

    // Menutup modal
    document.getElementById('closeAddIpModal').onclick = function() {
        document.getElementById('addIpModal').style.display = "none";
    }
    document.getElementById('closeSendLinkModal').onclick = function() {
        document.getElementById('sendLinkModal').style.display = "none";
    }
    document.getElementById('closeSendWaktuModal').onclick = function() {
        document.getElementById('sendWaktuModal').style.display = "none";
    }

    // Menutup modal jika klik di luar modal
    window.onclick = function(event) {
        if (event.target.className.includes('modal')) {
            event.target.style.display = "none";
        }
    }
</script>
</body>
</html>
'''

# ====== ROUTES ======

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE, ip_list=ip_list, results=[])

@app.route('/add_ip', methods=['POST'])
def add_ip():
    ips = request.form.get('ips', '').strip().splitlines()
    ips = [ip.strip() for ip in ips if ip.strip()]
    for ip in ips:
        if ip and ip not in ip_list:
            ip_list.append(ip)
    save_ips(ip_list)
    return redirect(url_for('index'))

@app.route('/delete_ip', methods=['POST'])
def delete_ip():
    ip = request.form.get('ip')
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
    links = request.form.get('links', '').strip().splitlines()
    links = [l.strip() for l in links if l.strip()]
    results = []

    if not ip_list:
        results.append("❌ Tidak ada IP yang ditambahkan.")
        return render_template_string(HTML_TEMPLATE, ip_list=ip_list, results=results)

    # Buat map IP ke link-list (dengan pembagian merata perbaris)
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

    return render_template_string(HTML_TEMPLATE, ip_list=ip_list, results=results)

@app.route('/send_waktu', methods=['POST'])
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

    return render_template_string(HTML_TEMPLATE, ip_list=ip_list, results=results)

# ====== Run Server ======
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
