#!/bin/bash

CONFIG_FILE='/etc/GPS_config.ini'
# 读取配置函数
function get_config() {
    local section=$1
    local key=$2
    grep -A 10 "^\[$section\]" "$CONFIG_FILE" | grep "^$key" | awk -F '=' '{print $2}' | sed 's/^[ \t]*//;s/[ \t]*$//'
}

i2cset -y 1 0x57 0x06 0x18

sudo mount -o remount,rw / ; sudo mount -o remount,rw /boot

PROJECT_DIR="/home/pi-star/RPI_APRS"

cd "$PROJECT_DIR" || exit

if [ $(get_config "OLED_Config" "OLED_Enable") = "True" ]; then
    echo "booting $(date)" >> /var/log/git_pull.log
    python3 SSD1306_booting.py
fi

# 判断 Test_Flag 是否等于 0
if [ $(get_config "Test_Flag" "enable") = "True" ]; then
    # 如果 Test_Flag 是 0，则执行 sleep 30
    sleep 5
fi

git reset --hard
git pull origin main

echo "Code pulled on $(date)" >> /var/log/git_pull.log

sudo sync ; sudo sync ; sudo sync ; sudo mount -o remount,ro / ; sudo mount -o remount,ro /boot
echo $(get_config "SSID_Config" "SSID")
python3 APRS_Reporter.py 
gpsdctl add tcp://10.0.6.116:12321
