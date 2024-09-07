#!/bin/bash

# 目标IP地址
TARGET_IP="114.114.114.114"

# Ping目标IP，-c 3表示尝试ping 3次，-W 2表示每次等待2秒
ping -c 3 -W 2 $TARGET_IP > /dev/null 2>&1

# 检查ping是否成功，$? 用于获取上一条命令的退出状态
if [ $? -ne 0 ]; then
    echo "$(date): Ping $TARGET_IP 失败，正在重启openvpn服务..."
    # 重启openvpn服务
    sudo systemctl restart openvpn.service@ctsdn
else
    echo "$(date): Ping $TARGET_IP 成功。"
fi