import smbus2
import time

# 设置I2C总线
bus = smbus2.SMBus(1)  # Raspberry Pi通常是1

# GNSS模块的I2C地址
I2C_ADDRESS = 0x50
I2C_READ_ADDRESS = 0x50

def read_buffer_length():
    # 读取缓冲区长度
    write = smbus2.i2c_msg.write(I2C_ADDRESS, [0xAA, 0x51, 0x00, 0x04, 0x00, 0x00, 0x00, 0x04])
    bus.i2c_rdwr(write)
    read = smbus2.i2c_msg.read(I2C_READ_ADDRESS, 4)  # 读取4字节长度数据
    bus.i2c_rdwr(read)
    # 解析返回的数据，假设返回数据是小端格式
    buffer_length = int.from_bytes(bytes(read), 'little')
    return buffer_length

def write_data_to_gnss(data):
    buffer_length = read_buffer_length()
    print(buffer_length)
    data_length = len(data)
    if data_length > buffer_length:
        print("Data length exceeds buffer length, needs segmentation.")
        return

    # 发送写入数据长度的配置指令
    write_length_command = [0xAA, 0x53, 0x10, 0x00] + list(data_length.to_bytes(4, 'little'))
    bus.write_i2c_block_data(I2C_ADDRESS, 0x00, write_length_command)
    
    # 写入数据
    bus.write_i2c_block_data(I2C_ADDRESS, 0x58, data)

def main():
    # 示例数据
    example_data = [0x01, 0x02, 0x03, 0x04]  # 替换为实际要发送的数据
    write_data_to_gnss(example_data)
    print("Data written to GNSS module successfully.")

if __name__ == '__main__':
    main()