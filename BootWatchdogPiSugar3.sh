#!/bin/bash
source /etc/GPS_config.cfg
## 判断 Test_Flag 是否等于 0
#if [ "$Test_Flag" -eq 0 ]; then
#    # 如果 Test_Flag 是 0，则执行 sleep 30
#    sleep 60
#fi

#设置最大重启次数 Set the maximum number of restarts
i2cset -y 1 0x57 0x0a 10 
TMP=$(i2cget -y 1 0x57 0x0a)
echo "设置最大重启次数0x57 0x0a=$TMP" >> /var/log/GPS_NMEA.log

#设置超时时长10*2s Set timeout duration 10 * 2S
i2cset -y 1 0x57 0x07 10
TMP=$(i2cget -y 1 0x57 0x07)
echo "设置超时时长0x57 0x07=$TMP" >> /var/log/GPS_NMEA.log


# 0x57 0x06地址为
#bit7-功能开关
#bit5-看门狗复位

#看门狗开启WatchdogOn
TMP=$(i2cget -y 1 0x57 0x06)
echo "0x57 0x06=$TMP" >> /var/log/GPS_NMEA.log
RST=$((0x80 | TMP ))
echo "RST=$RST" >> /var/log/GPS_NMEA.log
i2cset -y 1 0x57 0x06 $RST
TMP=$(i2cget -y 1 0x57 0x06)
echo "0x57 0x06=$TMP" >> /var/log/GPS_NMEA.log
#i2cdump -y 1 0x57
