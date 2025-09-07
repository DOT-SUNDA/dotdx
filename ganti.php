<?php
if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $ips = trim($_POST['ips'] ?? '');

    if (!empty($ips)) {
        // Simpan script ke file sementara
        $script = <<<BASH
#!/bin/bash

USER="cloudsigma"
OLD_PASSWORD="Cloud2025"
NEW_PASSWORD="Dotaja123@HHHH"

IPS="$ips"

IFS=',' read -ra IP_LIST <<< "\$IPS"

for IP in "\${IP_LIST[@]}"; do
    echo "Mengganti Sandi Vps \$IP..."

    /usr/bin/expect << EOF > /dev/null 2>&1
        set timeout 10
        spawn ssh \$USER@\$IP
        expect {
            "yes/no" { send "yes\r"; exp_continue }
            "password:" { send "\$OLD_PASSWORD\r" }
        }
        expect "Your password has expired. You must change your password now and login again!"
        expect "Current password:" { send "\$OLD_PASSWORD\r" }
        expect "New password:" { send "\$NEW_PASSWORD\r" }
        expect "Retype new password:" { send "\$NEW_PASSWORD\r" }
        expect eof
EOF

    echo "Koneksi ulang ke \$IP dengan password baru dan sudo su..."

    /usr/bin/expect << EOF
        set timeout 10
        spawn ssh \$USER@\$IP
        expect {
            "yes/no" { send "yes\r"; exp_continue }
            "password:" { send "\$NEW_PASSWORD\r" }
        }
        expect "\\$ "
        send "sudo su\r"
        expect "password for \$USER:"
        send "\$NEW_PASSWORD\r"
        expect "# "
        send "nohup bash -c \\"sudo bash -c \\\\\\"\$(curl -fsSL https://raw.githubusercontent.com/DOT-SUNDA/SOCKS/refs/heads/main/kontol.sh)\\\\\\"\" > /tmp/output.log 2>&1 &\r"
        expect "# "
        send "exit\r"
        expect "\\$ "
        send "exit\r"
        expect eof
EOF

done
BASH;

        $tmpFile = tempnam(sys_get_temp_dir(), 'runscript_');
        file_put_contents($tmpFile, $script);
        chmod($tmpFile, 0755);

        // Jalankan script
        $output = shell_exec("bash $tmpFile 2>&1");

        unlink($tmpFile);
    } else {
        $output = "Masukkan IP terlebih dahulu.";
    }
}
?>
<!DOCTYPE html>
<html lang="id">
<head>
    <meta charset="UTF-8">
    <title>Panel Jalankan Script</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body { font-family: Arial, sans-serif; background: #1e1e1e; color: #f0f0f0; padding: 20px; }
        .container { max-width: 700px; margin: auto; background: #2a2a2a; padding: 20px; border-radius: 12px; }
        h2 { text-align: center; }
        textarea, input, button {
            width: 100%; padding: 10px; margin: 10px 0;
            border: none; border-radius: 8px; font-size: 14px;
        }
        textarea { height: 80px; resize: vertical; }
        button {
            background: #0078d7; color: white; font-weight: bold;
            cursor: pointer; transition: background 0.2s;
        }
        button:hover { background: #005fa3; }
        pre {
            background: #111; padding: 15px; border-radius: 8px;
            overflow-x: auto; white-space: pre-wrap; word-wrap: break-word;
        }
    </style>
</head>
<body>
    <div class="container">
        <h2>Panel Jalankan Script VPS</h2>
        <form method="post">
            <label>Masukkan IP (pisahkan dengan koma jika banyak):</label>
            <textarea name="ips" placeholder="Contoh: 49.157.61.51,49.157.61.52"><?= htmlspecialchars($_POST['ips'] ?? '') ?></textarea>
            <button type="submit">Jalankan</button>
        </form>

        <?php if (!empty($output)): ?>
            <h3>Hasil Output:</h3>
            <pre><?= htmlspecialchars($output) ?></pre>
        <?php endif; ?>
    </div>
</body>
</html>
