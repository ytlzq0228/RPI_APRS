#!/bin/bash
source /etc/GPS_config.cfg



# 目标IP地址
TARGET_IP="223.5.5.5"

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




# 检查 python3 GPS_NMEA.py 是否在运行
if ! pgrep -f "python3 GPS_NMEA.py" > /dev/null; then
    echo "GPS_NMEA.py 未运行，正在执行 pull_APRS_code.sh"
    # 执行命令
    /home/pi-star/RPI_APRS/pull_APRS_code.sh
else
    echo "GPS_NMEA.py 正在运行。"
fi






# 获取树莓派当前温度
get_cpu_temp() {
  # vcgencmd 命令获取树莓派的CPU温度
  temp=$(vcgencmd measure_temp | awk -F "=" '{print $2}')
  echo "$temp"
}

# 获取系统运行时间
get_uptime() {
  # 从 /proc/uptime 获取系统开机时间
  uptime_seconds=$(cut -d. -f1 /proc/uptime)
  uptime_formatted=$(printf '%02d:%02d:%02d\n' $((uptime_seconds/3600)) $((uptime_seconds%3600/60)) $((uptime_seconds%60)))
  echo "$uptime_formatted"
}

# 将信息追加到日志文件
log_system_info() {
  log_file="/var/log/GPS_NMEA.log"
  current_time=$(date '+%Y-%m-%d %H:%M:%S')
  cpu_temp=$(get_cpu_temp)
  uptime=$(get_uptime)
  
  log_message="$current_time: CPU Temperature: $cpu_temp, Uptime: $uptime"
  echo "" >> "$log_file"
  echo "$log_message" >> "$log_file"
  echo "Logged: $log_message"
}

# 执行记录信息
log_system_info


# 设置日志文件路径
LOG_FILE="/var/log/GPS_NMEA.log"

# 获取当前日期时间作为文件前缀（格式：yyyy-mm-dd-hh-mm-ss）
DATE_PREFIX=$(date +"%Y-%m-%d-%H-%M-%S")
# 生成目标文件名
REMOTE_FILE="${DATE_PREFIX}_GPS_${SSID}.log"


# 设置远程服务器信息
REMOTE_USER="root"
REMOTE_HOST="nas.ctsdn.com"
#重要！！！请自行替换成你的SFTP服务器信息，或者删除
REMOTE_DIR="/volume1/Storage/Su7-GPS-PATH"





# 拷贝文件到远程服务器
scp -P 10223 $LOG_FILE ${REMOTE_USER}@${REMOTE_HOST}:${REMOTE_DIR}/${REMOTE_FILE}
#已经启用auth_key免密认证
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


