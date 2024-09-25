#!/bin/bash
source ~/GPS_config.cfg
#alias rpi-ro='sudo sync ; sudo sync ; sudo sync ; sudo mount -o remount,ro / ; sudo mount -o remount,ro /boot'
#alias rpi-rw='sudo mount -o remount,rw / ; sudo mount -o remount,rw /boot'


# 判断 Test_Flag 是否等于 0
if [ "$Test_Flag" -eq 0 ]; then
    # 如果 Test_Flag 是 0，则执行 sleep 30
    sleep 30
fi

sudo mount -o remount,rw / ; sudo mount -o remount,rw /boot

PROJECT_DIR="/home/pi-star/RPI_APRS"

cd "$PROJECT_DIR" || exit

git reset --hard
git pull origin main

echo "Code pulled on $(date)" >> /var/log/git_pull.log

sudo sync ; sudo sync ; sudo sync ; sudo mount -o remount,ro / ; sudo mount -o remount,ro /boot
echo "$SSID"
python3 GPS_NMEA.py "$Test_Flag" "$SSID" "$Message" #> /var/log/GPS_NMEA.log
