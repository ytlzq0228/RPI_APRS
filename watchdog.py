import smbus
import time

# 初始化 I2C 总线
bus = smbus.SMBus(1)  # 树莓派的 I2C-1

# I2C 设备地址
device_address = 0x57
register_address = 0x06

def reset_watchdog():
    try:
        # 设置超时时长40*2秒
        bus.write_byte_data(0x57, 0x07, 40)
        
        # 读取寄存器的当前值
        TMP = bus.read_byte_data(0x57, 0x06)
        
        # 确保看门狗开启（OR 操作以确保第 7,5 位为 1 0x80 or 0x20 = 0xa0）
        # 0x57 0x06地址功能为
        #bit7-功能开关
        #bit5-看门狗复位
        RST = 0xa0 | TMP

        # 将新的值写回寄存器
        bus.write_byte_data(0x57, 0x06, RST)
        
    finally:
        return True

def boot_watchdog():
    try:
        #设置最大重启次数 Set the maximum number of restarts
        bus.write_byte_data(0x57, 0x0a, 10)
        
        # 读取寄存器的当前值
        TMP = bus.read_byte_data(0x57, 0x06)
        
        # 启动看门狗复位（OR 操作以确保第 4,3 位为 1 0x18）
        # 0x57 0x06地址功能为
        #bit4-功能开关
        #bit3-看门狗复位（加电后90s内喂狗）
        RST = 0x18 | TMP

        # 将新的值写回寄存器
        bus.write_byte_data(0x57, 0x06, RST)
        
    finally:
        return True

