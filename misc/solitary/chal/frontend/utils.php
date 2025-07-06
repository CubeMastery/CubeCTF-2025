<?php
declare(strict_types=1);

function decode_mime_headers(array $headers): false|string {
    $mime = "";
    foreach ($headers as $header) if (str_contains(strtolower($header), "content-type:")) {
        if (str_contains(strtolower($header), "text/html")) continue;
        $mime = substr($header, 14);
        break;
    }
    return decode_mime($mime);
}


function decode_mime(string $mime): false|string {
    return match ($mime) {
        "image/bmp" => ".bmp",
        "image/gif" => ".gif",
        "image/vnd.microsoft.icon" => ".ico",
        "image/jpeg", "image/jpg" => ".jpg",
        "image/png" => ".png",
        "image/tiff" => ".tif",
        "image/webp" => ".webp",
        "video/mpeg" => ".mpeg",
        "video/mp4" => ".mp4",
        "video/ogg" => ".ogv",
        "video/mp2t" => ".ts",
        "audio/3gpp", "video/3gpp" => ".3gp",
        "audio/3gpp2", "video/3gpp2" => ".3g2",
        "audio/aac" => ".aac",
        "audio/midi", "audio/x-midi" => ".mid",
        "audio/mpeg" => ".mp3",
        "audio/ogg" => ".oga",
        "audio/opus" => ".opus",
        "audio/wav" => ".wav",
        "audio/webm" => ".weba",
        default => false,
    };
}


function stop(string $message, int $code = 400) {
    http_response_code($code);
    die($message);
}


function is_in_db(mysqli $connection, string $name, ?string $album = null): bool {
    $statement = $connection->prepare("SELECT checksum,album FROM mirror.image WHERE checksum = ?");
    $statement->bind_param("s", $name);
    $statement->execute();
    if ($result = $statement->get_result()) if ($content = $result->fetch_assoc()) {
        if ($album != null and $album != $content["album"]) {
            $statement = $connection->prepare("UPDATE mirror.image SET album = ? WHERE checksum = ?;");
            $statement->bind_param("ss", $album, $content["checksum"]);
            $statement->execute();
        }
        return true;
    }
    return false;
}


function add_to_db(mysqli $connection, string $name, string $url, string $source, int $size, ?string $album = null): void {
    $statement = $connection->prepare("INSERT INTO mirror.image (checksum, url, source, size, album) VALUES (?, ?, ?, ?, ?)");
    $statement->bind_param("sssss", $name, $url, $source, $size, $album);
    $statement->execute();
}


function db_login(): mysqli {
    $connection = "";
    try {
        @$connection = new mysqli("p:mariadb", "root", getenv("MARIADB_ROOT_PASSWORD"), getenv("MARIADB_DATABASE"));

        if ($connection->connect_errno) throw new Exception("Error: " . $connection->connect_errno . ". " . $connection->connect_error . "");
    } catch (Throwable $e) {
        stop("Server Error!<br>I lost my database ¯\_(ツ)_/¯", 500);
    }
    return $connection;
}


function get_storage_folder(string $hash_name): string {
    return "../storage/" . substr($hash_name, 0, 2) . "/" . substr($hash_name, 2, 2) . "/";
}


function get_storage_path(string $hash_name): string {
    return get_storage_folder($hash_name) . $hash_name;
}

function is_private_ip(string $ip):bool {
    return filter_var($ip, FILTER_VALIDATE_IP, FILTER_FLAG_IPV4 | FILTER_FLAG_NO_PRIV_RANGE | FILTER_FLAG_NO_RES_RANGE) === false;
}