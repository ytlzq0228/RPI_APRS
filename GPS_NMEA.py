import sys
import os
import time
import re
import serial
import aprs
from datetime import datetime
import socket
import adafruit_ssd1306
from PIL import Image,ImageDraw,ImageFont
from ina219 import INA219, DeviceRangeError


file_dir = os.path.dirname(os.path.realpath(__file__))

# 设置全局的socket超时时间，例如10秒
socket.setdefaulttimeout(5)

# 串口配置部分/COM port config params part
com_port='/dev/ttyAMA0'  
baud_rate=115200
ser=serial.Serial(com_port, baud_rate, bytesize=serial.EIGHTBITS, parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE)
LOG_FILE='/var/log/GPS_NMEA.log'
VERSION='0925.01'

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
			GNSS_Type=parts[0].replace("$","")
			save_log(sentence)
			return lat_dd,lat_dir,lon_dd,lon_dir,altitude,timestamp,GNSS_Type
		else:
			print("No %s Signal. Waiting....."%parts[0])
			return None,None,None,None,0,None
	return None,None,None,None,None,None

def NMEA_GPRMC(sentence):
	match=re.match(r'^\$..RMC,.*', sentence)  # 匹配GPRMC语句
	if match:
		parts=sentence.split(',')
		#print(parts)
		if len(parts) > 8 and (parts[7] or parts[8]):
			if parts[7]=='':
				speed="%03.0f"%0
			else:
				speed="%03.0f"%float(parts[7]) #NMEA APRS速度数据单位均为海里每小时/The speed data unit for both NMEA and APRS is knots, no conversion needed.
			if parts[8]=='':
				course="%03.0f"%180
			else:
				course="%03.0f"%float(parts[8]) #NMEA APRS航向数据单位均为度/The course data unit for both NMEA and APRS is degrees, no conversion needed.
			save_log(sentence)
			return speed,course
		else:
			print("No %s Signal. Waiting....."%parts[0])
	return '000','000'

def get_gnss_position(Test_Flag):
	try:
		ser.reset_input_buffer()
		i=0
		while True:
			if ser.in_waiting > 0:
				line=ser.readline().decode('ascii', errors='replace').strip()  # 读取一行NMEA数据
				if Test_Flag!=0:
					line='$GPGGA,041824.00,4004.6300,N,11618.2178,E,01,07,10.3,20.05,M,-15.40,M,1.1,1023*63<CR><LF>' #for testing
					#save_log(f"GPGGA Line:{line}")
				lat,lat_dir,lon,lon_dir,altitude,timestamp,GNSS_Type=NMEA_GPGGA(line)
				if lat is not None and lon is not None and altitude is not None:
					save_log(f"GNSS GGA: lat={lat}, lon={lon}, altitude/feet={altitude}")
					break
				if altitude==0:
					i+=1
				if altitude==0 and i%60==1:
					save_log('No GNSS Signal. Waiting.....')
				i=i%3600
			
		i=0
		while i<120:
			if ser.in_waiting > 0:  
				line=ser.readline().decode('ascii', errors='replace').strip()  # 读取一行NMEA数据
				if Test_Flag!=0:
					line='$GPRMC,123519,A,4807.038,N,01131.000,E,010.4,084.4,230394,003.1,W*6A' #for testing
					#save_log(f"GPRMC Line:{line}")
				speed,course=NMEA_GPRMC(line)
				if speed!='000' or course!='000':
					save_log(f"GNSS RMC: speed/knots={speed}, course={course}")
					break
				i+=1
		return lat,lat_dir,lon,lon_dir,altitude,timestamp,speed,course,GNSS_Type
	except Exception as err:
		save_log(f"get_gnss_position: {err}")
		raise



def OLED_Display(oled,lat,lon,GNSS_Type,update_time):
	try:
		# Make sure to create image with mode '1' for 1-bit color.
		image = Image.new("1", (oled.width, oled.height))
		
		# Get drawing object to draw on image.
		draw = ImageDraw.Draw(image)
		
		font1 = ImageFont.truetype(os.path.join(file_dir, 'Menlo.ttc'), 11)
		font3 = ImageFont.truetype(os.path.join(file_dir, 'PixelOperator.ttf'), 16)
		font2 = ImageFont.truetype(os.path.join(file_dir, 'Menlo.ttc'), 13,index=1)
		#logging.info ("***draw line")
		draw.line([(0,0),(127,0)], fill = 255)
		draw.line([(0,0),(0,63)], fill = 255)
		draw.line([(0,63),(127,63)], fill = 255)
		draw.line([(127,0),(127,63)], fill = 255)
		draw.line([(0,16),(127,16)], fill = 255)
		#logging.info ("***draw text")
		draw.text((3,0), 'GPS Information', font = font2, fill = 255)
		draw.text((7,16), '%s,%s'%(lat,lon), font = font1, fill = 255)
		draw.text((1,33), 'GNSS_Type: %s'%GNSS_Type, font = font1, fill = 255)
		draw.text((7,50), 'Update: %s'%update_time, font = font1, fill = 255)
		# Display image
		oled.image(image)
		oled.show()
		
	except Exception as err:
		print(err)

if __name__ == '__main__':
	Test_Flag=int(sys.argv[1])
	SSID=sys.argv[2]
	Message=sys.argv[3]
	SSID_ICON=sys.argv[4]
	OLED_Enable=int(sys.argv[5])
	# Define I2C OLED Display and config address.
	i2c = board.I2C()
	oled = adafruit_ssd1306.SSD1306_I2C(128, 64, i2c, addr=0x3d)
	# Clear display.
	oled.fill(0)
	oled.show()

	while True:
		try:
			while True:
				try:
					lat,lat_dir,lon,lon_dir,altitude,timestamp,speed,course,GNSS_Type = get_gnss_position(Test_Flag)
					break  # 成功获取GNSS数据时退出循环
				except Exception as err:
					save_log(f"Retrying get_gnss_position due to error: {err}")
					time.sleep(1)  # 等待1秒后重试
			frame_text=(f'{SSID}>PYTHON,TCPIP*,qAC,{SSID}:!{lat}{lat_dir}/{lon}{lon_dir}{SSID_ICON}{course}/{speed}/A={altitude} APRS by RPI with GNSS Module using {GNSS_Type} at UTC {timestamp} {Message}').encode()
			a=aprs.TCP(b'BI1FQO', b'20898')
			a.start()
			aprs_return=a.send(frame_text)
			if aprs_return==len(frame_text)+2:
				save_log('APRS Report Good Length:%s'%aprs_return)
				update_time=datetime.now().strftime('%H:%M:%S')
				if OLED_Enable==1:
					OLED_Display(oled,lat,lon,GNSS_Type,update_time)
				time.sleep(30)
			else:
				save_log('APRS Report Return:%s Frame Length: %s Retrying..'%(aprs_return,frame_text))
				update_time="Fail"

		except Exception as err:
			save_log(f"main: {err}")


#sudo apt-get update
#sudo apt-get -y upgrade
#sudo apt-get -y install i2c-tools python3-smbus python-smbus
#sudo apt-get -y install python3-pip python3-pil
#sudo pip3 install --upgrade setuptools
#sudo pip3 install --upgrade adafruit-python-shell
#sudo pip3 install adafruit-circuitpython-ssd1306





