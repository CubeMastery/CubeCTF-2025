<?php
declare(strict_types=1);
require "utils.php";
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <title>Image Upload</title>
    <style>body {
            background: #004165;
        }

        .center {
            position: relative;
            max-width: 400px;
            min-width: 250px;
            width: 80%;
            text-align: center;
            color: #ffffff;
            margin: 20px auto auto;
        }

        .center > * {
            margin: 0;
        }

        #main {
            background: #ADAFAF;
            border-radius: 10px;
            padding: 15px;
        }
    </style>
</head>
<body>
<div class="center" id="main">
    <?php
    if (isset($_GET["album"])) $album = substr(htmlspecialchars($_GET["album"]), 0, 16);
    else $album = null;
    if (isset($_FILES["file"])) {
        $file_count = count($_FILES["file"]["name"]);
        if ($file_count > 0) $connection = db_login();
        for ($i = 0; $i < $file_count; $i++)
            if ($_FILES["file"]["error"][$i] == 0) {
                flush();
                $b2b = sodium_crypto_generichash_init();
                $download = fopen($_FILES["file"]["tmp_name"][$i], "r");
                $len = 0;
                $size = filesize($_FILES["file"]["tmp_name"][$i]);
                $ext = "";
                while (!feof($download)) {
                    $tmp = fread($download, 1024 * 8);
                    if ($len === 0) {
                        $image_info = getimagesizefromstring($tmp);
                        if ($image_info) $ext = image_type_to_extension($image_info[2]);
                        elseif (!$ext = decode_mime($_FILES["file"]["type"][$i])) break;
                    }
                    if (!$tmp) break;
                    $len += strlen($tmp);
//                    if ($len > $size) stop("Something is wrong with the image :( " . $len . "/" . $size); // shouldnt happen
                    if ($len > 500000000) stop("Image too big :(", 413);
                    sodium_crypto_generichash_update($b2b, $tmp);
                }
                if ($ext == ".jpeg") $ext = ".jpg";
                fclose($download);
                if ($ext == "" || $len < 1) {
                    echo "Unsupported: " . htmlspecialchars(basename($_FILES["file"]["name"][$i])) . "<br>";
                    continue;
                }
                $b2b = bin2hex(sodium_crypto_generichash_final($b2b, 16));
                $name = $b2b . $ext;
                if (!is_in_db($connection, $name, $album) || !file_exists(get_storage_path($name))) {
                    add_to_db($connection, $name, "Upload:" . $_FILES["file"]["name"][$i] . " " . gmdate("D M j H:i:s T Y"), $_SERVER["REMOTE_ADDR"], $len, $album);
                    $folder = get_storage_folder($name);
                    mkdir($folder, 0777, true);
                    if (move_uploaded_file($_FILES["file"]["tmp_name"][$i], get_storage_path($name)))
                        echo "Success: <a href='/" . $name . "'>" . htmlspecialchars(basename($_FILES["file"]["name"][$i])) . "</a><br>";
                    else echo "Server Fail: " . htmlspecialchars(basename($_FILES["file"]["name"][$i])) . "<br>";
                } else echo "Duplicate: <a href='/" . $name . "'>" . htmlspecialchars(basename($_FILES["file"]["name"][$i])) . "</a><br>";
            } else echo "Fail: " . htmlspecialchars(basename($_FILES["file"]["name"][$i])) . "<br>";

    }

    ?>
    <br>
    File to upload to mirror:
    <form action="/upload<?php if ($album != null) echo "?album=" . $album ?>" method="post"
          enctype="multipart/form-data">
        <p><input id="file" multiple="multiple" name="file[]" type="file"/></p>
        <input type="submit" onclick="document.getElementById('loading').innerText = 'Loading'"/>
    </form>
    <br>
    <a href="/">URL instead</a>
    <p id="loading"></p>
</div>
</body>
</html>