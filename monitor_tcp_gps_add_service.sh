#!/bin/bash
mount -o remount,rw / ; sudo mount -o remount,rw /boot
cp /etc/RPI_APRS/monitor_tcp_gps.service /etc/systemd/system/
sudo cp /etc/RPI_APRS/monitor_tcp_gps.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable monitor_tcp_gps.service
sudo systemctl start monitor_tcp_gps.service
sync ; sudo sync ; sudo sync ; sudo mount -o remount,ro / ; sudo mount -o remount,ro /boot