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



# 日志存储目录
USB_DIR="/mnt/usb"
LOG_FILE="/var/log/GPS_NMEA.log"

# 获取当前时间戳（格式：YYYYMMDDHHMMSS）
DATE_PREFIX=$(date +"%Y%m%d%H%M%S")

# 获取 SSID（可选）
SSID=$(get_config "SSID_Config" "SSID")
echo "SSID: $SSID"

# 生成本地归档文件名
LOCAL_ARCHIVED_FILE="${USB_DIR}/${DATE_PREFIX}_GPS_${SSID}.log"

# 复制日志文件到 USB 目录并添加时间戳
cp $LOG_FILE $LOCAL_ARCHIVED_FILE
if [ $? -eq 0 ]; then
    echo "$(date) - Log file archived: $LOCAL_ARCHIVED_FILE"
else
    echo "$(date) - Failed to archive log file to $USB_DIR"
    exit 1
fi

# 清空原日志文件，保留文件结构
> $LOG_FILE

# 设置远程服务器信息
REMOTE_USER=$(get_config "SFTP_Config" "REMOTE_USER")
REMOTE_HOST=$(get_config "SFTP_Config" "REMOTE_HOST")
REMOTE_DIR=$(get_config "SFTP_Config" "REMOTE_DIR")
REMOTE_PORT=$(get_config "SFTP_Config" "REMOTE_PORT")

# 遍历 /mnt/usb/ 目录下未上传的日志文件
for FILE in ${USB_DIR}/*.log; do
    # 检查文件是否存在（避免 glob 为空时出错）
    [ -e "$FILE" ] || continue
    
    # 跳过已上传的文件（_uploaded 后缀）
    if [[ "$FILE" == *_uploaded.log ]]; then
        echo "$(date) - Skipping already uploaded file: $FILE"
        continue
    fi
    
    # 生成远程存储文件名
    FILE_BASENAME=$(basename "$FILE")
    REMOTE_FILE="${REMOTE_DIR}/${FILE_BASENAME}"

    # 上传文件到远程服务器
    scp -P $REMOTE_PORT "$FILE" "${REMOTE_USER}@${REMOTE_HOST}:${REMOTE_FILE}"
    
    # 检查上传是否成功
    if [ $? -eq 0 ]; then
        echo "$(date) - Successfully uploaded: $FILE"
        
        # 重命名文件，标记为已上传
        mv "$FILE" "${FILE}_uploaded.log"
        echo "$(date) - Marked as uploaded: ${FILE}_uploaded.log"
    else
        echo "$(date) - Failed to upload: $FILE"
    fi
done

echo "$(date) - Sync process completed."
exit 0

