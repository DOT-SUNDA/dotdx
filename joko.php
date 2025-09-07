<?php
if ($_SERVER["REQUEST_METHOD"] == "POST") {
    $config = [
        "url" => $_POST["url"],
        "user" => $_POST["user"],
        "pass" => $_POST["pass"],
        "threads" => (int)$_POST["threads"],
        "algo" => $_POST["algo"]
    ];

    $json = json_encode($config, JSON_PRETTY_PRINT);

    file_put_contents("config.json", $json);

    echo "<h3>Config berhasil disimpan!</h3>";
    echo "<pre>$json</pre>";
    echo '<a href="panel.html">Kembali</a>';
}
?>
