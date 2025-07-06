#!/bin/sh

cd /tmp

echo "Please enter the assembly code (up to 100 lines). End with an empty line:"
asm_code=""
while IFS= read -r line && [ "$line" != "" ] && [ $(echo "$asm_code" | wc -l) -lt 100 ]; do
    asm_code="$asm_code$line\n"
done

echo -e "$asm_code" > asm_code.asm
nasm -f bin asm_code.asm -o forward.bin

if [ $? -ne 0 ]; then
    echo "Compilation failed."
    exit 1
fi

rev forward.bin | tac > reversed.bin

chmod +x forward.bin reversed.bin

forward=$(./forward.bin)
reversed=$(./reversed.bin)

if [ "$forward" = "$reversed" ]; then
    echo $forward
fi

echo "Done!"
