FROM debian:bookworm-slim

# Install netcat
RUN apt-get update && \
    apt-get install -y socat && \
    rm -rf /var/lib/apt/lists/*

COPY ./incantation /opt/incantation
COPY ./run.sh /opt/serve
RUN chmod +x /opt/incantation && \
    chmod +x /opt/serve

CMD ["socat", "TCP-LISTEN:5757,fork,reuseaddr", "EXEC:/opt/serve"]
