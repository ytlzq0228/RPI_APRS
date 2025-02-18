import socket
import serial
import base64

# NTRIP 服务器信息
NTRIP_HOST = "rtk.ntrip.qxwz.com"
NTRIP_PORT = 8002
MOUNTPOINT = "RTCM32_GGB"
USERNAME = "qxymtq002"
PASSWORD = "c4bcfd9"

# LC29H GNSS 模块串口配置
SERIAL_PORT = "/dev/ttyAMA0"  # 串口设备
BAUD_RATE = 115200  # LC29H 波特率

def connect_ntrip():
    """连接 NTRIP Caster 并获取 RTCM 数据"""
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((NTRIP_HOST, NTRIP_PORT))

    # 生成 NTRIP 授权信息（Base64 编码）
    credentials = f"{USERNAME}:{PASSWORD}"
    credentials_base64 = base64.b64encode(credentials.encode()).decode()

    # 发送 NTRIP 请求
    request = f"GET /{MOUNTPOINT} HTTP/1.0\r\n"
    request += f"Authorization: Basic {credentials_base64}\r\n"
    request += "User-Agent: NTRIP Client\r\n"
    request += "\r\n"

    s.sendall(request.encode())

    # 读取服务器响应
    response = s.recv(1024)
    if b"ICY 200 OK" not in response:
        print("NTRIP 服务器连接失败！")
        s.close()
        return None
    print("NTRIP 连接成功，开始接收 RTCM 数据...")
    return s

def send_rtcm_to_gnss(ntrip_socket, serial_port):
    """接收 RTCM 差分数据，并发送到 LC29H"""
    try:
        while True:
            rtcm_data = ntrip_socket.recv(1024)  # 读取 1024 字节数据
            if not rtcm_data:
                print("NTRIP 连接中断")
                break
            serial_port.write(rtcm_data)  # 发送到 LC29H
    except Exception as e:
        print("发生错误:", e)
    finally:
        ntrip_socket.close()
        serial_port.close()

def main():
    """主程序入口"""
    # 连接 NTRIP 服务器
    ntrip_socket = connect_ntrip()
    if not ntrip_socket:
        return

    # 连接 GNSS 模块
    serial_port = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
    
    # 传输 RTCM 数据
    send_rtcm_to_gnss(ntrip_socket, serial_port)

if __name__ == "__main__":
    main()