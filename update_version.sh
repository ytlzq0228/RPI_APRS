#!/bin/bash

pkill -f "python3 APRS_Reporter.py"

i2cset -y 1 0x57 0x06 0x18
#关闭pi sugar硬件看门狗

mount -o remount,rw / ; sudo mount -o remount,rw /boot

git reset --hard
git pull origin main
echo "Code pulled on $(date)"
cp -r * /etc/RPI_APRS
echo "Copy to /etc finished"

systemctl restart aprs_reporter.service

sync ; sudo sync ; sudo sync ; sudo mount -o remount,ro / ; sudo mount -o remount,ro /boot

