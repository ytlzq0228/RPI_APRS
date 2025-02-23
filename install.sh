#!/bin/bash


mount -o remount,rw / ; sudo mount -o remount,rw /boot


git reset --hard
git pull origin main

echo "Code pulled on $(date)"

# 检查 /etc/GPS_config.ini 是否存在
if [ -f "/etc/GPS_config.ini" ]; then
    echo "/etc/GPS_config.ini already exists. Skipping copy."
else
    echo "/etc/GPS_config.ini does not exist. Copying..."
    cp ./GPS_config.ini /etc/GPS_config.ini
    echo "Copied ./GPS_config.ini to /etc/GPS_config.ini."
fi
mkdir /etc/RPI_APRS
cp -r * /etc/RPI_APRS

# 定义服务文件路径
SERVICE_FILE="/etc/systemd/system/aprs_reporter.service"
SCRIPT_PATH="/etc/RPI_APRS/APRS_Reporter.sh"
LOG_DIR="/var/log"

# 确保日志目录存在
mkdir -p "$LOG_DIR"

# 检查并创建脚本目录
if [ ! -d "/etc/RPI_APRS" ]; then
    mkdir -p "/etc/RPI_APRS"
    echo "Created directory /etc/RPI_APRS"
fi

# 检查脚本是否存在
if [ ! -f "$SCRIPT_PATH" ]; then
    echo "Error: $SCRIPT_PATH does not exist. Please ensure your script is in place."
    exit 1
fi

# 写入服务文件内容
echo "Creating systemd service file..."
cat <<EOF | sudo tee "$SERVICE_FILE"
[Unit]
Description=APRS Reporter Service
After=network.target i2c.service
Wants=network-online.target

[Service]
Type=simple
ExecStart=/bin/bash $SCRIPT_PATH
ExecStop=/bin/bash -c "pkill -f APRS_Reporter.py"
Restart=on-failure
RestartSec=5
StandardOutput=append:$LOG_DIR/APRS_Reporter.log
StandardError=append:$LOG_DIR/APRS_Reporter.err

[Install]
WantedBy=multi-user.target
EOF

# 设置正确的权限
sudo chmod 644 "$SERVICE_FILE"
echo "Service file created at $SERVICE_FILE"

# 重新加载 systemd 服务
sudo systemctl daemon-reload

# 启用服务开机自启
sudo systemctl enable aprs_reporter.service
echo "Service enabled to start at boot."

# 启动服务
sudo systemctl start aprs_reporter.service
echo "Service started."

# 检查服务状态
sudo systemctl status aprs_reporter.service --no-pager


apt-get update
apt-get -y install i2c-tools python3-smbus python3-pip python3-pil libjpeg-dev zlib1g-dev libfreetype6-dev liblcms2-dev libopenjp2-7 libtiff5 gpsd
python3 -m pip install --upgrade setuptools adafruit-circuitpython-ssd1306 adafruit-python-shell luma.oled pillow gps3 aprs psutil
#安装必要依赖

sync ; sudo sync ; sudo sync ; sudo mount -o remount,ro / ; sudo mount -o remount,ro /boot


