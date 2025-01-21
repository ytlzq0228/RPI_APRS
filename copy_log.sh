#!/bin/bash
CONFIG_FILE='/etc/GPS_config.ini'
# 读取配置函数
function get_config() {
    local section=$1
    local key=$2
    grep -A 10 "^\[$section\]" "$CONFIG_FILE" | grep "^$key" | awk -F '=' '{print $2}' | sed 's/^[ \t]*//;s/[ \t]*$//'
}
PROJECT_DIR=$(get_config "PROJECT_PATH" "PROJECT_DIR")

# 检查 python3 GPS_NMEA.py 是否在运行
if ! pgrep -f "python3 APRS_Reporter.py" > /dev/null; then
    echo "python3 APRS_Reporter.py 未运行，正在执行 pull_APRS_code.sh"
    # 执行命令
    /home/pi-star/RPI_APRS/APRS_Reporter.sh &
    
else
    echo "python3 APRS_Reporter.py 正在运行。"
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
SSID=$(get_config "SSID_Config" "SSID")
echo $SSID

REMOTE_FILE="${DATE_PREFIX}_GPS_${SSID}.log"




# 设置远程服务器信息
REMOTE_USER=$(get_config "SFTP_Config" "REMOTE_USER")
REMOTE_HOST=$(get_config "SFTP_Config" "REMOTE_HOST")
#重要！！！请自行替换成你的SFTP服务器信息，或者删除
REMOTE_DIR=$(get_config "SFTP_Config" "REMOTE_DIR")
REMOTE_PORT=$(get_config "SFTP_Config" "REMOTE_PORT")


# 拷贝文件到远程服务器
scp -P $REMOTE_PORT $LOG_FILE ${REMOTE_USER}@${REMOTE_HOST}:${REMOTE_DIR}/${REMOTE_FILE}
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


