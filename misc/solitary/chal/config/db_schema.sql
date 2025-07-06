CREATE TABLE IF NOT EXISTS image (
    id       INT(11)      NOT NULL AUTO_INCREMENT,
    time     TIMESTAMP    NOT NULL DEFAULT CURRENT_TIMESTAMP() ON UPDATE CURRENT_TIMESTAMP(),
    checksum CHAR(40)     NOT NULL,
    url      VARCHAR(512) NOT NULL,
    source   CHAR(32)     NOT NULL,
    size     INT(11)      NOT NULL,
    album    CHAR(32)              DEFAULT NULL,
    PRIMARY KEY (url),
    UNIQUE KEY id (id),
    KEY checksum (checksum),
    KEY url (url),
    KEY album (album),
    KEY time (time)
) DEFAULT CHARSET = utf8mb4
  COLLATE = utf8mb4_general_ci;

