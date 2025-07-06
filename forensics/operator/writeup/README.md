# Operator
Author: @B00TK1D

I think someone has been hiding secrets on my server. Can you find them?


# Writeup

This challenge provided a pcap containing a plaintext C2 connection to a server (in tcp stream 1), which was used to then trigger a netcat transfer of a binary to the server and execute that binary (in tcp stream 7).

The binary can be extracted using wireshark through a number of methods, such as displaying the stream as "raw" and then clicking "save as...".

The binary is a 64-bit ELF file, which can be inspected using a decompiler such as Ghidra.

Looking at the binary in ghidra reveals that it is performing a basic XOR encryption on data passed over a network socket, and has a hardcoded key:

```
0x040717764269b00bde1823221eedf7ae
```

This key can then be used to decrypt the data sent over the encrypted connection.

Because the binary encrypts each line sent on its own, initially only the first line of data successfully decrypts with the key (due to padding issues), but by decrypting each line separately, the flag is shown in the 6th line of stream 29:

```
cube{c00l_0p3r4t0rs_us3_mult1_st4g3_p4yl04ds_8ab49338}
```

