import sys
import os
import time
import re
import serial
import aprs

# 串口配置部分/COM port config params
com_port='/dev/ttyUSB0'  
baud_rate=9600
ser=serial.Serial(com_port, baud_rate, bytesize=serial.EIGHTBITS, parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE)


def NMEA_GPGGA(sentence):
	match=re.match(r'^\$..GGA,.*', sentence)  # 匹配GPGGA语句
	if match:
		parts=sentence.split(',')
		print(parts)
		if len(parts) > 9 and parts[2] and parts[4] and parts[9]:
			lat=float(parts[2])
			lon=float(parts[4])
			lat_dir=parts[3]
			lon_dir=parts[5]
			altitude=float(parts[9]) #NMEA协议海拔数据单位米/NMEA protocol altitude data in meters​.
			altitude=altitude*3.28 #APRS报文海拔数据单位英尺，米转英尺/APRS message altitude data is in feet; convert meters to feet.
			lat_dd="%.2f"%lat
			lon_dd="%.2f"%lon
			altitude="%06.0f"%altitude
			timestamp=parts[1]
			return lat_dd,lat_dir,lon_dd,lon_dir,altitude,timestamp
		else:
			print("No %s Signal. Waiting....."%parts[0])
	return None,None,None,None,None,None

def NMEA_GPRMC(sentence):
	match=re.match(r'^\$GPRMC,.*', sentence)  # 匹配GPRMC语句
	if match:
		parts=sentence.split(',')
		print(parts)
		if len(parts) > 8 and parts[7] and parts[8]:
			speed="%03.0f"%float(parts[7]) #NMEA APRS速度数据单位均为海里每小时/The speed data unit for both NMEA and APRS is knots, no conversion needed.
			course="%03.0f"%float(parts[8]) #NMEA APRS航向数据单位均为度/The course data unit for both NMEA and APRS is degrees, no conversion needed.
			return speed,course
		else:
			print("No %s Signal. Waiting....."%parts[0])
	return None,None

def get_gnss_position():
	try:
		ser.reset_input_buffer()
		while True:
			if ser.in_waiting > 0:  
				line=ser.readline().decode('ascii', errors='replace').strip()  # 读取一行NMEA数据
				#line='$GPGGA,024438.00,4008.3582,N,11632.3978,E,01,07,10.3,20.05,M,-15.40,M,1.1,1023*63<CR><LF>'
				lat,lat_dir,lon,lon_dir,altitude,timestamp=NMEA_GPGGA(line)
				if lat is not None and lon is not None and altitude is not None:
					print(f"GNSS GPGGA: lat={lat}, lon={lon}, altitude/feet={altitude}")
					break
			#time.sleep(0.1)
		i=0
		speed='000'
		course='000'
		while i<60:
			if ser.in_waiting > 0:  
				line=ser.readline().decode('ascii', errors='replace').strip()  # 读取一行NMEA数据
				#line='$GPRMC,123519,A,4807.038,N,01131.000,E,010.4,084.4,230394,003.1,W*6A'
				speed,course=NMEA_GPRMC(line)
				if speed is not None and course is not None:
					print(f"GNSS GPRMC: speed/knots={speed}, course={course}")
					break
			#time.sleep(0.1)
			i+=1
		return lat,lat_dir,lon,lon_dir,altitude,timestamp,speed,course
	except Exception as err:
		print(err)


if __name__ == '__main__':
	while True:
		try:
			lat,lat_dir,lon,lon_dir,altitude,timestamp,speed,course=get_gnss_position()
			frame_text=('BI1FQO-P>APDG03,TCPIP*,qAC,BI1FQO-RS:!%s%s/%s%s>%s/%s/A=%s Auto Report by RPI with GPS module at UTC %s on 逗老师的Xiaomi Su7 Max'%(lat,lat_dir,lon,lon_dir,course,speed,altitude,timestamp)).encode()
			a=aprs.TCP(b'BI1FQO', b'20898')
			print(a.start())
			print(a.send(frame_text))
			time.sleep(15)
		except Exception as err:
			print(err)






