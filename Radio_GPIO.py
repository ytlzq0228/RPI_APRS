import RPi.GPIO as GPIO

def read_gpio(Radio_CONTROL_ENABLE,GPIO_PIN):
	"""
	读取指定GPIO引脚的状态。
	每次调用自动初始化引脚模式，读取状态后自动清理。
	
	:param pin: GPIO引脚编号 (物理引脚号)
	:return: True (高电平) 或 False (低电平)
	"""
	state = False
	try:
		# 设置引脚模式
		GPIO.setmode(GPIO.BCM)  # 使用BCM逻辑引脚编号
		GPIO.setup(GPIO_PIN, GPIO.IN)
		state=False
		# 读取引脚状态
		if Radio_CONTROL_ENABLE:
			if not GPIO.input(GPIO_PIN):
				state = True
		else:
			state=True
	finally:
		# 清理GPIO设置
		GPIO.cleanup()
		return state

if __name__ == '__main__':
	for i in [16,20,21]:
		print(i,read_gpio(True,i))