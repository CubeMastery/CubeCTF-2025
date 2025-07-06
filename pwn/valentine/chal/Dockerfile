FROM ubuntu:22.04 as base

WORKDIR /app
COPY vuln run
COPY libc.so.6 libc.so.6
COPY ld-linux-x86-64.so.2 ld-linux-x86-64.so.2
RUN chmod +x *
COPY flag.txt /flag.txt
RUN mv /flag.txt /flag-$(md5sum /flag.txt | awk '{print $1}').txt

FROM pwn.red/jail
COPY --from=base / /srv

ENV JAIL_TIME=600 JAIL_CPU=100 JAIL_MEM=10M
