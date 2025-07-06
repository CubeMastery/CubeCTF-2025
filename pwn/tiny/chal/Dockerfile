FROM ubuntu:20.04

# Install dependencies: build-essential for gcc/make and supervisor for process management.
RUN apt-get update && apt-get install -y supervisor build-essential ncat

# Create the directory for challenge files.
RUN mkdir -p /opt/challenge

# Copy all challenge source files into /opt/challenge.
# (Assuming your challenge source includes a Makefile to build the challenge binary.)
COPY tiny.c /opt/challenge/
COPY tiny /opt/challenge/
COPY *so* /opt/challenge/

# Build the challenge binary using make.
RUN cd /opt/challenge

# Create a new user named "flag".
RUN useradd -m flag

# Copy flag.txt, move it to the root, set its ownership to "flag",
# and restrict permissions so that it is only readable by "flag".
COPY flag.txt /tmp/flag.txt
RUN mv /tmp/flag.txt /flag.txt && \
    chown flag:flag /flag.txt && \
    chmod 400 /flag.txt

# Copy the flag C source, compile it using gcc, move it to /flag,
# change ownership to "flag", and set the SUID bit so that it runs with "flag"'s privileges.
COPY flag.c /tmp/flag.c
RUN gcc -o /tmp/flag_binary /tmp/flag.c && \
    mv /tmp/flag_binary /flag && \
    chown flag:flag /flag && \
    chmod 4755 /flag

# Expose port 9999 for the challenge.
EXPOSE 9999

# Create a Supervisor configuration to automatically start and restart the challenge binary.
RUN echo "[supervisord]\nnodaemon=true\n\n[program:tiny]\ncommand=/opt/challenge/tiny\nuser=nobody\nautostart=true\ndirectory=/opt/challenge\nautorestart=true\nstderr_logfile=/dev/stderr\nstdout_logfile=/dev/stdout" \
    > /etc/supervisor/conf.d/challenge.conf

# Start Supervisor.
CMD ["/usr/bin/supervisord", "-n"]
