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
<!DOCTYPE html>
<html>
<head>
    <title>Control Panel Multi RDP</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: #eef1f5;
            padding: 30px;
        }
        .container {
            background: white;
            padding: 25px 30px;
            border-radius: 12px;
            max-width: 700px;
            margin: auto;
            box-shadow: 0 8px 24px rgba(0,0,0,0.1);
        }
        h2, h4 {
            margin-bottom: 20px;
            color: #333;
        }
        label {
            font-weight: 500;
            margin-top: 15px;
            display: block;
        }
        textarea, input {
            width: 100%;
            padding: 12px;
            margin-top: 8px;
            border: 1px solid #ccc;
            border-radius: 8px;
            font-size: 14px;
        }
        button {
            margin-top: 15px;
            padding: 12px;
            background-color: #007bff;
            color: white;
            border: none;
            border-radius: 8px;
            cursor: pointer;
            font-weight: 600;
            transition: background 0.3s;
        }
        button:hover {
            background-color: #0056b3;
        }
        .ip-list {
            margin-top: 20px;
        }
        .ip-item {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 8px 0;
            border-bottom: 1px solid #eee;
        }
        .results {
            background: #e8f0ff;
            padding: 12px;
            border-radius: 8px;
            margin-top: 25px;
            white-space: pre-wrap;
            border: 1px solid #cbd6ee;
        }

        /* Popup Modal */
        .modal {
            display: none;
            position: fixed;
            z-index: 1000;
            padding-top: 100px;
            left: 0;
            top: 0;
            width: 100%;
            height: 100%;
            overflow: auto;
            background-color: rgba(0,0,0,0.4);
        }
        .modal-content {
            background-color: #fff;
            margin: auto;
            padding: 20px;
            border-radius: 10px;
            width: 80%;
            max-width: 400px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.3);
            text-align: center;
        }
        .close {
            color: #aaa;
            float: right;
            font-size: 24px;
            font-weight: bold;
            cursor: pointer;
        }
        .close:hover {
            color: #000;
        }
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

<!-- Modal Popup -->
<div id="myModal" class="modal">
    <div class="modal-content">
        <span class="close" onclick="closeModal()">&times;</span>
        <p id="modalText">Notifikasi</p>
    </div>
</div>

<script>
    function showModal(message) {
        event.preventDefault(); // mencegah form submit langsung
        document.getElementById("modalText").innerText = message;
        document.getElementById("myModal").style.display = "block";
        setTimeout(() => {
            document.getElementById("myModal").style.display = "none";
            event.target.submit(); // submit setelah tampil sebentar
        }, 1200);
    }

    function closeModal() {
        document.getElementById("myModal").style.display = "none";
    }

    window.onclick = function(event) {
        const modal = document.getElementById("myModal");
        if (event.target === modal) {
            modal.style.display = "none";
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
    # Ambil data dan ubah ke integer (bukan string)
    def parse_int_or_none(value):
        try:
            return int(value)
        except (ValueError, TypeError):
            return None

    waktu = {
        "buka_jam": parse_int_or_none(request.form.get('buka_jam')),
        "buka_menit": parse_int_or_none(request.form.get('buka_menit')),
        "tutup_jam": parse_int_or_none(request.form.get('tutup_jam')),
        "tutup_menit": parse_int_or_none(request.form.get('tutup_menit')),
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
