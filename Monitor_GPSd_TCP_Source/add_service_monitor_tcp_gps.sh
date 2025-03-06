#!/bin/bash
mount -o remount,rw / ; sudo mount -o remount,rw /boot

# 写入服务文件内容
echo "Creating systemd service file..."
cat <<EOF | sudo tee /etc/systemd/system/monitor_tcp_gps.service 
[Unit]
Description=Monitor and reconnect TCP GPS source for gpsd
After=network.target gpsd.service
Wants=gpsd.service

[Service]
Type=simple
ExecStart=/etc/RPI_APRS/monitor_tcp_gps.sh
Restart=on-failure
RestartSec=10
StandardOutput=syslog
StandardError=syslog
SyslogIdentifier=monitor_tcp_gps
User=root
Environment=CONFIG_FILE=/etc/GPS_config.ini
ExecStartPre=/bin/sleep 5

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable monitor_tcp_gps.service
systemctl start monitor_tcp_gps.service
systemctl status monitor_tcp_gps.service
sync ; sudo sync ; sudo sync ; sudo mount -o remount,ro / ; sudo mount -o remount,ro /boot