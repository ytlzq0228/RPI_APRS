from PIL import Image,ImageDraw,ImageFont

class OLED
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
			draw.text((7,16), '%s,%s'%(lat,lon), font = font1, fill = 255)
			draw.text((1,33), 'GNSS_Type: %s'%GNSS_Type, font = font1, fill = 255)
			draw.text((7,50), 'Update: %s'%update_time, font = font1, fill = 255)
			# Display image
			oled.image(image)
			oled.show()
			
		except Exception as err:
			print(err)
	
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
			print(err)
