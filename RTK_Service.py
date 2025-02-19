import smbus2
import time

# 设置I2C总线
bus = smbus2.SMBus(1)  # Raspberry Pi通常是1

# 模块的I2C地址和寄存器
I2C_ADDRESS = 0x50
WRITE_REGISTER = 0x58  # 根据文档，用于写入数据的寄存器地址

def write_data_to_gnss(data):
    try:
        # 将数据分解为单个字节，并发送
        for byte in data:
            bus.write_byte_data(I2C_ADDRESS, WRITE_REGISTER, byte)
            time.sleep(0.01)  # 为稳定通信，添加短暂延时
        print("Data written to GNSS module successfully.")
    except Exception as e:
        print(f"Failed to write data: {e}")

# 示例数据：从NTRIP客户端接收的RTK修正数据
rtk_correction_data = [0xAA, 0x51, 0x20, 0x00]  # 示例数据，应替换为实际RTK数据

# 将RTK修正数据写入GNSS模块
write_data_to_gnss(rtk_correction_data)