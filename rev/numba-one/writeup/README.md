# Numba One

Analyzing the short crackme.py script, we can see we give it a file, it'll read it in, prepend the sha256 hash of it to the buffer, and encrypt it using the encrypt function from the encrypt_module we import.

```python
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
```

encrypt_module is a .so file, which means it was compiled and uses the C API to interface with python.

We can load up an interactive shell to see what functions exist in encrypt_module

```python
>>> import encrypt_module
>>> dir(encrypt_module)
['__doc__', '__file__', '__loader__', '__name__', '__package__', '__spec__', 'encrypt', 'interweave', 'make_key']
```

So along with `encrypt`, we have `interweave` and `make_key`. We can assume they probably have something to do with the encrypt function, so we can open up the module in IDA to see what's going on.

In IDA, we can filter out all the boilerplate functions by searching for `__main__`, and we can see there's 5 functions: `__main__::encrypt[abi:v1][abi:c8tJTC_2fWQMSlLSj2gb4vKgGzNAE_3d]`, `__main__::make_key[abi:v2][abi:c8tJTIeFIjxB2IKSgI4CrvQClQZ6FczSBAA_3d]`, `__main__::interweave[abi:v6][abi:c8tJTIeFIjxB2IKSgI4CrvQClQZ6FczSBAA_3d]`, `__main__::to_arr[abi:v7][abi:c8tJTIeFIjxB2IKSgI4CrvQClQZ6FczSBAA_3d]`, and `__main__::stream[abi:v8][abi:c8tJTIeFIjxB2IKSgI4CrvQClQZ6FczSBAA_3d]`.

Checking out the encrypt function, we can see it calls `make_key` after some setup, and then calls `stream`.

```c
__int64 __fastcall __main__::encrypt[abi:v1][abi:c8tJTC_2fWQMSlLSj2gb4vKgGzNAE_3d](
        __int64 rdi0,
        _QWORD *a2,
        __int64 rdx0,
        __int64 a4,
        __int64 a5,
        __int64 a6)
{
  signed __int64 v9; // rbx
  __int64 v10; // rax
  __int64 v11; // rax
  __int64 v12; // rbp
  __int64 result; // rax
  __int64 v14; // rax
  __int64 v15; // rcx
  __int64 v16; // rdx
  __int128 v17; // rdi
  NRT_MemInfo *v18; // rbx
  __int64 v19; // rcx
  __int64 a3; // [rsp+10h] [rbp-E8h]
  int v22[2]; // [rsp+20h] [rbp-D8h] BYREF
  __int64 v23; // [rsp+28h] [rbp-D0h] BYREF
  int v24[2]; // [rsp+30h] [rbp-C8h]
  __int64 v25; // [rsp+38h] [rbp-C0h]
  __int64 v26; // [rsp+40h] [rbp-B8h]
  int v27[2]; // [rsp+48h] [rbp-B0h]
  NRT_MemInfo *a1[2]; // [rsp+50h] [rbp-A8h] BYREF
  __int128 v29; // [rsp+60h] [rbp-98h]
  __int128 v30; // [rsp+70h] [rbp-88h]
  __int64 v31; // [rsp+80h] [rbp-78h]
  int v32[4]; // [rsp+90h] [rbp-68h] BYREF
  int v33[4]; // [rsp+A0h] [rbp-58h]
  __int128 v34; // [rsp+B0h] [rbp-48h]
  __int64 v35; // [rsp+C0h] [rbp-38h]
  __int64 v36; // [rsp+100h] [rbp+8h]
  signed __int64 size; // [rsp+108h] [rbp+10h]
  __int64 v38; // [rsp+110h] [rbp+18h]

  *(_QWORD *)v27 = a5;
  v23 = 0LL;
  *(_QWORD *)v22 = 0LL;
  NRT_incref(rdx0);
  v9 = size;
  if ( size <= 0 || (v10 = 2LL, v9 = 0LL, (unsigned __int64)size <= 2) )
    v10 = size;
  v11 = v10 - v9;
  v12 = 0LL;
  if ( v11 > 0 )
    v12 = v11;
  NRT_incref(rdx0);
  v34 = 0LL;
  *(_OWORD *)v33 = 0LL;
  *(_OWORD *)v32 = 0LL;
  v35 = 0LL;
  result = __main__::make_key[abi:v2][abi:c8tJTIeFIjxB2IKSgI4CrvQClQZ6FczSBAA_3d](
             (NRT_MemInfo **)v32,
             &v23,
             rdx0,
             a4,
             v12,
             a6,
             (unsigned __int8 *)(v36 + v38 * v9),
             v12,
             v38);
  a3 = *(_QWORD *)v32;
  if ( (_DWORD)result != -2 && (_DWORD)result )
  {
    v19 = v23;
  }
  else
  {
    *(_QWORD *)v24 = v35;
    v25 = *((_QWORD *)&v34 + 1);
    v26 = v34;
    NRT_decref(rdx0);
    v30 = 0LL;
    v29 = 0LL;
    *(_OWORD *)a1 = 0LL;
    v31 = 0LL;
    result = __main__::stream[abi:v8][abi:c8tJTIeFIjxB2IKSgI4CrvQClQZ6FczSBAA_3d](a1, v22, a3);
    if ( (_DWORD)result == -2 || !(_DWORD)result )
    {
      v14 = v31;
      v15 = *((_QWORD *)&v30 + 1);
      v16 = v30;
      v17 = v29;
      v18 = a1[1];
      *(NRT_MemInfo **)rdi0 = a1[0];
      *(_QWORD *)(rdi0 + 8) = v18;
      *(_OWORD *)(rdi0 + 16) = v17;
      *(_QWORD *)(rdi0 + 32) = v16;
      *(_QWORD *)(rdi0 + 40) = v15;
      *(_QWORD *)(rdi0 + 48) = v14;
      NRT_decref(a3);
      NRT_decref(rdx0);
      return 0LL;
    }
    v19 = *(_QWORD *)v22;
  }
  *a2 = v19;
  return result;
}
```

After a bit of debugging and some inferences, we can see that `make_key` is being called with the first 2 bytes of the buffer we give it. Looking into the `stream` function, we can take advantage of the errors being handled by pickle objects which gives us information of what's going on in the more obscure sections of the code. After a bit of debugging and static analysis, we can figure out that it's just regular RC4 encryption.

So at this point, we can recover the original value by brute forcing all possible 2 byte combinations, decrypting, then sha256 hashing the output and checking it against the prepended hash in the encrypted file to see if we have the right decrypted data.

```python
from Crypto.Cipher import ARC4
from hashlib import sha256
import encrypt_module
import numpy as np

with open("flag.enc", "rb") as f:
    data = f.read()

sha_hash = data[:32]
enc_data = data[32:]

for a in range(256):
    for b in range(256):
        d = np.array([a, b], dtype=np.uint8)
        key = encrypt_module.make_key(d)

        ciph = ARC4.new(bytes(key))
        result = ciph.decrypt(enc_data)
        if sha256(result).digest() == sha_hash:
            print("FOUND!", bytes([a,b]))
            with open("flag.bin", "wb") as f:
                f.write(result)
            exit()
```

Upon opening the dumped flag.bin file, we can see that the initial bytes are `TROLLED!`, but the bytes following it looks like PNG data, so we can change that troll header to the actual PNG signature bytes to get the image file with the flag in it.

`cube{python_numba_1}`