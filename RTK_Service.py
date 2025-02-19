import socket
import time
from gps import gps, WATCH_ENABLE, WATCH_NEWSTYLE
import base64

def generate_gga(latitude, longitude, timestamp):
    # 格式化时间为hhmmss
    utc_time = time.strptime(timestamp, "%Y-%m-%dT%H:%M:%S.%fZ")
    formatted_time = time.strftime("%H%M%S", utc_time)
    
    # 简单的GGA消息生成示例
    gga = f"GPGGA,{formatted_time},{latitude:.6f},N,{longitude:.6f},E,1,12,1.0,0.0,M,0.0,M,,"
    checksum = 0
    for char in gga:
        checksum ^= ord(char)
    return f"${gga}*{checksum:02X}"

def send_gga_to_ntrip(gga, ntrip_socket):
    # 发送GGA消息到NTRIP服务器以获取RTK修正信息
    try:
        ntrip_socket.sendall(gga.encode('ascii') + b'\r\n')
    except socket.error as e:
        print("Socket error:", e)
        return False
    return True

def connect_to_ntrip_server(user, password, server, port, mountpoint):
    # 连接到NTRIP服务器
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((server, port))
    
    # 使用base64编码用户名和密码
    auth = f"{user}:{password}".encode('ascii')
    auth_encoded = base64.b64encode(auth).decode('ascii')
    
    # HTTP 0.9基本请求格式，适用于早期的简单NTRIP服务器
    ntrip_request = f"GET /{mountpoint}\r\nAuthorization: Basic {auth_encoded}\r\n\r\n"
    s.sendall(ntrip_request.encode('ascii'))
    # 跳过HTTP头部响应
    response = s.recv(1024)
    print(response.decode('ascii'))  # 打印连接确认消息
    return s

# 设置GPSD连接
session = gps(mode=WATCH_ENABLE | WATCH_NEWSTYLE)
ntrip_socket = connect_to_ntrip_server("qxymtq002", "c4bcfd9", "rtk.ntrip.qxwz.com", 8002, "AUTO")

try:
    while True:
        report = session.next()
        # 当我们从GPSD获得一个定位报告时
        if report['class'] == 'TPV':
            if hasattr(report, 'lat') and hasattr(report, 'lon'):
                # 生成GGA消息
                gga_message = generate_gga(report.lat, report.lon, report.time)
                # 发送GGA消息到NTRIP服务器
                if send_gga_to_ntrip(gga_message, ntrip_socket):
                    # 读取服务器返回的数据
                    response = ntrip_socket.recv(4096)
                    print(response.decode('ascii'))
except KeyError:
    pass
except KeyboardInterrupt:
    print("Script stopped by user.")
finally:
    ntrip_socket.close()
    print("NTRIP connection closed.")