#!/bin/bash


mount -o remount,rw / ; sudo mount -o remount,rw /boot


git reset --hard
git pull origin main

echo "Code pulled on $(date)"

cp ./GPS_config.ini /etc/
mkdir /etc/RPI_APRS
cp * /etc/RPI_APRS
bash -c 'crontab -u root -l 2>/dev/null | grep -q "@reboot /etc/RPI_APRS/APRS_Reporter.sh" || (crontab -u root -l 2>/dev/null; echo "@reboot /etc/RPI_APRS/APRS_Reporter.sh") | crontab -u root -'

apt-get update
apt-get -y install i2c-tools python3-smbus python-sm python3-pip python3-pil libjpeg-dev zlib1g-dev libfreetype6-dev liblcms2-dev libopenjp2-7 libtiff5 gpsd
pip3 install --upgrade setuptools
pip3 install adafruit-circuitpython-ssd1306 adafruit-python-shell luma.oled pillow gps3 aprs
#安装必要依赖

sync ; sudo sync ; sudo sync ; sudo mount -o remount,ro / ; sudo mount -o remount,ro /boot


