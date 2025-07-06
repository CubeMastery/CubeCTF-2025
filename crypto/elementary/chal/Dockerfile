FROM python:3.12 AS app

FROM pwn.red/jail
COPY --from=app / /srv
COPY main.py /srv/app/run
RUN chmod +x /srv/app/run
