import encrypt_module
from hashlib import sha256
import numpy as np
import sys

def encrypt(data):
    hsh = sha256(data).digest()
    data = np.frombuffer(data, dtype=np.uint8)
    enc = encrypt_module.encrypt(data)
    return hsh + bytes(enc)

if len(sys.argv) < 2:
    print(f"Usage: python3.13 {sys.argv[0]} <file to encrypt>")
    exit()

filename = sys.argv[1]
file_data = open(filename, 'rb').read()
enc = encrypt(file_data)

basename = filename.split('.', maxsplit=1)[0]
open(basename + '.enc', 'wb').write(enc)