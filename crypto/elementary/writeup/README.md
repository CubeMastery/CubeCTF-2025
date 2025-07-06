# Elementary
Author: @B00TK1D

I made a calculator for elementary students.  I made sure it can only do basic operations, so it should be safe.

# Writeup

Solving this requires creating a hash collision between an allowed input and a blocked input.  If the allowed input is sent first, it's hash is saved as valid, allowing the otherwise bad input to be run.
Because the hash is 6 bytes long, it is unlikely that players will be able to find a collision with a specific chosen plaintext, but by using a meet in the middle attack (storing a large list of generated hashes),
it is reasonble to find a collision between an allowed and bad input.
