FROM alpine AS app
RUN apk add nasm

FROM pwn.red/jail
COPY --from=app / /srv
COPY chal.sh /srv/app/run
RUN chmod +x /srv/app/run
