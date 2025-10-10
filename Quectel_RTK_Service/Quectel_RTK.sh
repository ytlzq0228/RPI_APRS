#!/bin/bash

CONFIG_FILE='/etc/GPS_config.ini'
# 读取配置函数
get_config() {
  local section=$1 key=$2
  grep -A 50 "^\[$section\]" "$CONFIG_FILE" | \
  grep -m1 "^$key" | \
  awk -F '=' '{print $2}' | \
  sed 's/[;#].*$//' | sed 's/^[ \t]*//;s/[ \t]*$//' | tr -d '\r'
}

if [ $(get_config "RTK_CONFIG" "enable") = "True" ]; then
    python3 /etc/RPI_APRS/Quectel_RTK_Service/Quectel_RTK.py -P $(get_config "RTK_CONFIG" "RTK_PORT") -u $(get_config "RTK_CONFIG" "USERNAME") -p $(get_config "RTK_CONFIG" "PASSWORD") $(get_config "RTK_CONFIG" "NTRIP_SERVER") $(get_config "RTK_CONFIG" "NTRIP_PORT") $(get_config "RTK_CONFIG" "MOUNTPOINT")
fi

