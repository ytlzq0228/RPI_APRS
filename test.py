import sys
import os
import time
import re
import serial
import aprs
from datetime import datetime
import socket

# 设置全局的socket超时时间，例如10秒
socket.setdefaulttimeout(2)

## 串口配置部分/COM port config params part
#com_port='/dev/ttyu0'  
#baud_rate=115200
#ser=serial.Serial(com_port, baud_rate, bytesize=serial.EIGHTBITS, parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE)
LOG_FILE='./GPS_NMEA.log'
VERSION='0912.01'

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

def NMEA_GPGGA(sentence):
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
			timestamp=parts[1]
			save_log(sentence)
			return lat_dd,lat_dir,lon_dd,lon_dir,altitude,timestamp
		else:
			print("No %s Signal. Waiting....."%parts[0])
			return None,None,None,None,0,None
	return None,None,None,None,None,None

def NMEA_GPRMC(sentence):
	match=re.match(r'^\$..RMC,.*', sentence)  # 匹配GPRMC语句
	if match:
		parts=sentence.split(',')
		if len(parts) > 8 and parts[7] and parts[8]:
			speed="%03.0f"%float(parts[7]) #NMEA APRS速度数据单位均为海里每小时/The speed data unit for both NMEA and APRS is knots, no conversion needed.
			course="%03.0f"%float(parts[8]) #NMEA APRS航向数据单位均为度/The course data unit for both NMEA and APRS is degrees, no conversion needed.
			save_log(sentence)
			return speed,course
		else:
			print("No %s Signal. Waiting....."%parts[0])
	return '000','000'

def get_gnss_position():
	try:
		i=0
		while True:
			#line=ser.readline().decode('ascii', errors='replace').strip()  # 读取一行NMEA数据
			line='$GPGGA,041824.000,4004.6300,N,11618.2178,E,01,07,10.3,20.05,M,-15.40,M,1.1,1023*63<CR><LF>' #for testing
			#save_log(f"GPGGA Line:{line}")
			lat,lat_dir,lon,lon_dir,altitude,timestamp=NMEA_GPGGA(line)
			if lat is not None and lon is not None and altitude is not None:
				save_log(f"GNSS GPGGA: lat={lat}, lon={lon}, altitude/feet={altitude}")
				break
			if altitude==0:
				i+=1
			if altitude==0 and i%60==1:
				save_log('No GPS Signal. Waiting.....')
			
		i=0
		while i<120:
			#line=ser.readline().decode('ascii', errors='replace').strip()  # 读取一行NMEA数据
			line='$GPRMC,123519,A,4807.038,N,01131.000,E,010.4,084.4,230394,003.1,W*6A' #for testing
			#save_log(f"GPRMC Line:{line}")
			speed,course=NMEA_GPRMC(line)
			if speed!='000' or course!='000':
				save_log(f"GNSS GPRMC: speed/knots={speed}, course={course}")
				break
			i+=1
		return lat,lat_dir,lon,lon_dir,altitude,timestamp,speed,course
	except Exception as err:
		save_log(f"get_gnss_position: {err}")
		raise


if __name__ == '__main__':
	while True:
		try:
			while True:
				try:
					lat,lat_dir,lon,lon_dir,altitude,timestamp,speed,course = get_gnss_position()
					break  # 成功获取GNSS数据时退出循环
				except Exception as err:
					save_log(f"Retrying get_gnss_position due to error: {err}")
					time.sleep(1)  # 等待1秒后重试
			frame_text=('BI1FQO-MI>PYTHON,TCPIP*,qAC,BI1FQO-MI:!%s%s/%s%s>%s/%s/A=%s APRS by RPI with GPS at UTC %s on 逗老师的Xiaomi Su7 Max,see more https://ctsdn.blog.csdn.net/article/details/130228867'%(lat,lat_dir,lon,lon_dir,course,speed,altitude,timestamp)).encode()
			a=aprs.TCP(b'BI1FQO', b'20898')
			a.start()
			aprs_return=a.send(frame_text)
			if aprs_return==len(frame_text)+2:
				save_log('APRS Report Good Length:%s'%aprs_return)
				time.sleep(10)
			else:
				save_log('APRS Report Return:%s Frame Length: %s Retrying..'%(aprs_return,frame_text))
		except Exception as err:
			save_log(f"main: {err}")






