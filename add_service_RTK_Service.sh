#!/bin/bash
mount -o remount,rw / ; sudo mount -o remount,rw /boot

# 写入服务文件内容
echo "Creating systemd service file..."
cat <<EOF | sudo tee /etc/systemd/system/Quectel_RTK.service
[Unit]
Description=NTRIP Client Service for GNSS RTK Correction
After=network.target gpsd.service

[Service]
ExecStart=/etc/RPI_APRS/RTK_Service.sh
ExecStop=/usr/bin/pkill -f RTK_Service.py
Restart=always
RestartSec=5
User=root
WorkingDirectory=/etc/RPI_APRS/
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable Quectel_RTK.service
systemctl start Quectel_RTK.service
systemctl status Quectel_RTK.service
sync ; sudo sync ; sudo sync ; sudo mount -o remount,ro / ; sudo mount -o remount,ro /boot