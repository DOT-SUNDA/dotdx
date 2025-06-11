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
      <button onclick="document.getElementById('ipModal').classList.remove('hidden')" class="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded mb-4">
  📜 Daftar IP
</button>
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

<div id="ipModal" class="hidden fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
  <div class="bg-gray-900 border border-gray-700 rounded-lg p-6 w-full max-w-lg relative">
    <h3 class="text-xl font-bold mb-4 text-green-400">📋 Daftar IP</h3>
    <ul class="mb-4 space-y-2 max-h-64 overflow-y-auto pr-2">
      {% for ip in ip_list %}
        <li class="flex justify-between items-center bg-gray-800 px-3 py-2 rounded">
          <span>{{ ip }}</span>
          <form method="POST" action="/delete_ip" class="inline">
            <input type="hidden" name="ip" value="{{ ip }}">
            <button class="text-red-400 hover:text-red-300 text-sm">Hapus</button>
          </form>
        </li>
      {% endfor %}
    </ul>
    <div class="flex justify-end gap-2">
      <form method="POST" action="/clear_ip">
        <button class="bg-yellow-600 hover:bg-yellow-700 text-white px-3 py-1 rounded text-sm">Hapus Semua</button>
      </form>
      <button onclick="document.getElementById('ipModal').classList.add('hidden')" class="bg-gray-600 hover:bg-gray-700 text-white px-3 py-1 rounded text-sm">
        Tutup
      </button>
    </div>
  </div>
</div>


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
