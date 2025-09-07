<?php
// === proses simpan config ===
if ($_SERVER["REQUEST_METHOD"] == "POST") {
    $config = [
        "url" => $_POST["url"],
        "user" => $_POST["user"],
        "pass" => $_POST["pass"],
        "threads" => (int)$_POST["threads"],
        "algo" => $_POST["algo"]
    ];
    $json = json_encode($config, JSON_PRETTY_PRINT);
    file_put_contents("config.json", $json, LOCK_EX);
    $message = "✅ Config berhasil disimpan!";
}

// === ambil isi config.json ===
$config = json_decode(file_get_contents("config.json"), true);
?>
<!DOCTYPE html>
<html lang="id">
<head>
  <meta charset="UTF-8">
  <title>Config Editor</title>
  <meta name="viewport" content="width=device-width, initial-scale=1.0"> <!-- penting untuk responsif -->
  <style>
    body {
      font-family: Arial, sans-serif;
      margin: 0;
      padding: 20px;
      background: #111;
      color: #eee;
    }
    .container {
      max-width: 600px;
      margin: auto;
      padding: 20px;
      background: #222;
      border-radius: 10px;
      box-shadow: 0 0 15px rgba(0,0,0,0.5);
    }
    h2 {
      text-align: center;
      margin-bottom: 20px;
      color: #00ffc6;
    }
    label {
      display: block;
      margin-top: 15px;
      font-size: 0.9rem;
      color: #ddd;
    }
    input {
      width: 100%;
      padding: 10px;
      margin-top: 5px;
      border-radius: 8px;
      border: none;
      font-size: 1rem;
      box-sizing: border-box;
    }
    button {
      margin-top: 20px;
      padding: 12px;
      width: 100%;
      background: teal;
      color: white;
      border: none;
      border-radius: 8px;
      font-size: 1rem;
      cursor: pointer;
      transition: background 0.3s;
    }
    button:hover {
      background: darkcyan;
    }
    .message {
      text-align: center;
      margin-bottom: 15px;
      color: lightgreen;
      font-weight: bold;
    }
    /* Responsif */
    @media (max-width: 600px) {
      body {
        padding: 10px;
      }
      .container {
        padding: 15px;
      }
      h2 {
        font-size: 1.2rem;
      }
      input, button {
        font-size: 0.9rem;
        padding: 8px;
      }
    }
  </style>
</head>
<body>
  <div class="container">
    <h2>Edit Config JSON</h2>

    <?php if (!empty($message)): ?>
      <div class="message"><?php echo $message; ?></div>
    <?php endif; ?>

    <form action="panel.php" method="post">
      <label>URL:</label>
      <input type="text" name="url" value="<?php echo htmlspecialchars($config['url']); ?>">

      <label>User:</label>
      <input type="text" name="user" value="<?php echo htmlspecialchars($config['user']); ?>">

      <label>Password:</label>
      <input type="text" name="pass" value="<?php echo htmlspecialchars($config['pass']); ?>">

      <label>Threads:</label>
      <input type="number" name="threads" value="<?php echo htmlspecialchars($config['threads']); ?>">

      <label>Algo:</label>
      <input type="text" name="algo" value="<?php echo htmlspecialchars($config['algo']); ?>">

      <button type="submit">Simpan Config</button>
    </form>
  </div>
</body>
</html>
