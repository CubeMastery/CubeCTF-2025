#!/bin/sh

rm /var/run/docker.pid
dockerd -H unix:///var/run/docker.sock -H tcp://0.0.0.0:2375&
while ! docker info >/dev/null 2>&1; do sleep 1; done
docker compose build
docker compose up
