#!/bin/bash
source /etc/GPS_config.cfg
#alias rpi-ro='sudo sync ; sudo sync ; sudo sync ; sudo mount -o remount,ro / ; sudo mount -o remount,ro /boot'
#alias rpi-rw='sudo mount -o remount,rw / ; sudo mount -o remount,rw /boot'

i2cset -y 1 0x57 0x06 0x18

sudo mount -o remount,rw / ; sudo mount -o remount,rw /boot

PROJECT_DIR="/home/pi-star/RPI_APRS"

cd "$PROJECT_DIR" || exit

if [ "$OLED_Enable" -eq 1 ]; then
    echo "booting $(date)" >> /var/log/git_pull.log
    python3 SSD1306_booting.py
fi

# 判断 Test_Flag 是否等于 0
if [ "$Test_Flag" -eq 0 ]; then
    # 如果 Test_Flag 是 0，则执行 sleep 30
    sleep 30
fi

git reset --hard
git pull origin main

echo "Code pulled on $(date)" >> /var/log/git_pull.log

sudo sync ; sudo sync ; sudo sync ; sudo mount -o remount,ro / ; sudo mount -o remount,ro /boot
echo "$SSID"
python3 GPS_NMEA.py "$Test_Flag" "$SSID" "$Message" "$SSID_ICON" "$OLED_Enable" "$OLED_Address" 
