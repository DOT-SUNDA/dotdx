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
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.4/css/all.min.css">
    <style>
        body { font-family: 'Arial', sans-serif; background: #f2f2f2; padding: 30px; }
        .container { background: white; padding: 20px; border-radius: 8px; max-width: 700px; margin: auto; box-shadow: 0 0 10px rgba(0,0,0,0.1); }
        button { background-color: #007bff; color: white; border: none; cursor: pointer; padding: 10px; border-radius: 4px; }
        button:hover { background-color: #0056b3; }
        .ip-list { margin-top: 20px; }
        .ip-item { display: flex; justify-content: space-between; padding: 5px 0; }
        .results { background: #e8f0ff; padding: 10px; border-radius: 5px; margin-top: 20px; white-space: pre-wrap; }
        h2, h4 { color: #333; }
        label { font-weight: bold; }
        .modal { display: none; position: fixed; z-index: 1; left: 0; top: 0; width: 100%; height: 100%; overflow: auto; background-color: rgb(0,0,0); background-color: rgba(0,0,0,0.4); padding-top: 60px; }
        .modal-content { background-color: #fefefe; margin: 5% auto; padding: 20px; border: 1px solid #888; width: 80%; border-radius: 8px; }
        .close { color: #aaa; float: right; font-size: 28px; font-weight: bold; }
        .close:hover, .close:focus { color: black; text-decoration: none; cursor: pointer; }
    </style>
</head>
<body>
<div class="container">
    <h2>Control Panel Multi RDP</h2>
    
    <button id="addIpBtn">Tambah IP RDP</button>
    <button id="sendLinkBtn">Kirim Link</button>
    <button id="sendWaktuBtn">Kirim Waktu</button>

    {% if ip_list %}
    <div class="ip-list">
        <h4>Daftar IP Aktif:</h4>
        {% for ip in ip_list %}
            <div class="ip-item">
                <span>{{ loop.index }}. {{ ip }}</span>
                <form method="POST" action="/delete_ip" style="display:inline;">
                    <input type="hidden" name="ip" value="{{ ip }}">
                    <button type="submit">Hapus</button>
                </form>
            </div>
        {% endfor %}
        <form method="POST" action="/clear_ip">
            <button type="submit" style="margin-top:10px;">Hapus Semua</button>
        </form>
    </div>
    {% endif %}

    {% if results %}
    <div class="results">
        {% for res in results %}
            {{ res }}<br>
        {% endfor %}
    </div>
    {% endif %}
</div>

<!-- Modal untuk Tambah IP -->
<div id="addIpModal" class="modal">
    <div class="modal-content">
        <span class="close" id="closeAddIpModal">&times;</span>
        <h4>Tambah IP RDP</h4>
        <form method="POST" action="/add_ip">
            <label>IP RDP (tanpa http:// dan port):</label>
            <input name="ip" placeholder="192.168.1.10" required>
            <button type="submit">Tambah</button>
        </form>
    </div>
</div>

<!-- Modal untuk Kirim Link -->
<div id="sendLinkModal" class="modal">
    <div class="modal-content">
        <span class="close" id="closeSendLinkModal">&times;</span>
        <h4>Kirim Link</h4>
        <form method="POST" action="/send_link">
            <label>Link (satu per baris):</label>
            <textarea name="links" rows="5" placeholder="https://example.com/page1\nhttps://example.com/page2"></textarea>
            <button type="submit">Kirim Link ke IP</button>
        </form>
    </div>
</div>

<!-- Modal untuk Kirim Waktu -->
<div id="sendWaktuModal" class="modal">
    <div class="modal-content">
        <span class="close" id="closeSendWaktuModal">&times;</span>
        <h4>Kirim Waktu</h4>
        <form method="POST" action="/send_waktu">
            <label>Jam Buka:</label>
            <input name="buka_jam" type="number" placeholder="Jam Buka" min="0" max="23">
            <label>Menit Buka:</label>
            <input name="buka_menit" type="number" placeholder="Menit Buka" min="0" max="59">
            <label>Jam Tutup:</label>
            <input name="tutup_jam" type="number" placeholder="Jam Tutup" min="0" max="23">
            <label>Menit Tutup:</label>
            <input name="tutup_menit" type="number" placeholder="Menit Tutup" min="0" max="59">
            <button type="submit">Kirim Waktu ke Semua IP</button>
        </form>
    </div>
</div>

<script>
    // Menampilkan modal
    document.getElementById('addIpBtn').onclick = function() {
        document.getElementById('addIpModal').style.display = "block";
    }
    document.getElementById('sendLinkBtn').onclick = function() {
        document.getElementById('sendLinkModal').style.display = "block";
    }
    document.getElementById('sendWaktuBtn').onclick = function() {
        document.getElementById('sendWaktuModal').style.display = "block";
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
        if (event.target.className === 'modal') {
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
    ip = request.form.get('ip').strip()
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
