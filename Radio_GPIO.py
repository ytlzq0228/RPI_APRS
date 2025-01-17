import RPi.GPIO as GPIO

def read_gpio(pin):
    """
    读取指定GPIO引脚的状态。
    每次调用自动初始化引脚模式，读取状态后自动清理。
    
    :param pin: GPIO引脚编号 (物理引脚号)
    :return: True (高电平) 或 False (低电平)
    """
    try:
        # 设置引脚模式
        GPIO.setmode(GPIO.BOARD)  # 使用物理引脚编号
        GPIO.setup(pin, GPIO.IN)
        state = False
        # 读取引脚状态
        state = GPIO.input(pin)
    finally:
        # 清理GPIO设置
        GPIO.cleanup()
        return state

if __name__ == '__main__':
    print(read_gpio(33))