from flask import Flask, request, jsonify
import requests
import json
import os

app = Flask(__name__)

# ====== Konfigurasi ======
PORT = 5000  # Port target server RDP
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

ip_list = load_ips()

# ====== Endpoint API ======

@app.route('/api/ip_list', methods=['GET'])
def get_ip_list():
    return jsonify({"ip_list": ip_list})

@app.route('/api/add_ip', methods=['POST'])
def api_add_ip():
    data = request.json
    new_ips = data.get("ips", [])
    added = []
    for ip in new_ips:
        if ip not in ip_list:
            ip_list.append(ip)
            added.append(ip)
    save_ips(ip_list)
    return jsonify({"added": added, "total": len(ip_list)})

@app.route('/api/delete_ip', methods=['POST'])
def api_delete_ip():
    data = request.json
    ip = data.get("ip")
    if ip in ip_list:
        ip_list.remove(ip)
        save_ips(ip_list)
        return jsonify({"message": f"{ip} removed"})
    return jsonify({"error": "IP not found"}), 404

@app.route('/api/clear_ips', methods=['POST'])
def api_clear_ips():
    ip_list.clear()
    save_ips(ip_list)
    return jsonify({"message": "All IPs cleared"})

@app.route('/api/send_link', methods=['POST'])
def api_send_link():
    data = request.json
    links = [l.strip() for l in data.get("links", []) if l.strip()]
    results = []

    if not ip_list:
        return jsonify({"error": "No IPs available"}), 400

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
            results.append({ip: {"link_count": len(ip_links_map[ip]), "response": msg}})
        except Exception as e:
            results.append({ip: {"error": str(e)}})

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
            results.append({ip: {"response": msg}})
        except Exception as e:
            results.append({ip: {"error": str(e)}})

    return jsonify({"results": results})

# ====== Run API Server ======
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
