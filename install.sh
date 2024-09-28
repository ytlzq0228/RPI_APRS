#!/bin/bash


sudo mount -o remount,rw / ; sudo mount -o remount,rw /boot

PROJECT_DIR="/home/pi-star/RPI_APRS"

cd "$PROJECT_DIR" || exit

git reset --hard
git pull origin main

echo "Code pulled on $(date)" >> /var/log/git_pull.log




sudo apt-get update
#sudo apt-get -y upgrade
sudo apt-get -y install i2c-tools python3-smbus python-sm
sudo apt-get -y install python3-pip python3-pil
sudo pip3 install --upgrade setuptools
sudo pip3 install --upgrade adafruit-python-shell
sudo pip3 install adafruit-circuitpython-ssd1306
sudo pip3 install luma.oled
sudo pip3 install pillow
sudo apt-get -y install libjpeg-dev zlib1g-dev libfreetype6-dev liblcms2-dev libopenjp2-7 libtiff5

sudo apt-get install python3-smbus
sudo pip3 install aprs



cp ./GPS_config.cfg /etc/


sudo sync ; sudo sync ; sudo sync ; sudo mount -o remount,ro / ; sudo mount -o remount,ro /boot