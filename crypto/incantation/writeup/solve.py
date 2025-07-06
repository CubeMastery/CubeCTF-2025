import socket
from collections import Counter, defaultdict

HOST = '192.168.88.20'
PORT = 5757

MAX_FLAG_LENGTH = 100

freq = [Counter() for _ in range(MAX_FLAG_LENGTH)]

with socket.create_connection((HOST, PORT)) as sock:
    buffer = b""
    samples_collected = 0

    while True:
        chunk = sock.recv(1024)
        if not chunk:
            break
        buffer += chunk

        while b'\r' in buffer:
            line, buffer = buffer.split(b'\r', 1)
            try:
                line = line.decode('utf-8', errors='ignore')
                for i in range(min(len(line), MAX_FLAG_LENGTH)):
                    freq[i][line[i]] += 1
                samples_collected += 1
            except Exception:
                continue
        print(''.join(f.most_common(1)[0][0] for f in freq if f))
