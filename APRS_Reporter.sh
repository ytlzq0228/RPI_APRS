#!/bin/bash

CONFIG_FILE='/etc/GPS_config.ini'
# 读取配置函数
function get_config() {
    local section=$1
    local key=$2
    grep -A 10 "^\[$section\]" "$CONFIG_FILE" | grep "^$key" | awk -F '=' '{print $2}' | sed 's/^[ \t]*//;s/[ \t]*$//'
}
PROJECT_DIR=$(get_config "PROJECT_PATH" "PROJECT_DIR")

i2cset -y 1 0x57 0x06 0x18
#如果存在pi sugar，启用看门狗


cd "$PROJECT_DIR" || exit

if [ $(get_config "OLED_Config" "OLED_Enable") = "True" ]; then
    echo "booting $(date)" >> /var/log/GPS_NMEA.log
    python3 /etc/OLED_Driver/SSD1306_booting.py
fi

# 判断 Test_Flag 是否等于 0
#if [ $(get_config "Test_Flag" "enable") != "True" ]; then
#    # 如果 Test_Flag 是 0，则执行 sleep 30
#    sleep 30
#fi

echo $(get_config "SSID_Config" "SSID")
echo "start python $(date)" >> /var/log/GPS_NMEA.log
python3 APRS_Reporter.py 

