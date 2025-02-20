import socket
import serial
import threading

# 打开串行端口
ser = serial.Serial('/dev/ttyAMA0', 115200, timeout=1)

# 服务器设置
host = '0.0.0.0'
port_read_only = 12321  # 只读端口
port_read_write = 12322  # 读写端口

def handle_read_only_client(conn, addr):
    print(f"Connected by {addr} for read-only access")
    try:
        while True:
            data = ser.read(ser.in_waiting or 1)
            if data:
                conn.sendall(data)
    except socket.error as e:
        print(f"Read-only client {addr} disconnected: {e}")
    finally:
        conn.close()

def handle_read_write_client(conn, addr):
    print(f"Connected by {addr} for read-write access")
    try:
        while True:
            # 发送数据到客户端
            data = ser.read(ser.in_waiting or 1)
            if data:
                conn.sendall(data)
            # 读取来自客户端的数据
            data = conn.recv(1024)
            if data:
                ser.write(data)
    except socket.error as e:
        print(f"Read-write client {addr} disconnected: {e}")
    finally:
        conn.close()

def start_server(port, handler):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((host, port))
        s.listen()
        print(f"Listening on {host}:{port}")
        while True:
            conn, addr = s.accept()
            client_thread = threading.Thread(target=handler, args=(conn, addr))
            client_thread.start()

# 启动服务器
threading.Thread(target=start_server, args=(port_read_only, handle_read_only_client)).start()
threading.Thread(target=start_server, args=(port_read_write, handle_read_write_client)).start()