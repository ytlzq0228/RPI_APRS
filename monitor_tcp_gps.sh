#!/bin/bash

CONFIG_FILE='/etc/GPS_config.ini'

# 读取配置函数
function get_config() {
    local section=$1
    local key=$2
    grep -A 10 "^\[$section\]" "$CONFIG_FILE" | grep "^$key" | awk -F '=' '{print $2}' | sed 's/^[ \t]*//;s/[ \t]*$//'
}

# 获取配置文件中的关键值
GPS_DEVICE=$(get_config "GPS_Config" "GPS_Device")
TCP_SOURCE=$(get_config "GPS_Config" "GPSd_TCP_SOURCE")
CHECK_INTERVAL=10  # 每 10 秒检查一次

# 检查 TCP GPS 源是否丢失
check_tcp_source() {
    # 检查 gpspipe 的实时输出是否包含 TCP_SOURCE
    if ! gpspipe -w -n 10 | grep -q "\"device\":\"$TCP_SOURCE\""; then
        echo "$(date): 检测到 TCP GPS 源丢失，尝试重新添加..."
        gpsdctl add "$TCP_SOURCE" || echo "$(date): 无法重新添加 TCP GPS 源，请检查网络或 GPSD 配置。"
    else
        echo "$(date): TCP GPS 源正常。"
    fi
}

# 检查是否需要监控
if [[ "$GPS_DEVICE" == "GPSd" && -n "$TCP_SOURCE" ]]; then
    echo "$(date): 配置文件指示使用 GPSd 并配置了 TCP 源 $TCP_SOURCE。开始监控..."
    while true; do
        check_tcp_source
        sleep "$CHECK_INTERVAL"
    done
else
    echo "$(date): 配置文件未指示使用 GPSd 或未配置 TCP 源。无需监控。"
    exit 0
fi