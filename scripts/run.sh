#!/bin/bash

docker run --network host \
  -it \
  -v `pwd`/logs:/usr/src/app/logs \
  -v `pwd`/results:/usr/src/app/results \
  eyewitness2 $@
