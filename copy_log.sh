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
    systemctl restart aprs_reporter.service
    
else
    echo "Service running...."
fi



# 日志存储目录
LOG_PATH=$(get_config "SFTP_Config" "LOCAL_LOG_FILE_PATH")


# 设置远程服务器信息
REMOTE_USER=$(get_config "SFTP_Config" "REMOTE_USER")
REMOTE_HOST=$(get_config "SFTP_Config" "REMOTE_HOST")
REMOTE_DIR=$(get_config "SFTP_Config" "REMOTE_DIR")
REMOTE_PORT=$(get_config "SFTP_Config" "REMOTE_PORT")

rsync -avz --inplace -e "ssh -p $REMOTE_PORT" ${LOG_PATH}/*.log "${REMOTE_USER}@${REMOTE_HOST}:${REMOTE_DIR}"

echo "$(date) - Sync process completed."
exit 0


##!/bin/bash
#
#LOG_FILE="/var/log/GPS.log"
#REMOTE_USER="user"
#REMOTE_HOST="remote-server"
#REMOTE_DIR="/path/to/logs/"
#
## 监听文件变化，秒级触发
#inotifywait -m -e modify "$LOG_FILE" | while read path action file; do
#    while true; do
#        TIMESTAMP=$(date +'%Y%m%d%H%M%S')
#        rsync -avz --inplace "$LOG_FILE" "$REMOTE_USER@$REMOTE_HOST:$REMOTE_DIR/GPS.log"
#        if [ $? -eq 0 ]; then
#            break  # 传输成功，退出循环
#        else
#            sleep 5  # 传输失败，5 秒后重试
#        fi
#    done
#done
