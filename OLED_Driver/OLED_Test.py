import sys
import os
from datetime import datetime
from PIL import Image,ImageDraw,ImageFont
file_dir = os.path.dirname(os.path.realpath(__file__))


def OLED_Position(lat_disp,lon_disp,GNSS_Type,update_time,time_dif,speed,bat_cap,invert=False):
	try:
		speed="%03.0f"%(float(speed)*1.852)
		bat_cap=round(int(bat_cap)/6.25)
		# Make sure to create image with mode '1' for 1-bit color.
		image = Image.new("1", (128, 64))
		
		# Get drawing object to draw on image.
		draw = ImageDraw.Draw(image)
		
		font1 = ImageFont.truetype(os.path.join(file_dir, 'Menlo.ttc'), 11)
		font1_XL = ImageFont.truetype(os.path.join(file_dir, 'Menlo.ttc'), 30)
		font1_SM = ImageFont.truetype(os.path.join(file_dir, 'Menlo.ttc'), 8)
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
		draw.text((3,0), 'GPS APRS Inf', font = font2, fill = fill_color)
		draw.text((1,16), "%s"%lat_disp, font = font1, fill = fill_color)
		draw.text((1,27), "%s"%lon_disp, font = font1, fill = fill_color)
		draw.text((72,15), "Speed:km /H", font = font1_SM, fill = fill_color)
		draw.text((73,21), speed, font = font1_XL, fill = fill_color)
		draw.text((1,38), "Type:%s"%GNSS_Type, font = font1, fill = fill_color)
		draw.text((1,50), 'Update:%s-%s'%(update_time,time_dif), font = font1, fill = fill_color)

		draw.rectangle((106, 3, 123, 13), outline=fill_color)
		draw.rectangle((124, 5, 125, 11), outline=fill_color)
		for i in range(bat_cap):
			draw.line([(107+i,4),(107+i,12)], fill = fill_color)

		image.show()

	except Exception as err:
		raise err


if __name__ == '__main__':
	OLED_Position("N 040.0703","E 112.0713","GNRMC","21:19:32","12","013","100",invert=False)