#!/usr/bin/env python3

import re
import random

def h(data: str) -> bytes:
    b = data.encode('utf-8')

    h1 = 0x1234567890ab
    h2 = 0xfedcba098765

    for i in range(len(b)):
        byte = b[i]
        shift = (i % 6) * 6

        if i % 2 == 0:
            h1 ^= (byte << shift)
            h1 = (h1 * 0x100000001b3) & 0xFFFFFFFFFFFF
        else:
            h2 ^= (byte << shift)
            h2 = (h2 * 0xc6a4a7935bd1) & 0xFFFFFFFFFFFF

    result = h1 ^ ((h2 << 24) | (h2 >> 24))
    result = (result ^ (result >> 25)) * 0xff51afd7ed55
    result &= 0xFFFFFFFFFFFFFFFF
    result = (result ^ (result >> 25)) * 0xc4ceb9fe1a85
    result &= 0xFFFFFFFFFFFFFFFF
    result ^= result >> 25

    return result.to_bytes(8, 'big')[:6]

def attack():
    bad_hashes = {}
    good_hashes = {}

    bad_base = "__import__('os').environ['FLAG'] #"
    good_base = ""

    while True:
        i = random.randint(0, 2**48)
        bad = bad_base + str(i)
        good = good_base + str(i)

        bad_hash = h(bad)
        good_hash = h(good)

        if bad_hash in good_hashes:
            print(f"Found collision: {bad} -> {good_base}{good_hashes[bad_hash]}")
            print(f"Hash: {bad_hash.hex()}")
            break

        if good_hash in bad_hashes:
            print(f"Found collision: {bad_base}{bad_hashes[good_hash]} -> {good}")
            print(f"Hash: {good_hash.hex()}")
            break

        bad_hashes[bad_hash] = i
        good_hashes[good_hash] = i

        if i % 100000 == 0:
            print(f"Checked {i} hashes...")
            print(f"Bad hash: {bad_hash.hex()}")
            print(f"Good hash: {good_hash.hex()}")

        i += 1

if __name__ == "__main__":
    attack()
