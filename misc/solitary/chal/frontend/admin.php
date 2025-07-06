<?php
require "utils.php";
$connection = db_login();

if (isset($_REQUEST["host"]) and $_REQUEST["host"] != "") {
    if (!is_private_ip($_SERVER["REMOTE_ADDR"])) stop("No access :(", 403);
    $tls = $_REQUEST["tls"] ?? false;
    $method = $_REQUEST["method"] ?? "GET";
    $uri = $_REQUEST["uri"] ?? "/";
    $host = $_REQUEST["host"];
    $host_port = explode(":", $host);
    $port = ($tls) ? 443 : 80;
    $raw_host = $host;
    if (sizeof($host_port) > 1) {
        $raw_host = $host_port[0];
        $port = $host_port[1];
    }
    $ua = $_REQUEST["ua"] ?? $_SERVER["HTTP_USER_AGENT"];
    $accept = $_REQUEST["accept"] ?? "*/*";
    if ($tls) $raw_host = "tls://" . $raw_host;

    $valid = $host != "" and in_array(strtoupper($method), ["GET", "POST"]);
    if (!$valid) stop("Bad request :(");

    $request = $method . " " . $uri . " HTTP/1.1\r\n";
    $request .= "Host: " . $host . "\r\n";
    $request .= "User-Agent: " . $ua . "\r\n";
    $request .= "Accept: " . $accept . "\r\n";
    $request .= "Connection: Close\r\n\r\n";

    $socket = fsockopen($raw_host, $port, $errno, $errstr, 5);
    if (!$socket) {
        stop("Error: $errstr ($errno)");
    }
    socket_set_timeout($socket, 5);

    fwrite($socket, $request);

    $response = "";
    while (!feof($socket) and strlen($response) < 10_000) {
        $response .= fgets($socket, 1024);
    }

    fclose($socket);
    ?>Response data:
    <pre><?= htmlspecialchars($response) ?></pre>
    <?php
    exit();
}
?>


<!DOCTYPE html>
<html lang="en">
<head>
    <title>Mirror Admin Interface</title>
    <style type="text/css">body {
            background: #004165;
        }

        .center {
            max-width: 400px;
            min-width: 250px;
            width: 80%;
            margin: auto;
            text-align: center;
            color: #ffffff;
        }

        .center > * {
            margin: 0;
        }

        #test > * {
            margin: 0;
            text-align: left;
        }

        .test_data {
            display: flex;
        }

        .test_data > input {
            width: 100%;
        }

        #main {
            background: #adafaf;
            border-radius: 10px;
            padding: 15px;
        }
    </style>
</head>
<body>
<div class="center" id="main">
    Latest image:
    <?php
    $result = $connection->execute_query("SELECT checksum,album,size FROM image ORDER BY id DESC LIMIT 1");
    $row = $result->fetch_assoc();
    if ($row) {
        ?>
        <div id="image">
            <img loading="lazy" alt="Error" src="/<?= $row["checksum"]; ?>"
                 title="<?= $row["album"] === null ? "No Album" : $row["album"] ?>"
                 width="250px">
            <a href="/<?= $row["checksum"]; ?>"><?= $row["checksum"] ?></a> (<?= $row["size"] ?> bytes)
        </div>
    <?php } ?>
    <br>

    <form id="new">
        <fieldset>
            <legend> Add new image:</legend>
            <p><label for="url">Url: </label><input id="url" type="url" autofocus></p>
            <input type="submit">
        </fieldset>
    </form>
    <script>
        document.getElementById("new").addEventListener("submit", (e) => {
            e.preventDefault();
            location.href += document.getElementById("url").value;
        });
    </script>
    <br>
    <a href="/upload">Upload instead</a>
    <br>
    <form id="test" method="POST" action="/admin">
        <fieldset>
            <legend>Test image retrieval</legend>
            <label for="tls">TLS:&nbsp;</label><input type="checkbox" id="tls" name="tls">
            <div class="test_data">
                <!--<label for="method">Method: </label><select id="method" name="method"><option value="GET">GET</option><option value="POST">POST</option></select>-->
                GET&nbsp;<input id="uri" name="uri" placeholder="/">&nbsp;HTTP/1.1
            </div>
            <div class="test_data">
                <label for="host">Host:&nbsp;</label>
                <input id="host" name="host" placeholder="cyber.cyber">
            </div>
            <div class="test_data">
                <label for="ua">User&#8209;Agent:&nbsp;</label>
                <input id="ua" name="ua" value="<?= $_SERVER['HTTP_USER_AGENT'] ?>">
            </div>
            <div class="test_data">
                <label for="accept">Accept:&nbsp;</label>
                <input id="accept" name="accept" value="*/*">
            </div>
            <input type="submit">
        </fieldset>
    </form>
</div>
</body>
</html>
