all:
	gcc vuln.c -o vuln -no-pie -fno-stack-protector
	patchelf --set-interpreter ./ld-linux-x86-64.so.2 \
	         --replace-needed libc.so.6 ./libc.so.6 \
	         ./vuln
	zip player.zip Dockerfile \
	               Makefile \
	               docker-compose.yml \
	               ld-linux-x86-64.so.2 \
	               libc.so.6 \
	               run.sh \
	               vuln.c \
	               vuln
	zip admin.zip Dockerfile \
	              Makefile \
	              README.md \
	              docker-compose.yml \
	              ld-linux-x86-64.so.2 \
	              libc.so.6 \
	              run.sh \
	              vuln.c \
	              vuln \
	              flag.txt \
	              solve.py \
	              player.zip

clean:
	rm vuln
	rm admin.zip
	rm player.zip
