from flask import Flask, request, jsonify
from flask_cors import CORS  # ✅ Tambahan
import requests
import json
import os

app = Flask(__name__)
CORS(app)  # ✅ Mengizinkan semua origin mengakses API ini (termasuk GitHub Pages)

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

# ====== API PUBLIC ======

@app.route('/api/ip_list', methods=['GET'])
def get_ip_list():
    return jsonify({"ip_list": ip_list})

@app.route('/api/add_ip', methods=['POST'])
def api_add_ip():
    ips = request.json.get('ips', [])
    added = []
    for ip in ips:
        ip = ip.strip()
        if ip and ip not in ip_list:
            ip_list.append(ip)
            added.append(ip)
    save_ips(ip_list)
    return jsonify({"message": f"{len(added)} IP ditambahkan", "added": added})

@app.route('/api/delete_ip', methods=['POST'])
def api_delete_ip():
    ip = request.json.get('ip')
    if ip in ip_list:
        ip_list.remove(ip)
        save_ips(ip_list)
        return jsonify({"message": f"IP {ip} dihapus"})
    return jsonify({"error": "IP tidak ditemukan"}), 404

@app.route('/api/clear_ip', methods=['POST'])
def api_clear_ip():
    ip_list.clear()
    save_ips(ip_list)
    return jsonify({"message": "Semua IP dihapus"})

@app.route('/api/send_link', methods=['POST'])
def api_send_link():
    links = request.json.get('links', [])
    links = [l.strip() for l in links if l.strip()]
    results = []

    if not ip_list:
        return jsonify({"error": "Tidak ada IP yang ditambahkan."}), 400

    # Buat map IP ke link-list
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
            results.append({"ip": ip, "status": "success", "message": msg, "link_count": len(ip_links_map[ip])})
        except Exception as e:
            results.append({"ip": ip, "status": "error", "message": str(e)})

    return jsonify({"results": results})

@app.route('/api/send_waktu', methods=['POST'])
def api_send_waktu():
    waktu = {
        "buka_jam": int(request.json.get('buka_jam', 0)),
        "buka_menit": int(request.json.get('buka_menit', 0)),
        "tutup_jam": int(request.json.get('tutup_jam', 0)),
        "tutup_menit": int(request.json.get('tutup_menit', 0)),
    }

    results = []
    for ip in ip_list:
        url = f"http://{ip}:{PORT}/update-waktu"
        try:
            r = requests.post(url, json=waktu, timeout=5)
            msg = r.json().get("message", r.text)
            results.append({"ip": ip, "status": "success", "message": msg})
        except Exception as e:
            results.append({"ip": ip, "status": "error", "message": str(e)})

    return jsonify({"results": results})

# ====== Run Server ======
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
