#!/bin/bash

# 定义 OLED 的 I2C 地址
I2C_ADDR=0x3C

# 初始化 SSD1306 显示屏（简化版本）
i2cset -y 1 $I2C_ADDR 0x00 0xAE    # Display OFF
i2cset -y 1 $I2C_ADDR 0x00 0x20    # Set Memory Addressing Mode
i2cset -y 1 $I2C_ADDR 0x00 0x10    # Set Page Addressing Mode
i2cset -y 1 $I2C_ADDR 0x00 0xB0    # Set Page Start Address for Page Addressing Mode
i2cset -y 1 $I2C_ADDR 0x00 0xC8    # Set COM Output Scan Direction
i2cset -y 1 $I2C_ADDR 0x00 0x00    # Set Low Column Address
i2cset -y 1 $I2C_ADDR 0x00 0x10    # Set High Column Address
i2cset -y 1 $I2C_ADDR 0x00 0x40    # Set Start Line Address
i2cset -y 1 $I2C_ADDR 0x00 0x81    # Set Contrast Control
i2cset -y 1 $I2C_ADDR 0x00 0xFF    # Contrast Data
i2cset -y 1 $I2C_ADDR 0x00 0xA1    # Set Segment Re-map
i2cset -y 1 $I2C_ADDR 0x00 0xA6    # Set Normal/Inverse Display
i2cset -y 1 $I2C_ADDR 0x00 0xA8    # Set Multiplex Ratio
i2cset -y 1 $I2C_ADDR 0x00 0x3F    # 1/64 Duty
i2cset -y 1 $I2C_ADDR 0x00 0xA4    # Disable Entire Display On
i2cset -y 1 $I2C_ADDR 0x00 0xD3    # Set Display Offset
i2cset -y 1 $I2C_ADDR 0x00 0x00    # No Offset
i2cset -y 1 $I2C_ADDR 0x00 0xD5    # Set Display Clock Divide Ratio/Oscillator Frequency
i2cset -y 1 $I2C_ADDR 0x00 0xF0    # Divide Ratio
i2cset -y 1 $I2C_ADDR 0x00 0xD9    # Set Pre-charge Period
i2cset -y 1 $I2C_ADDR 0x00 0x22
i2cset -y 1 $I2C_ADDR 0x00 0xDA    # Set COM Pins Hardware Configuration
i2cset -y 1 $I2C_ADDR 0x00 0x12
i2cset -y 1 $I2C_ADDR 0x00 0xDB    # Set VCOMH Deselect Level
i2cset -y 1 $I2C_ADDR 0x00 0x20
i2cset -y 1 $I2C_ADDR 0x00 0x8D    # Charge Pump Setting
i2cset -y 1 $I2C_ADDR 0x00 0x14
i2cset -y 1 $I2C_ADDR 0x00 0xAF    # Display ON

# 清屏（全屏设置为黑色）
for page in $(seq 0 7); do
    i2cset -y 1 $I2C_ADDR 0x00 0xB0$page  # Set page address
    i2cset -y 1 $I2C_ADDR 0x00 0x00       # Set low column address
    i2cset -y 1 $I2C_ADDR 0x00 0x10       # Set high column address
    for col in $(seq 0 127); do
        i2cset -y 1 $I2C_ADDR 0x40 0x00   # Clear display (fill with zeros)
    done
done

# 定义 "B" 字符的位图，8x8 像素，每一行对应一个字节
# 你可以使用在线工具生成字符位图
booting_data=(0x00 0x7C 0x44 0x7C 0x44 0x44 0x7C 0x00)  # 简化的 "B" 字符

# 发送数据到 OLED 显示屏，假设要显示在第 0 页
i2cset -y 1 $I2C_ADDR 0x00 0xB0  # Set page 0
i2cset -y 1 $I2C_ADDR 0x00 0x00  # Set low column address
i2cset -y 1 $I2C_ADDR 0x00 0x10  # Set high column address

# 将数据发送给 OLED
for byte in "${booting_data[@]}"; do
    i2cset -y 1 $I2C_ADDR 0x40 $byte
done

