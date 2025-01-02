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


# 设置全局的socket超时时间，例如10秒
socket.setdefaulttimeout(5)

CONFIG_FILE='/etc/GPS_config.ini'
LOG_FILE='/var/log/GPS_NMEA.log'
VERSION='0102.02'

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

	# 读取配置文件
	config = configparser.ConfigParser()
	config.read(CONFIG_FILE)

	Test_Flag=config.getboolean('Test_Flag', 'enable')
	SSID=config['SSID_Config']['SSID']
	Message=config['SSID_Config']['Message']
	SSID_ICON=config['SSID_Config']['SSID_ICON']
	OLED_Enable=config.getboolean('OLED_Config', 'OLED_Enable')
	OLED_Address=int(config.get('OLED_Config', 'OLED_Address'), 16)
	GPS_Device=config['GPS_Config']['GPS_Device']
	if GPS_Device[:8]=="/dev/tty":
		GPS_Method="COM"
		com_port=GPS_Device
		baud_rate=config.getint('GPS_Config', 'GPS_Option')
	elif GPS_Device=='GPSd':
		GPS_Method=GPS_Device
	else:
		GPS_Method="TCP"
		tcp_host=GPS_Device
		tcp_port=config.getint('GPS_Config', 'GPS_Option')

	OLED_Enable,oled=OLED.OLED_Init(OLED_Enable,OLED_Address)
	update_time=datetime.min
	update_timestamp=''
	while True:
		try:
			while True:
				try:
					if GPS_Method=="COM":
						lat,lat_dir,lon,lon_dir,altitude,timestamp,speed,course,GNSS_Type,lat_raw,lon_raw,GPS_Source = GNSS_NMAE.Get_GNSS_Position.COM(Test_Flag,com_port,baud_rate)
					if GPS_Method=="TCP":
						lat,lat_dir,lon,lon_dir,altitude,timestamp,speed,course,GNSS_Type,lat_raw,lon_raw,GPS_Source = GNSS_NMAE.Get_GNSS_Position.TCP(Test_Flag,tcp_host,tcp_port)
					if GPS_Method=="GPSd":
						lat,lat_dir,lon,lon_dir,altitude,timestamp,speed,course,GNSS_Type,lat_raw,lon_raw,GPS_Source = GNSS_NMAE.Get_GNSS_Position.GPSd()
					break  # 成功获取GNSS数据时退出循环
				except Exception as err:
					save_log(f"Retrying get_gnss_position due to error: {err}")
					time.sleep(0.1)  # 等待0.1秒后重试
			
			if OLED_Enable:
				try:
					lat_disp=lat_dir+" "+"%08.4f"%(float(lat_raw)/100)
					lon_disp=lon_dir+" "+"%08.4f"%(float(lon_raw)/100)
					if update_time==datetime.min:
						time_diff="00"
					else:
						time_diff="%02.0f"%(datetime.now()-update_time).total_seconds()
					invert=False
					OLED.OLED_Position(oled,lat_disp,lon_disp,GNSS_Type,update_time.strftime('%H:%M:%S'),time_diff,speed,invert)
				except Exception as err:
					save_log(f"main_OLED: {err}")

			if float(timestamp)%10==0:
				save_log(f"gpx:{lat,lat_dir,lon,lon_dir,altitude,timestamp,speed,course}")

			if float(timestamp)%30==0 and timestamp!=update_timestamp:#避免多GPS源的情况下多次上报
				update_timestamp=timestamp
				frame_text=(f'{SSID}>PYTHON,TCPIP*,qAC,{SSID}:!{lat}{lat_dir}/{lon}{lon_dir}{SSID_ICON}{course}/{speed}/A={altitude} APRS by RPI with GNSS Module using {GNSS_Type} at UTC {timestamp} {Message}').encode()
				callsign = b'BI1FQO'
				password = b'20898'
				
				# 定义 APRS 服务器地址和端口（字节形式）
				server_host = b'china.aprs2.net:14580'  # 使用 rotate.aprs2.net 服务器和端口 14580
				
				# 创建 TCP 对象并传入服务器信息
				a = aprs.TCP(callsign, password, servers=[server_host])
				a.start()
				aprs_return=a.send(frame_text)
				if aprs_return==len(frame_text)+2:
					save_log('APRS Report Good Length:%s'%aprs_return)
					update_time=datetime.now()
				else:
					save_log('APRS Report Return:%s Frame Length: %s Retrying..'%(aprs_return,frame_text))
					update_time=datetime.min

		except Exception as err:
			save_log(f"main: {err}")
			#raise
			#切记全部改完了之后这里把raise注释掉


#sudo apt-get update
#sudo apt-get -y upgrade
#sudo apt-get -y install i2c-tools python3-smbus python-smbus
#sudo apt-get -y install python3-pip python3-pil
#sudo pip3 install --upgrade setuptools
#sudo pip3 install --upgrade adafruit-python-shell
#sudo pip3 install adafruit-circuitpython-ssd1306





