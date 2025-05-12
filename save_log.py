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



def save_log(result):
	try:
		print(result)
		now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
		LOG_FILE = f"{LOG_FILE_PATH}/{datetime.now().strftime('%Y-%m-%d')}-GPS-{SSID}.log"
		f = open(LOG_FILE,'a')
		f.writelines("\n%s log:%s" %(now,result))
		f.flush()
		f.close()
	except Exception as err:
		print(err)