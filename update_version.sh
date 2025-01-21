#!/bin/bash

pkill -f "python3 APRS_Reporter.py"

i2cset -y 1 0x57 0x06 0x18
#重置pi sugar硬件看门狗

sudo mount -o remount,rw / ; sudo mount -o remount,rw /boot

git reset --hard
git pull origin main


sudo sync ; sudo sync ; sudo sync ; sudo mount -o remount,ro / ; sudo mount -o remount,ro /boot

