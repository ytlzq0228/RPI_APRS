#!/bin/bash


# 目标IP地址
TARGET_IP="10.1.9.1"

# 定义最大重试次数
MAX_RETRIES=3

# 定义当前重试次数
RETRY_COUNT=0

# Ping目标IP并检查结果
ping_target() {
    ping -c 3 -W 2 $TARGET_IP > /dev/null 2>&1
    return $?
}

# 循环检查Ping状态并重启VPN服务
while [ $RETRY_COUNT -lt $MAX_RETRIES ]; do
    ping_target
    if [ $? -eq 0 ]; then
        echo "$(date): Ping $TARGET_IP 成功。"
        break  # Ping成功，退出循环，继续执行后面的代码
    else
        echo "$(date): Ping $TARGET_IP 失败，正在重启openvpn服务... (第$(($RETRY_COUNT + 1))次)"
        # 重启openvpn服务
        systemctl restart openvpn.service@ctsdn
        sleep 30
    fi
    RETRY_COUNT=$(($RETRY_COUNT + 1))
done

# 如果已经尝试3次仍然失败，则重启设备
if [ $RETRY_COUNT -eq $MAX_RETRIES ]; then
    echo "$(date): 已尝试3次，但Ping仍然失败，正在重启设备..."
    reboot
fi

# 如果ping成功，或者尝试重启VPN之后Ping成功，继续执行后续代码
echo "$(date): 继续执行脚本的后续部分。"
# 在这里继续添加后续的命令





# 设置日志文件路径
LOG_FILE="/var/log/GPS_NMEA.log"

# 获取当前日期时间作为文件前缀（格式：yyyy-mm-dd-hh-mm-ss）
DATE_PREFIX=$(date +"%Y-%m-%d-%H-%M-%S")
# 生成目标文件名
REMOTE_FILE="${DATE_PREFIX}_GPS_NMEA.log"


# 设置远程服务器信息
REMOTE_USER="root"
REMOTE_HOST="nas.ctsdn.com"
REMOTE_DIR="/volume1/Storage/Su7-GPS-PATH"





# 拷贝文件到远程服务器
scp -P 10223 $LOG_FILE ${REMOTE_USER}@${REMOTE_HOST}:${REMOTE_DIR}/${REMOTE_FILE}

# 检查拷贝是否成功
if [ $? -eq 0 ]; then
  echo "File copied successfully to ${REMOTE_USER}@${REMOTE_HOST}:${REMOTE_DIR}/${REMOTE_FILE}"
  
  # 删除本地日志文件
  rm -f $LOG_FILE
  
  if [ $? -eq 0 ]; then
    echo "Local log file deleted successfully."
  else
    echo "Failed to delete local log file."
  fi
else
  echo "Failed to copy file to remote server."
fi