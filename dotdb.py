from flask import Flask, request, render_template_string, redirect, url_for
import requests
import json
import os

app = Flask(__name__)

# ====== Konfigurasi ======
PORT = 5000
IP_FILE = "ip_list.json"

# ====== IP Handling ======
def load_ips():
    if os.path.exists(IP_FILE):
        with open(IP_FILE, "r") as f:
            return json.load(f)
    return []

def save_ips(ip_list):
    with open(IP_FILE, "w") as f:
        json.dump(ip_list, f, indent=4)

# ====== HTML Template ======
HTML_TEMPLATE = '''<!DOCTYPE html>
<html>
<head>
    <title>Control Panel Multi RDP</title>
    <style>
        /* CSS seperti sebelumnya (tidak diubah) */
    </style>
</head>
<body>
<div class="container">
    <h2>Control Panel Multi RDP</h2>

    <form method="POST" action="/add_ip" onsubmit="showModal('IP berhasil ditambahkan!')">
        <label>Tambah IP RDP (tanpa http:// dan port):</label>
        <input name="ip" placeholder="192.168.1.10" required>
        <button type="submit">Tambah</button>
    </form>

    {% if ip_list %}
    <div class="ip-list">
        <h4>Daftar IP Aktif:</h4>
        {% for ip in ip_list %}
            <div class="ip-item">
                <span>{{ loop.index }}. {{ ip }}</span>
                <form method="POST" action="/delete_ip" style="display:inline;" onsubmit="showModal('IP dihapus!')">
                    <input type="hidden" name="ip" value="{{ ip }}">
                    <button type="submit">Hapus</button>
                </form>
            </div>
        {% endfor %}
        <form method="POST" action="/clear_ip" onsubmit="showModal('Semua IP telah dihapus!')">
            <button type="submit" style="background:#dc3545;">Hapus Semua</button>
        </form>
    </div>
    {% endif %}

    <hr>

    <form method="POST" action="/send_link" onsubmit="showModal('Link dikirim ke IP!')">
        <label>Link (satu per baris):</label>
        <textarea name="links" rows="5" placeholder="https://example.com/page1\nhttps://example.com/page2"></textarea>
        <button type="submit">Kirim Link ke IP</button>
    </form>

    <form method="POST" action="/send_waktu" onsubmit="showModal('Waktu dikirim ke semua IP!')">
        <h4>Waktu</h4>
        <input name="buka_jam" type="number" placeholder="Buka Jam">
        <input name="buka_menit" type="number" placeholder="Buka Menit">
        <input name="tutup_jam" type="number" placeholder="Tutup Jam">
        <input name="tutup_menit" type="number" placeholder="Tutup Menit">
        <button type="submit">Kirim Waktu ke Semua IP</button>
    </form>

    {% if results %}
    <div class="results">
        {% for res in results %}
            {{ res }}<br>
        {% endfor %}
    </div>
    {% endif %}
</div>

<!-- Modal -->
<div id="myModal" class="modal">
    <div class="modal-content">
        <span class="close" onclick="closeModal()">&times;</span>
        <p id="modalText">Notifikasi</p>
    </div>
</div>

<script>
    function showModal(message) {
        event.preventDefault();
        document.getElementById("modalText").innerText = message;
        document.getElementById("myModal").style.display = "block";
        setTimeout(() => {
            document.getElementById("myModal").style.display = "none";
            event.target.submit();
        }, 1200);
    }

    function closeModal() {
        document.getElementById("myModal").style.display = "none";
    }

    window.onclick = function(event) {
        if (event.target === document.getElementById("myModal")) {
            closeModal();
        }
    }
</script>
</body>
</html>
'''

# ====== Routes ======

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE, ip_list=load_ips(), results=[])

@app.route('/add_ip', methods=['POST'])
def add_ip():
    ip = request.form.get('ip', '').strip()
    ip_list = load_ips()
    if ip and ip not in ip_list:
        ip_list.append(ip)
        save_ips(ip_list)
    return redirect(url_for('index'))

@app.route('/delete_ip', methods=['POST'])
def delete_ip():
    ip = request.form.get('ip')
    ip_list = load_ips()
    if ip in ip_list:
        ip_list.remove(ip)
        save_ips(ip_list)
    return redirect(url_for('index'))

@app.route('/clear_ip', methods=['POST'])
def clear_ip():
    save_ips([])
    return redirect(url_for('index'))

@app.route('/send_link', methods=['POST'])
def send_link():
    links = [l.strip() for l in request.form.get('links', '').strip().splitlines() if l.strip()]
    ip_list = load_ips()
    results = []

    if not ip_list:
        results.append("❌ Tidak ada IP yang ditambahkan.")
        return render_template_string(HTML_TEMPLATE, ip_list=ip_list, results=results)

    ip_links_map = {ip: [] for ip in ip_list}
    for i, link in enumerate(links):
        ip_links_map[ip_list[i % len(ip_list)]].append(link)

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
    def parse_int_or_none(val):
        try:
            return int(val)
        except (ValueError, TypeError):
            return None

    waktu = {
        "buka_jam": parse_int_or_none(request.form.get('buka_jam')),
        "buka_menit": parse_int_or_none(request.form.get('buka_menit')),
        "tutup_jam": parse_int_or_none(request.form.get('tutup_jam')),
        "tutup_menit": parse_int_or_none(request.form.get('tutup_menit')),
    }

    ip_list = load_ips()
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

# ====== Jalankan Server ======
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
