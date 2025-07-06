<?php
declare(strict_types=1);
require "utils.php";
$url = $_SERVER["REQUEST_URI"];

$album = null;

if (str_starts_with($url, "/http%3") || str_starts_with($url, "/https%3")) $url = urldecode($url);
if (!(str_starts_with($url, "/http://") || str_starts_with($url, "/https://"))) stop("That doesnt look like a valid url!" . $url);
$url = substr($url, 1);

$url = str_replace("//imgur.com/", "//i.imgur.com/", $url);
$host = explode("/", explode("//", $url)[1])[0];
$host_port = explode(":", $host);
if (sizeof($host_port) == 2) {
    $host = $host_port[0];
    $port = $host_port[1];
} elseif (sizeof($host_port) > 2) stop("Server is allergic to ipv6 :(");
if (str_contains($host, "imgur.com") and !str_contains(substr($url, -5), ".")) $url .= ".jpg";
if (str_contains($host, "imgur.com") and str_contains($url, ".gifv")) $url = str_replace(".gifv", ".mp4", $url);

// login to db
$connection = db_login();


$link = $_SERVER["REQUEST_SCHEME"] . "://" . $_SERVER["HTTP_HOST"] . "/";


// is url in db?
$redownload = false;
$statement = $connection->prepare("SELECT checksum, album FROM mirror.image WHERE url = ?;");
$statement->bind_param("s", $url);
$statement->execute();
if ($result = $statement->get_result()) if ($result->num_rows > 0) {
    $result = $result->fetch_assoc();
    $name = $result["checksum"];
    try {
        $path = get_storage_path($name);

        if (file_exists($path) and filesize($path) > 0) {
            header("State: Old");
            header("Size: " . filesize($path));
            header("Album: " . $result["album"]);
            header("Location: " . $link . $name);
            header("X-is-it-working: no");
            stop($link . $name, 301);
        } else $redownload = true;
    } catch (Exception $e) {
        $redownload = true;
    }
}

// disallow local
if (is_private_ip(gethostbyname($host))) {
    stop("That's not very nice. :(", 403);
}

// Download and checksum file
$buff = "";
$ext = "";
$len = 0;
$name = "";
try {
    ini_set("user_agent", "Mozilla/5.0 (X11; Linux x86_64; rv:134.0) Gecko/20100101 Firefox/134.0");
    $request = @fopen($url, 'rb', false, stream_context_create([
        "ssl" => ["verify_peer" => false, "verify_peer_name" => false],
        "http" => ["header" => "accept-encoding: gzip, deflate, br\r\naccept: */*\r\nx-requested-by: " . $_SERVER["REMOTE_ADDR"]]
    ]));
    if (!$request) stop("That image does not like me :(");
    $b2b = sodium_crypto_generichash_init();
    $size = -1;
    foreach ($http_response_header as $header) if (str_starts_with(strtolower($header), "content-length:")) {
        $size = (int)substr($header, 15);
        break;
    }

    while (!feof($request)) {
        $tmp = fread($request, 1024 * 8);
        if ($buff === "") {
            $image_info = getimagesizefromstring($tmp);
//            print_r($http_response_header);
            if ($image_info) $ext = image_type_to_extension($image_info[2]); elseif (!$ext = decode_mime_headers($http_response_header)) stop("Unsupported image type :(", 415);
            if ($ext == ".jpeg") $ext = ".jpg";
        }
        if (!$tmp) break;
        $len += strlen($tmp);
//        print_r($http_response_header);
        if ($len > $size) stop("Something is wrong with the image :( " . $len . "/" . $size);
        if ($len > 100000000) stop("Image too big :(", 413);
        sodium_crypto_generichash_update($b2b, $tmp);
        $buff .= $tmp;
    }
    fclose($request);
    if ($ext == "" || $len < 1) stop("Something is wrong with the image :(");
    $b2b = bin2hex(sodium_crypto_generichash_final($b2b, 16));
    $name = $b2b . $ext;
} catch (Exception $e) {
    stop("Lmao what?", 500);
}

// is in db
$in_db = is_in_db($connection, $name);


// get album
if ($album === null and isset(getallheaders()["Album"])) $album = getallheaders()["Album"];

// add to db
try {
    add_to_db($connection, $name, $url, $_SERVER["REMOTE_ADDR"], $len, $album);
} catch (mysqli_sql_exception $e) {
    if (!$in_db) stop("DB Error");
}

// save file
if (!$in_db || $redownload) {
    $folder = get_storage_folder($name);

    mkdir($folder, 0777, true);

    $new_file = fopen(get_storage_path($name), 'wb');
    fwrite($new_file, $buff);
    fclose($new_file);
}

$link .= $name;
// return link
header("Location: " . $link);
header("Album: " . $album);
header("Size: " . $len);
header("State: " . ($in_db ? "Alt" : "New"));
stop($link, 301);
