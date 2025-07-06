#!/usr/bin/env python3

import re

validated = {}

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

def validate(data: str) -> bool:
    global validated
    if h(data) in validated:
        return True
    if not re.match(r'^[0-9 \+\-\/\*\.]+$', data):
        print("Invalid input. Only numbers and operators (+, -, /, *, .) are allowed.")
        return False
    validated[h(data)] = True
    return True

def main():
    print("Welcome to my elementary calculator!")
    while True:
        print()
        calc = input("Enter expression to calculate: ").strip()
        if not calc:
            print("Goodbye!")
            break

        if not calc in validated:
            if not validate(calc):
                continue

        try:
            print(eval(calc))
        except Exception as e:
            print(f"Hmm, I haven't learned that yet")


if __name__ == "__main__":
    try:
        main()
    except:
        print("\nGoodbye!")
