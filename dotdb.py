from flask import Flask, request, jsonify, render_template_string
import requests
import os

app = Flask(__name__)

API_LIST_URL = "https://dot-store.biz.id/api_list.txt"
LINK_LIST_URL = "https://dot-store.biz.id/link_list.txt"
PORT = 5000

@app.route("/")
def index():
    try:
        api_list = requests.get(API_LIST_URL).text.splitlines()
    except Exception as e:
        api_list = [f"Error: {str(e)}"]
    
    return render_template_string('''
<!DOCTYPE html>
<html lang="id">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>API Manager</title>
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css">
    <style>
        body {
            background-color: #f8f9fa;
        }
        .container {
            margin-top: 50px;
        }
        .api-list {
            max-height: 200px;
            overflow-y: auto;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1 class="text-center mb-4">API Manager</h1>
        <div class="card shadow mb-4">
            <div class="card-body">
                <h5 class="card-title">Opsi</h5>
                <div class="d-grid gap-2">
                    <button class="btn btn-primary" onclick="downloadAndSplit()">Unduh & Bagi Link</button>
                    <button class="btn btn-success" onclick="updateTime()">Perbarui waktu.json</button>
                    <button class="btn btn-info" onclick="updateLinks()">Perbarui link.txt</button>
                </div>
            </div>
        </div>
        <div class="card shadow">
            <div class="card-body">
                <h5 class="card-title">Daftar API</h5>
                <div class="api-list">
                    <ul class="list-group" id="apiList">
                        {% for api in api_list %}
                        <li class="list-group-item">{{ api }}</li>
                        {% endfor %}
                    </ul>
                </div>
            </div>
        </div>
        <div id="response" class="mt-4"></div>
    </div>
    <script>
        async function downloadAndSplit() {
            const response = await fetch('/download', { method: 'POST' });
            const result = await response.json();
            showResponse(result);
        }

        async function updateTime() {
            const tutup_jam = prompt("Masukkan tutup jam:");
            const buka_jam = prompt("Masukkan buka jam:");
            const response = await fetch('/update-waktu', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ tutup_jam, buka_jam })
            });
            const result = await response.json();
            showResponse(result);
        }

        async function updateLinks() {
            const response = await fetch('/update-link', { method: 'POST' });
            const result = await response.json();
            showResponse(result);
        }

        function showResponse(result) {
            const responseDiv = document.getElementById('response');
            responseDiv.innerHTML = `<pre>${JSON.stringify(result, null, 2)}</pre>`;
        }
    </script>
</body>
</html>
''', api_list=api_list)

@app.route("/download", methods=["POST"])
def download_and_split():
    try:
        api_list = requests.get(API_LIST_URL).text.splitlines()
        link_list = requests.get(LINK_LIST_URL).text.splitlines()

        for i, link in enumerate(link_list):
            group_index = i % len(api_list)
            with open(f"link{group_index + 1}.txt", "a") as file:
                file.write(link + "\n")
        
        return jsonify({"message": "Berhasil mengunduh dan membagi link"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/update-waktu", methods=["POST"])
def update_time():
    data = request.json
    tutup_jam = data.get("tutup_jam")
    buka_jam = data.get("buka_jam")

    try:
        api_list = requests.get(API_LIST_URL).text.splitlines()
        for api_ip in api_list:
            payload = {
                "buka_jam": int(buka_jam),
                "buka_menit": 30,
                "tutup_jam": int(tutup_jam),
                "tutup_menit": 0,
            }
            url = f"http://{api_ip}:{PORT}/update-waktu"
            response = requests.post(url, json=payload)
        
        return jsonify({"message": "waktu.json berhasil diperbarui"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/update-link", methods=["POST"])
def update_links():
    try:
        api_list = requests.get(API_LIST_URL).text.splitlines()
        for i, api_ip in enumerate(api_list):
            file_path = f"link{i + 1}.txt"
            if os.path.exists(file_path):
                with open(file_path, "r") as file:
                    links = file.read().strip()
                payload = {"link": links.replace("\n", "\\n")}
                url = f"http://{api_ip}:{PORT}/update-link"
                requests.post(url, json=payload)
        
        return jsonify({"message": "link.txt berhasil diperbarui"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=8000)
