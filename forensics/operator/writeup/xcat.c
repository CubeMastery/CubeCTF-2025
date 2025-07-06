#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <arpa/inet.h>
#include <sys/socket.h>
#include <fcntl.h>
#include <errno.h>
#include <sys/select.h>

#define BUF_SIZE 1024
#define KEY_LEN 16

unsigned char key[KEY_LEN] = {
    0x13, 0x37, 0xC0, 0xDE, 0x42, 0x69, 0xB0, 0x0B,
    0xDE, 0xAD, 0xBE, 0xEF, 0xFE, 0xED, 0xFA, 0xCE
};

void xor_encrypt(unsigned char *data, size_t len) {
    for (size_t i = 0; i < len; ++i) {
        data[i] ^= key[i % KEY_LEN];
    }
}

void chat(int sock) {
    fd_set fds;
    unsigned char buf[BUF_SIZE];
    int n;

    while (1) {
        FD_ZERO(&fds);
        FD_SET(0, &fds);
        FD_SET(sock, &fds);

        if (select(sock + 1, &fds, NULL, NULL, NULL) < 0) {
            break;
        }

        if (FD_ISSET(0, &fds)) {
            n = read(0, buf, BUF_SIZE);
            if (n <= 0) break;
            xor_encrypt(buf, n);
            if (send(sock, buf, n, 0) != n) {
                break;
            }
        }

        if (FD_ISSET(sock, &fds)) {
            n = recv(sock, buf, BUF_SIZE, 0);
            if (n <= 0) break;
            xor_encrypt(buf, n);
            write(1, buf, n);
        }
    }
}

void run_server(int port) {
    int server_fd, client_fd;
    struct sockaddr_in addr = {0};

    server_fd = socket(AF_INET, SOCK_STREAM, 0);
    if (server_fd < 0) {
        exit(1);
    }

    addr.sin_family = AF_INET;
    addr.sin_port = htons(port);
    addr.sin_addr.s_addr = INADDR_ANY;

    if (bind(server_fd, (struct sockaddr*)&addr, sizeof(addr)) < 0) {
        exit(1);
    }

    if (listen(server_fd, 1) < 0) {
        exit(1);
    }

    client_fd = accept(server_fd, NULL, NULL);
    if (client_fd < 0) {
        exit(1);
    }

    close(server_fd);
    chat(client_fd);
    close(client_fd);
}

void run_client(const char *host, int port) {
    int sock;
    struct sockaddr_in addr = {0};

    sock = socket(AF_INET, SOCK_STREAM, 0);
    if (sock < 0) {
        exit(1);
    }

    addr.sin_family = AF_INET;
    addr.sin_port = htons(port);
    if (inet_pton(AF_INET, host, &addr.sin_addr) <= 0) {
        exit(1);
    }

    if (connect(sock, (struct sockaddr*)&addr, sizeof(addr)) < 0) {
        exit(1);
    }

    chat(sock);
    close(sock);
}

int main(int argc, char *argv[]) {
    if (argc == 3 && strcmp(argv[1], "-l") == 0) {
        int port = atoi(argv[2]);
        run_server(port);
    } else if (argc == 3) {
        const char *host = argv[1];
        int port = atoi(argv[2]);
        run_client(host, port);
    } else {
        return 1;
    }

    return 0;
}
