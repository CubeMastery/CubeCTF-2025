FROM python:3.13-slim-bookworm

# Fix apt on apple silicon
RUN echo "Acquire::http::Pipeline-Depth 0;" > /etc/apt/apt.conf.d/99custom && \
    echo "Acquire::http::No-Cache true;" >> /etc/apt/apt.conf.d/99custom && \
    echo "Acquire::BrokenProxy    true;" >> /etc/apt/apt.conf.d/99custom

RUN apt-get update && apt-get install -y --no-install-recommends socat curl && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

RUN useradd -m prisoner
USER prisoner

WORKDIR /solitary

COPY solitary/server.py .

EXPOSE 5005

CMD socat -v TCP-LISTEN:5005,fork EXEC:"python3 server.py"
