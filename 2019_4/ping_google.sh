#!/bin/bash
TARGET="8.8.8.8"
ping -I wlan0 $TARGET -c 1 > /dev/null 2>&1 && echo [+] ping $TARGET was succussful || echo [-] Error: ping to $TARGET was **NOT** successful
TARGET="www.google.com"
ping -I wlan0 www.google.com -c 1 > /dev/null 2>&1 && echo [+] ping $TARGET was succussful || echo [-] Error: ping to $TARGET was **NOT** successful