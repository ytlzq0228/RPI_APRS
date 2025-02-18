import sys
import os
import time
import re
import serial
import json
import subprocess
import configparser
from gps3 import gps3
from datetime import datetime
import socket

from Display import OLED

from watchdog import reset_watchdog

# 设置全局的socket超时时间，例如10秒
socket.setdefaulttimeout(5)

CONFIG_FILE='/etc/GPS_config.ini'
VERSION='NMEA_0218.01'

# 读取配置文件
config = configparser.ConfigParser()
config.read(CONFIG_FILE)

LOG_FILE=config['SFTP_Config']['LOCAL_LOG_FILE_PATH']

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

class NMEA_Processing:
	def NMEA_GGA(sentence,timestamp):
		match=re.match(r'^\$..GGA,.*', sentence)  # 匹配GPGGA语句
		if match:
			parts=sentence.split(',')
			if len(parts) > 9 and parts[2] and parts[4] and parts[9]:
				lat=float(parts[2])
				lon=float(parts[4])
				lat_dir=parts[3]
				lon_dir=parts[5]
				altitude=float(parts[9]) #NMEA协议海拔数据单位米/NMEA protocol altitude data in meters.
				altitude=altitude*3.28 #APRS报文海拔数据单位英尺，米转英尺/APRS message altitude data is in feet; convert meters to feet.
				lat_dd="%.2f"%lat
				lon_dd="%.2f"%lon
				altitude="%06.0f"%altitude
				GNSS_Type=parts[0].replace("$","")
				#if float(timestamp)%10==0 and timestamp!=0:
				#	save_log(sentence)
				return altitude
			else:
				print("No %s Signal. Waiting....."%parts[0])
		return None

	def NMEA_RMC(sentence):
		match=re.match(r'^\$..RMC,.*', sentence)  # 匹配GPRMC语句
		if match:
			reset_watchdog()
			#喂狗
			parts=sentence.split(',')
			#print(parts)
			if len(parts) > 8 and parts[3] and parts[5]:
				lat_raw=float(parts[3])
				lon_raw=float(parts[5])
				lat_dir=parts[4]
				lon_dir=parts[6]
				lat_dd="%.2f"%lat_raw
				lon_dd="%.2f"%lon_raw
				GNSS_Type=parts[0].replace("$","")
				if parts[7]=='':
					speed="%03.0f"%0
				else:
					speed="%03.0f"%float(parts[7]) #NMEA APRS速度数据单位均为海里每小时/The speed data unit for both NMEA and APRS is knots, no conversion needed.
				if parts[8]=='':
					course="%03.0f"%180
				else:
					course="%03.0f"%float(parts[8]) #NMEA APRS航向数据单位均为度/The course data unit for both NMEA and APRS is degrees, no conversion needed.
				timestamp=parts[1]
				#if float(timestamp)%10==0 and timestamp!=0:
				#	save_log(sentence)
				return lat_dd,lat_dir,lon_dd,lon_dir,speed,course,timestamp,GNSS_Type,lat_raw,lon_raw
			else:
				print("No %s Signal. Waiting....."%parts[0])
				return None,None,None,None,None,None,0,None,None,None
		return None,None,None,None,None,None,None,None,None,None


class Get_GNSS_Position:

	def COM(Test_Flag,com_port,baud_rate):
		"""直读本地串口获取数据"""
		try:
			ser = serial.Serial(com_port, baud_rate, bytesize=serial.EIGHTBITS, parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE)
			print(com_port, baud_rate)
			ser.reset_input_buffer()
			i=0
			while True:
				if ser.in_waiting > 0:
					line=ser.readline().decode('ascii', errors='replace').strip()  # 读取一行NMEA数据
					if Test_Flag:
						line='$GPRMC,%s,A,4104.6300,N,10618.2178,E,010.4,084.4,230394,003.1,W*6A'%datetime.now().strftime('%H%M%S') #for testing
					lat,lat_dir,lon,lon_dir,speed,course,timestamp,GNSS_Type,lat_raw,lon_raw=NMEA_Processing.NMEA_RMC(line)
					if lat is not None and lon is not None :
						i=0
						#save_log(f"GNSS GGA: lat={lat}, lon={lon}, altitude/feet={altitude}")
						break
					if timestamp==0:
						i+=1
						if OLED_Enable==1:
							try:
								OLED.OLED_Display(oled,'No GNSS Signal Yet')
							except Exception as err:
								save_log(f"No GNSS_OLED: {err}")
					if timestamp==0 and i%60==1:
						save_log('No GNSS Signal. Waiting.....')
					i=i%3600
				
			i=0
			while i<120:
				if ser.in_waiting > 0:  
					line=ser.readline().decode('ascii', errors='replace').strip()  # 读取一行NMEA数据
					if Test_Flag:
						line='$GPGGA,%s,4104.6300,N,10618.2178,E,01,07,10.3,20.05,M,-15.40,M,1.1,1023*63<CR><LF>'%datetime.now().strftime('%H%M%S') #for testing
					altitude=NMEA_Processing.NMEA_GGA(line,timestamp)
					if altitude :
						#save_log(f"GNSS RMC: speed/knots={speed}, course={course}")
						break
					i+=1
			GPS_Source=com_port
			return lat,lat_dir,lon,lon_dir,altitude,timestamp,speed,course,GNSS_Type,lat_raw,lon_raw,GPS_Source
		except Exception as err:
			save_log(f"get_gnss_position_COM: {err}")
	
	def TCP(Test_Flag,tcp_host,tcp_port):
		"""通过TCP Server获取数据"""
		try:
			# TCP 初始化
			sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			sock.connect((tcp_host, tcp_port))
			sock.settimeout(2)  # 设置超时时间
	
			i = 0
			line=""
			while True:
				if Test_Flag:
					line_RMC = '$GPRMC,%s,A,4104.6300,N,10618.2178,E,010.4,084.4,230394,003.1,W*6A' % datetime.now().strftime('%H%M%S')  # for testing
					line_GGA = '$GPGGA,%s,4104.6300,N,10618.2178,E,01,07,10.3,20.05,M,-15.40,M,1.1,1023*63<CR><LF>' % datetime.now().strftime('%H%M%S')  # for testing
				else:
					try:
						line = sock.recv(1024).decode('utf-8').split()
					except Exception as err:
						save_log("TCP connection timed out.%s"%err)
					if len(line)==0:
						break
					line_RMC =""
					line_GGA =""
					for i in line:
						if i[3:6]=="RMC":
							line_RMC=i
						if i[3:6]=="GGA":
							line_GGA=i
				lat, lat_dir, lon, lon_dir, speed, course, timestamp, GNSS_Type, lat_raw, lon_raw = NMEA_Processing.NMEA_RMC(line_RMC)
				altitude = NMEA_Processing.NMEA_GGA(line_GGA, timestamp)
	
				if lat is not None and lon is not None:
					i = 0
					GPS_Source="tcp://%s:%s"%(tcp_host,tcp_port)
					return lat,lat_dir,lon,lon_dir,altitude,timestamp,speed,course,GNSS_Type,lat_raw,lon_raw,GPS_Source
					break
				if timestamp == 0:
					i += 1
					if OLED_Enable == 1:
						try:
							OLED.OLED_Display(oled, 'No GNSS Signal Yet')
						except Exception as err:
							save_log(f"No GNSS_OLED: {err}")
					if i % 60 == 1:
						save_log('No GNSS Signal. Waiting.....')
					i = i % 3600
	
	
			sock.close()
	
	
		except Exception as err:
			save_log(f"get_gnss_position_TCP: {err}")


	def GPSd(altitude,speed,course):
		"""通过 gps3 获取 GPS 数据"""
		gps_socket = gps3.GPSDSocket()
		data_stream = gps3.DataStream()
		# 连接到 GPSd
		gps_socket.connect(host="127.0.0.1", port=2947)
		gps_socket.watch()
		
		try:
			retyr_time=0
			for new_data in gps_socket:
				retyr_time+=1
				if retyr_time>6000:
					save_log('GPSd no GNSS Signal in 60s')
					return
				if new_data:
					data=json.loads(new_data)
					data_stream.unpack(new_data)
					if data['class']=='TPV':
						#save_log(f"GPSd TPV data: {new_data}")##-------------------------testing log------------------
						if int(data['mode'])>2:
							#data['lat']和data['lon']使用十进制度，NMEA和APRS使用十进制分
							# 纬度转换
							decimal_lat=float(data['lat'])
							lat_dir = "N" if decimal_lat >= 0 else "S"  # 北纬为 N，南纬为 S
							lat_abs = abs(decimal_lat)
							lat_degrees = int(lat_abs)
							lat_minutes = (lat_abs - lat_degrees) * 60
							

							# 经度转换
							decimal_lon=float(data['lon'])
							lon_dir = "E" if decimal_lon >= 0 else "W"  # 东经为 E，西经为 W
							lon_abs = abs(decimal_lon)
							lon_degrees = int(lon_abs)
							lon_minutes = (lon_abs - lon_degrees) * 60

							# 格式化为 APRS 格式
							lat = f"{lat_degrees:02d}{lat_minutes:05.2f}"
							lon = f"{lon_degrees:03d}{lon_minutes:05.2f}"

							# 格式化为 NMEA 格式，高精度
							lat_raw= f"{lat_degrees:02d}{lat_minutes:09.6f}"
							lon_raw= f"{lon_degrees:03d}{lon_minutes:09.6f}"

							altitude="%06.0f"%(float(data['alt'])*3.28) if 'alt' in data else altitude#APRS报文海拔数据单位英尺，米转英尺/APRS message altitude data is in feet; convert meters to feet.
							
							timestamp = datetime.strptime(data['time'], "%Y-%m-%dT%H:%M:%S.%fZ").strftime("%H%M%S.00") if 'time' in data else '000000.00'#时间戳"2025-01-02T09:01:10.000Z"转为NMEA语句格式的时间戳090110.00
							
							speed="%03.0f"%(float(data['speed'])*3600/1852) if 'speed' in data else speed#NMEA APRS速度数据单位均为海里每小时，GPSd报告的为米/秒。/The speed data unit for both NMEA and APRS is knots, no conversion needed.
							
							course="%03.0f"%float(data['track']) if 'track' in data else course

							GNSS_Type='TPV'

							GPS_Source="GPSd_Device:%s"%data['device']
							if lat and lon:
								return lat,lat_dir,lon,lon_dir,altitude,timestamp,speed,course,GNSS_Type,lat_raw,lon_raw,GPS_Source
									  #4004.83 N 11619.38 E    000211   092344.00 000   066    GPRMC     4004.829687 11619.375852
				time.sleep(0.01)
		except Exception as e:
			save_log(f"Error fetching GPSd data: {e}")


def add_gps_source(source):
	"""通过 gpsdctl 动态添加 GPS 源"""
	retyr_time=0
	max_retry=30
	while retyr_time<max_retry:
		try:
			retyr_time+=1
			subprocess.run(['gpsdctl', 'add', source], check=True,timeout=5)
			save_log(f"Successfully added GPS source: {source}")
			break
		except subprocess.CalledProcessError as e:
			save_log(f"Failed to add GPS source: {source}.Retry{retyr_time}/{max_retry} Error: {e}")
			time.sleep(1)
		except Exception as e:
			save_log(f"Failed to add GPS source: {source}.Retry{retyr_time}/{max_retry} Error: {e}")
			time.sleep(1)
