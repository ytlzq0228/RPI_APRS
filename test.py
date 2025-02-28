import sys
import os
import time
import re
import serial
import json
import subprocess
import configparser
from gps3 import gps3
from datetime import datetime
import socket
from save_log import save_log

# 创建一个gps会话
gps_socket = gps3.GPSDSocket()
data_stream = gps3.DataStream()

# 连接到 GPSD
gps_socket.connect(host="127.0.0.1", port=2947)
gps_socket.watch()



for new_data in gps_socket:
    
    if not new_data:  # 跳过空数据
        continue
    data_stream.unpack(new_data)
    data = data_stream.TPV
    print(data)