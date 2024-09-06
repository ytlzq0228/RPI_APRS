#!/bin/bash

#alias rpi-ro='sudo sync ; sudo sync ; sudo sync ; sudo mount -o remount,ro / ; sudo mount -o remount,ro /boot'
#alias rpi-rw='sudo mount -o remount,rw / ; sudo mount -o remount,rw /boot'

# 等待直到 ifconfig 中发现 tun0,否则git拉不到
while true; do
    if ifconfig | grep -q "tun0"; then
        echo "tun0 接口已找到，继续执行后续操作..."
        break
    else
        echo "等待 tun0 接口..."
        sleep 5  # 每5秒检查一次
    fi
done

sudo mount -o remount,rw / ; sudo mount -o remount,rw /boot

# 定义你的项目路径
PROJECT_DIR="/home/pi-star/RPI_APRS"

# 进入项目目录
cd "$PROJECT_DIR" || exit

# 拉取最新代码
git pull origin main

# 记录拉取操作的时间和结果
echo "Code pulled on $(date)" >> /var/log/git_pull.log

sudo sync ; sudo sync ; sudo sync ; sudo mount -o remount,ro / ; sudo mount -o remount,ro /boot

python3 GPS_NMEA.py #> /var/log/GPS_NMEA.log