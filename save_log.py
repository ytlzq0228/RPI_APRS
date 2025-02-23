import sys
import os
import time
import configparser
from datetime import datetime

# 读取配置文件
CONFIG_FILE='/etc/GPS_config.ini'
config = configparser.ConfigParser()
config.read(CONFIG_FILE)

LOG_FILE_PATH=config['SFTP_Config']['LOCAL_LOG_FILE_PATH']
SSID=config['SSID_Config']['SSID']
LOG_FILE = f"{datetime.now().strftime('%Y-%m-%d')}-{LOG_FILE_PATH}-{SSID}"


def save_log(result):
	try:
		print(result)
		now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
		f = open(LOG_FILE,'a')
		f.writelines("\n%s log:%s" %(now,VERSION,result))
		f.flush()
		f.close()
	except Exception as err:
		print(err)