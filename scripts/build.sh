#!/bin/bash

docker stop `docker ps -a -q`
docker system prune -af
docker build -t eyewitness2 .
