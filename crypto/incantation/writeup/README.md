# Incantation

Author: @B00TK1D

# Description

While walking through a meadow, you find a magical book on the ground.  The letters seem to be dancing off the page, dancing to a rhythm of a song you used to know.

# Solution

The binary provided is a 64-bit ELF executable, packed with UPX (as indicated by the strings in the binary).

Dumping the unpacked binary from memory reveals that it randomly substitutes characters in the flag with other characters.

However, the substitution is flawed because it includes the original character twice in the randomized selection, meaning that capturing a few thousand samples
and performing a frequency analysis on the characters will expose the original flag.
