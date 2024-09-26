#!/bin/bash
source /etc/GPS_config.cfg
# 判断 Test_Flag 是否等于 0
if [ "$Test_Flag" -eq 0 ]; then
    # 如果 Test_Flag 是 0，则执行 sleep 30
    sleep 30
fi


#设置超时时长10*2s Set timeout duration 10 * 2S
i2cset -y 1 0x57 0x07 10
TMP=$(i2cget -y 1 0x57 0x07)
echo >> /var/log/GPS_NMEA.log
echo "WatchDog 设置超时时长0x57 0x07=$TMP" >> /var/log/GPS_NMEA.log

# 0x57 0x06地址功能为
#bit7-功能开关
#bit5-看门狗复位

#看门狗开启WatchdogOn
TMP=$(i2cget -y 1 0x57 0x06)
echo "Watchdog 0x57 0x06=$TMP" >> /var/log/GPS_NMEA.log
RST=$((0x80 | TMP ))
echo "WatchdogOn RST=$RST" >> /var/log/GPS_NMEA.log
i2cset -y 1 0x57 0x06 $RST
TMP=$(i2cget -y 1 0x57 0x06)
echo "WatchdogOn 0x57 0x06=$TMP" >> /var/log/GPS_NMEA.log
#i2cdump -y 1 0x57
