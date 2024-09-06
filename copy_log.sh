#!/bin/bash

# 设置日志文件路径
LOG_FILE="/var/log/GPS_NMEA.log"
# 生成目标文件名
REMOTE_FILE="${DATE_PREFIX}_GPS_NMEA.log"


# 设置远程服务器信息
REMOTE_USER="root"
REMOTE_HOST="10.0.6.10"
REMOTE_DIR="/volume1/Storage/Su7-GPS-PATH"

# 获取当前日期时间作为文件前缀（格式：yyyy-mm-dd-hh-mm-ss）
DATE_PREFIX=$(date +"%Y-%m-%d-%H-%M-%S")



# 拷贝文件到远程服务器
scp $LOG_FILE ${REMOTE_USER}@${REMOTE_HOST}:${REMOTE_DIR}/${REMOTE_FILE}

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