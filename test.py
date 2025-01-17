import sys
import os
import time
import re
import serial
import configparser
import aprs
from datetime import datetime
import socket
from Display import OLED
from watchdog import reset_watchdog
from watchdog import boot_watchdog
import GNSS_NMAE
from Radio_GPIO import read_gpio


# 设置全局的socket超时时间，例如10秒
socket.setdefaulttimeout(5)

CONFIG_FILE='/etc/GPS_config.ini'
LOG_FILE='/var/log/GPS_NMEA.log'
VERSION='main_0117.01'
Radio_ENABLE_PIN=33

def save_log(result):
    try:
        print(result)
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        f = open(LOG_FILE,'a')
        f.writelines("\n%s ver %s log:%s" %(now,VERSION,result))
        f.flush()
        f.close()
    except Exception as err:
        print(err)



if __name__ == '__main__':
    print(read_gpio(Radio_ENABLE_PIN))

#sudo apt-get update
#sudo apt-get -y upgrade
#sudo apt-get -y install i2c-tools python3-smbus python-smbus
#sudo apt-get -y install python3-pip python3-pil
#sudo pip3 install --upgrade setuptools
#sudo pip3 install --upgrade adafruit-python-shell
#sudo pip3 install adafruit-circuitpython-ssd1306





