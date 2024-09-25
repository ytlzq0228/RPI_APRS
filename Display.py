import sys
import os
from datetime import datetime
import board
import adafruit_ssd1306
from PIL import Image,ImageDraw,ImageFont
file_dir = os.path.dirname(os.path.realpath(__file__))

LOG_FILE='/var/log/GPS_NMEA.log'
VERSION='DISP_0925.01'

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


	def OLED_Position(oled,lat,lon,GNSS_Type,update_time):
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
			draw.text((5,16), '%s,%s'%(lat,lon), font = font1, fill = 255)
			draw.text((1,33), 'GNSS_Type: %s'%GNSS_Type, font = font1, fill = 255)
			draw.text((7,50), 'Update: %s'%update_time, font = font1, fill = 255)
			# Display image
			oled.image(image)
			oled.show()
			
		except Exception as err:
			save_log(err)
	
	def OLED_Display(Message):
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


class IPS:
from luma.core.interface.serial import i2c
from luma.oled.device import ssd1306
from luma.core.render import canvas
from PIL import ImageFont, ImageDraw

# 使用I2C接口连接设备
serial = i2c(port=1, address=0x3C)  # 确保你使用正确的I2C地址

# 创建OLED显示设备实例（如果ST7789支持I2C）
device = ssd1306(serial, width=128, height=64)

# 使用Pillow的字体功能
font = ImageFont.load_default()

# 显示文本的函数
def display_text():
    with canvas(device) as draw:
        draw.text((30, 30), "Hello, I2C ST7789!", font=font, fill="white")
