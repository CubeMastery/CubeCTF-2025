# gnisrever

Normally you get a binary and have to reverse engineer it.  That sounds like a lot of work.  Instead, ths time you give us a binary and we do the reversing for you.

Author: @B00TK1D

# Solution

The easiest way to solve this is to just make nasm write a bash script instead of a binary.  Including an `exit` and reversing the script in the second half means it can run forward or backward:

```asm
db '#!/bin/sh', 10
db 'echo $FLAG', 10
db 'exit', 10
db 'tixe', 10
db 'GALF$ ohce', 10
db 'hs/nib/!#', 10
```

There are probably much more complicated ways to do this using proper assembly and carefully crafted instructions, but those are not necessary to solve this challenge.
