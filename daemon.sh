#!/bin/bash

#usage: nohup ./daemon.sh &

#exit: killall -g daemon.sh

while [ 1 ]; do
    python himawari8downloader.py
    sleep 60 # 5 min
done
