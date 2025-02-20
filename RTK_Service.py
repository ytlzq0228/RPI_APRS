import smbus2
import time

# 初始化I2C总线
bus_number = 1
device_address = 0x50  # I2C设备地址
bus = smbus2.SMBus(bus_number)

def write_data_to_device(address, data):
    """向指定的I2C地址写入数据"""
    for reg_addr, value in data:
        bus.write_byte_data(address, reg_addr, value)
        print(f"Written value {value:#04x} to register {reg_addr:#04x}")
        time.sleep(0.02)  # 延时100ms，确保数据稳定写入

# 数据准备，(寄存器地址, 数据)
commands = [
    (0x08, 0x00),
    (0x51, 0xAA),
    (0x04, 0x00),
    (0x00, 0x00)  # 根据设备手册调整这些值
]

try:
    write_data_to_device(device_address, commands)
finally:
    bus.close()
    print("I2C bus closed.")