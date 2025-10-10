#!/bin/bash

CONFIG_FILE='/etc/GPS_config.ini'
# 读取配置函数
function get_config() {
  local section=$1 key=$2
  awk -v s="$section" -v k="$key" '
    $0 ~ "^[ \t]*\\[" s "\\][ \t]*$" {in=1; next}
    in && $0 ~ "^[ \t]*\\[" {in=0}
    in {
      # 去掉注释
      sub(/[;#].*$/, "", $0)
      if ($0 ~ "^[ \t]*" k "[ \t]*=") {
        sub("^[ \t]*" k "[ \t]*=[ \t]*", "", $0)
        gsub(/^[ \t"]+|[ \t"]+$/, "", $0)
        print; exit
      }
    }
  ' "$CONFIG_FILE" | tr -d '\r'
}

if [ $(get_config "RTK_CONFIG" "enable") = "True" ]; then
    python3 /etc/RPI_APRS/Quectel_RTK_Service/Quectel_RTK.py -P $(get_config "RTK_CONFIG" "RTK_PORT") -u $(get_config "RTK_CONFIG" "USERNAME") -p $(get_config "RTK_CONFIG" "PASSWORD") $(get_config "RTK_CONFIG" "NTRIP_SERVER") $(get_config "RTK_CONFIG" "NTRIP_PORT") $(get_config "RTK_CONFIG" "MOUNTPOINT")
fi

