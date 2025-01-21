#!/bin/bash

CONFIG_FILE='/etc/GPS_config.ini'
# 读取配置函数
function get_config() {
    local section=$1
    local key=$2
    grep -A 10 "^\[$section\]" "$CONFIG_FILE" | grep "^$key" | awk -F '=' '{print $2}' | sed 's/^[ \t]*//;s/[ \t]*$//'
}

pkill -f "python3 APRS_Reporter.py"

i2cset -y 1 0x57 0x06 0x18

sudo mount -o remount,rw / ; sudo mount -o remount,rw /boot

git reset --hard
git pull origin main


sudo sync ; sudo sync ; sudo sync ; sudo mount -o remount,ro / ; sudo mount -o remount,ro /boot

