#/bin/bash

source /etc/GPS_config.cfg
# 判断 Test_Flag 是否等于 0
if [ "$Test_Flag" -eq 0 ]; then
    # 如果 Test_Flag 是 0，则执行 sleep 30
    sleep 30
fi




TMP=$(i2cget -y 1 0x57 0x06)
#echo $TMP
#开机看门狗开启并喂狗 Turn on the watchdog and feed the dog
RST=$((0x98 | TMP ))
#echo $RST
#设置最大重启次数 Set the maximum number of restarts
i2cset -y 1 0x57 0x0a 10 
#写入寄存器 Write register
i2cset -y 1 0x57 0x06 $RST 

#该脚本应当设置为开机启动。每次开机只需要运行一次 The script should be set to boot. You only need to run it once per boot