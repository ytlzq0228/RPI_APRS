import sys
import os
from datetime import datetime
import board
import adafruit_ssd1306
import smbus
from PIL import Image,ImageDraw,ImageFont
file_dir = os.path.dirname(os.path.realpath(__file__))

LOG_FILE='/var/log/GPS_NMEA.log'
VERSION='DISP_0925.01'
bus=smbus.SMBus(1)

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

def readCapacity():

	Battery_Capacity = bus.read_word_data(0x57, 0x2a)
	return Battery_Capacity


class OLED:
	def OLED_Init(OLED_Enable,OLED_Address):
		# Define I2C OLED Display and config address.
		oled=None
		if OLED_Enable==1:
			try:
				i2c = board.I2C()
				oled = adafruit_ssd1306.SSD1306_I2C(128, 64, i2c, addr=OLED_Address)
				save_log(f"SSD1306_I2C(128, 64, i2c, addr={OLED_Address})")
				# Clear display
				oled.fill(0)
				oled.show()
				save_log("Init I2C OLED Success")
			except Exception as err:
				OLED_Enable=0
				save_log(err)
				save_log("Init I2C OLED Fail.Turn off it.")
		return OLED_Enable,oled


	def OLED_Position(oled,lat_disp,lon_disp,GNSS_Type,update_time,time_dif,speed,invert=False):
		try:
			speed="%03.0f"%(float(speed)*1.852)
			bat_cap=round(int(readCapacity())/6.25)
			# Make sure to create image with mode '1' for 1-bit color.
			image = Image.new("1", (oled.width, oled.height))
			
			# Get drawing object to draw on image.
			draw = ImageDraw.Draw(image)
			
			font1 = ImageFont.truetype(os.path.join(file_dir, 'Menlo.ttc'), 11)
			font3 = ImageFont.truetype(os.path.join(file_dir, 'PixelOperator.ttf'), 16)
			font2 = ImageFont.truetype(os.path.join(file_dir, 'Menlo.ttc'), 13,index=1)
			if invert:
				draw.rectangle([0, 0, oled.width, oled.height], fill=128)
				fill_color=0
			else:
				fill_color=128
			#logging.info ("***draw line")
			draw.line([(0,0),(127,0)], fill = fill_color)
			draw.line([(0,0),(0,63)], fill = fill_color)
			draw.line([(0,63),(127,63)], fill = fill_color)
			draw.line([(127,0),(127,63)], fill = fill_color)
			draw.line([(0,16),(127,16)], fill = fill_color)
			#logging.info ("***draw text")
			draw.text((3,0), 'GPS%s'%bat_cap, font = font2, fill = fill_color)
			draw.text((1,16), "Lat:%s"%lat_disp, font = font1, fill = fill_color)
			draw.text((1,27), "Lon:%s"%lon_disp, font = font1, fill = fill_color)
			draw.text((1,38), "Type:%s %sKM/H"%(GNSS_Type,speed), font = font1, fill = fill_color)
			draw.text((1,50), 'Update:%s-%s'%(update_time,time_dif), font = font1, fill = fill_color)

			draw.rectangle((106, 3, 123, 13), outline=fill_color)
			draw.rectangle((124, 5, 125, 11), outline=fill_color)
			for i in range(bat_cap):
				draw.line([(107+i,4),(107+i,12)], fill = fill_color)
	
			# Display image
			oled.image(image)
			oled.show()
			
		except Exception as err:
			save_log(err)
	
	def OLED_Display(oled,Message):
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
			draw.text((1,25), Message, font = font1, fill = 255)
			# Display image
			oled.image(image)
			oled.show()
			
		except Exception as err:
			save_log(err)

if __name__ == '__main__':
	OLED_Enable=1
	OLED_Address=0x3c
	OLED_Enable,oled=OLED.OLED_Init(OLED_Enable,OLED_Address)
	OLED.OLED_Position(oled,"040.0703800","112.0713240","GNRMC","21:19:32","12","013",invert=False)
