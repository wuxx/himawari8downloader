#!/bin/bash

#usage: nohup ./daemon.sh &

#exit: killall -g daemon.sh

while [ 1 ]; do
    #python himawari8downloader.py
    python get_all.py
    sleep 300 # 5 min
done
