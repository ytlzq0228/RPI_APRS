import sys
import os
import time
import re
import serial
import json
from gps3 import gps3
from datetime import datetime
import socket

from Display import OLED

from watchdog import reset_watchdog

# 设置全局的socket超时时间，例如10秒
socket.setdefaulttimeout(5)


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
				if float(timestamp)%10==0 and timestamp!=0:
					save_log(sentence)
				return altitude
			else:
				print("No %s Signal. Waiting....."%parts[0])
		return None

	def NMEA_RMC(sentence):
		match=re.match(r'^\$..RMC,.*', sentence)  # 匹配GPRMC语句
		if match:
			reset_watchdog()
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
				if float(timestamp)%10==0 and timestamp!=0:
					save_log(sentence)
				return lat_dd,lat_dir,lon_dd,lon_dir,speed,course,timestamp,GNSS_Type,lat_raw,lon_raw
			else:
				print("No %s Signal. Waiting....."%parts[0])
				return None,None,None,None,None,None,0,None,None,None
		return None,None,None,None,None,None,None,None,None,None


class Get_GNSS_Position:

	def COM(Test_Flag,com_port,baud_rate):
		try:
			ser = serial.Serial(com_port, baud_rate, bytesize=serial.EIGHTBITS, parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE)
			print(com_port, baud_rate)
			ser.reset_input_buffer()
			i=0
			while True:
				if ser.in_waiting > 0:
					line=ser.readline().decode('ascii', errors='replace').strip()  # 读取一行NMEA数据
					if Test_Flag:
						line='$GPRMC,%s,A,4004.6300,N,11618.2178,E,010.4,084.4,230394,003.1,W*6A'%datetime.now().strftime('%H%M%S') #for testing
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
						line='$GPGGA,%s,4004.6300,N,11618.2178,E,01,07,10.3,20.05,M,-15.40,M,1.1,1023*63<CR><LF>'%datetime.now().strftime('%H%M%S') #for testing
					altitude=NMEA_Processing.NMEA_GGA(line,timestamp)
					if altitude :
						#save_log(f"GNSS RMC: speed/knots={speed}, course={course}")
						break
					i+=1
			return lat,lat_dir,lon,lon_dir,altitude,timestamp,speed,course,GNSS_Type,lat_raw,lon_raw
		except Exception as err:
			save_log(f"get_gnss_position_COM: {err}")
			raise
	
	def TCP(Test_Flag,tcp_host,tcp_port):
		try:
			# TCP 初始化
			sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			sock.connect((tcp_host, tcp_port))
			sock.settimeout(2)  # 设置超时时间
	
			i = 0
			line=""
			while True:
				if Test_Flag:
					line_RMC = '$GPRMC,%s,A,4004.6300,N,11618.2178,E,010.4,084.4,230394,003.1,W*6A' % datetime.now().strftime('%H%M%S')  # for testing
					line_GGA = '$GPGGA,%s,4004.6300,N,11618.2178,E,01,07,10.3,20.05,M,-15.40,M,1.1,1023*63<CR><LF>' % datetime.now().strftime('%H%M%S')  # for testing
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
				print(lat,lat_dir,lon,lon_dir,altitude,timestamp,speed,course,GNSS_Type,lat_raw,lon_raw)
	
				if lat is not None and lon is not None:
					i = 0
					return lat,lat_dir,lon,lon_dir,altitude,timestamp,speed,course,GNSS_Type,lat_raw,lon_raw
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
			raise


	def GPSd(Test_Flag,tcp_host,tcp_port):
		"""通过 gps3 获取 GPS 数据"""
		gps_socket = gps3.GPSDSocket()
		data_stream = gps3.DataStream()
		# 连接到 GPSd
		gps_socket.connect(host="127.0.0.1", port=2947)
		gps_socket.watch()
		
		try:
			for new_data in gps_socket:
				if new_data:
					print(new_data)
					data=json.loads(new_data)
					data_stream.unpack(new_data)
					if data['class']=='TPV':
						if int(data['mode'])>2:

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

							# 格式化为 NMEA 格式
							lat = f"{lat_degrees:02d}{lat_minutes:05.2f}"
							lon = f"{lon_degrees:03d}{lon_minutes:05.2f}"

							altitude = altitude="%06.0f"%(float(data['alt'])*3.28)#APRS报文海拔数据单位英尺，米转英尺/APRS message altitude data is in feet; convert meters to feet.
							
							timestamp = datetime.strptime(data['time'], "%Y-%m-%dT%H:%M:%S.%fZ").strftime("%H%M%S.00")#时间戳"2025-01-02T09:01:10.000Z"转为NMEA语句格式的时间戳090110.00
							
							speed='000'
							if 'speed' in data:
								speed = speed="%03.0f"%(float(data['speed'])*3.6/1852)#NMEA APRS速度数据单位均为海里每小时，GPSd报告的为米/秒。/The speed data unit for both NMEA and APRS is knots, no conversion needed.
							
							course='000'
							if 'track' in data:
								course="%03.0f"%float(data['track'])

							GNSS_Type='TPV'
							lat_raw=float(data['lat'])*100
							lon_raw=float(data['lon'])*100
							if lat and lon:
								print(lat,lat_dir,lon,lon_dir,altitude,timestamp,speed,course,GNSS_Type,lat_raw,lon_raw)
								return lat,lat_dir,lon,lon_dir,altitude,timestamp,speed,course,GNSS_Type,lat_raw,lon_raw
									  #4004.83 N 11619.38 E    000211   092344.00 000   066    GPRMC     4004.829687 11619.375852
		except Exception as e:
			print(f"Error fetching GPS data: {e}")



#{
#    "class": "TPV",
#    "device": "tcp://10.0.6.116:12321",
#    "mode": 3,
#    "time": "2025-01-02T09:01:10.000Z",
#    "ept": 0.005,
#    "lat": 40.0806169,
#    "lon": 116.322863433,
#    "altHAE": 53.7,
#    "altMSL": 60.7,
#    "alt": 60.7,
#    "track": 195.5,
#    "magtrack": 201.4,
#    "magvar": -5.9,
#    "speed": 0,
#    "climb": -0.1,
#    "geoidSep": -7,
#    "eph": 24.7
#}
