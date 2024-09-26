import smbus
import time

# 初始化 I2C 总线
bus = smbus.SMBus(1)  # 树莓派的 I2C-1

# I2C 设备地址
device_address = 0x57
register_address = 0x06

def reset_watchdog():
    try:
        # 读取寄存器的当前值
        TMP = bus.read_byte_data(device_address, register_address)
        
        # 确保看门狗开启（OR 操作以确保第 7 位为 1）
        RST = 0x80 | TMP
        
        # 喂看门狗（OR 操作以确保第 5 位为 1）
        RST = 0x20 | TMP
        
        # 将新的值写回寄存器
        bus.write_byte_data(device_address, register_address, RST)
        
    finally:
        return True