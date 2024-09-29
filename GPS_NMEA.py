import sys
import os
import time
import re
import serial
import aprs
from datetime import datetime
import socket
from Display import OLED
from watchdog import reset_watchdog
from watchdog import boot_watchdog

# 设置全局的socket超时时间，例如10秒
socket.setdefaulttimeout(5)

# 串口配置部分/COM port config params part
com_port='/dev/ttyAMA0'  
baud_rate=115200
ser=serial.Serial(com_port, baud_rate, bytesize=serial.EIGHTBITS, parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE)
LOG_FILE='/var/log/GPS_NMEA.log'
VERSION='0926.01'

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
		if Test_Flag==0:
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

def get_gnss_position(Test_Flag):
	try:
		ser.reset_input_buffer()
		i=0
		while True:
			if ser.in_waiting > 0:
				line=ser.readline().decode('ascii', errors='replace').strip()  # 读取一行NMEA数据
				if Test_Flag!=0:
					line='$GPRMC,%s,A,4807.038,N,01131.000,E,010.4,084.4,230394,003.1,W*6A'%datetime.now().strftime('%H%M%S') #for testing
				lat,lat_dir,lon,lon_dir,speed,course,timestamp,GNSS_Type,lat_raw,lon_raw=NMEA_RMC(line)
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
				if Test_Flag!=0:
					line='$GPGGA,%s,4004.6300,N,11618.2178,E,01,07,10.3,20.05,M,-15.40,M,1.1,1023*63<CR><LF>'%datetime.now().strftime('%H%M%S') #for testing
				altitude=NMEA_GGA(line,timestamp)
				if altitude :
					#save_log(f"GNSS RMC: speed/knots={speed}, course={course}")
					break
				i+=1
		return lat,lat_dir,lon,lon_dir,altitude,timestamp,speed,course,GNSS_Type,lat_raw,lon_raw
	except Exception as err:
		save_log(f"get_gnss_position: {err}")
		raise



if __name__ == '__main__':
	#boot_watchdog()
	Test_Flag=int(sys.argv[1])
	SSID=sys.argv[2]
	Message=sys.argv[3]
	SSID_ICON=sys.argv[4]
	OLED_Enable=int(sys.argv[5])
	if sys.argv[6]=='':
		OLED_Address=60
	else:
		OLED_Address=int(sys.argv[6],16)

	OLED_Enable,oled=OLED.OLED_Init(OLED_Enable,OLED_Address)
	update_time=datetime.min
	while True:
		try:
			while True:
				try:
					lat,lat_dir,lon,lon_dir,altitude,timestamp,speed,course,GNSS_Type,lat_raw,lon_raw = get_gnss_position(Test_Flag)
					break  # 成功获取GNSS数据时退出循环
				except Exception as err:
					save_log(f"Retrying get_gnss_position due to error: {err}")
					time.sleep(0.1)  # 等待0.1秒后重试
			
			if OLED_Enable==1:
				try:
					lat_disp=lat_dir+" "+"%08.4f"%(float(lat_raw)/100)
					lon_disp=lon_dir+" "+"%08.4f"%(float(lon_raw)/100)
					if update_time==datetime.min:
						time_diff="00"
					else:
						time_diff="%02.0f"%(datetime.now()-update_time).total_seconds()
					invert=False
					#if float(timestamp)%60>30:
					#	invert=True
					#else:
					#	invert=False
					OLED.OLED_Position(oled,lat_disp,lon_disp,GNSS_Type,update_time.strftime('%H:%M:%S'),time_diff,speed,invert)
				except Exception as err:
					save_log(f"main_OLED: {err}")
			
			if float(timestamp)%30==0:
				frame_text=(f'{SSID}>PYTHON,TCPIP*,qAC,{SSID}:!{lat}{lat_dir}/{lon}{lon_dir}{SSID_ICON}{course}/{speed}/A={altitude} APRS by RPI with GNSS Module using {GNSS_Type} at UTC {timestamp} {Message}').encode()
				callsign = b'BI1FQO'
				password = b'20898'
				
				# 定义 APRS 服务器地址和端口（字节形式）
				server_host = b'rotate.aprs2.net:14580'  # 使用 rotate.aprs2.net 服务器和端口 14580
				
				# 创建 TCP 对象并传入服务器信息
				a = aprs.TCP(callsign, password)
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


#sudo apt-get update
#sudo apt-get -y upgrade
#sudo apt-get -y install i2c-tools python3-smbus python-smbus
#sudo apt-get -y install python3-pip python3-pil
#sudo pip3 install --upgrade setuptools
#sudo pip3 install --upgrade adafruit-python-shell
#sudo pip3 install adafruit-circuitpython-ssd1306





