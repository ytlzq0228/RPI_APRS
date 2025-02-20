#!/bin/bash

CONFIG_FILE='/etc/GPS_config.ini'
# 读取配置函数
function get_config() {
    local section=$1
    local key=$2
    grep -A 10 "^\[$section\]" "$CONFIG_FILE" | grep "^$key" | awk -F '=' '{print $2}' | sed 's/^[ \t]*//;s/[ \t]*$//'
}

python3 /etc/RPI_APRS/RTK_Service.py -u $(get_config "RTK_CONFIG" "USERNAME") -p $(get_config "RTK_CONFIG" "PASSWORD") $(get_config "RTK_CONFIG" "NTRIP_SERVER") $(get_config "RTK_CONFIG" "NTRIP_PORT") $(get_config "RTK_CONFIG" "MOUNTPOINT")
