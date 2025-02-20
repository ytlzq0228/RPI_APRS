import socket
import serial
import threading
from queue import Queue
import time

# 打开串行端口
ser = serial.Serial('/dev/ttyAMA0', 115200, timeout=1)

# 服务器设置
host = '0.0.0.0'
port_read_only = 12321  # 只读端口
port_read_write = 12322  # 读写端口


# 全局数据队列
data_queue = Queue()

def distribute_data():
    while True:
        if not data_queue.empty():
            data = data_queue.get()
            # 分发数据给读写客户端
            for conn in read_write_clients:
                conn.sendall(data)
            # 分发数据给只读客户端
            for conn in read_only_clients:
                conn.sendall(data)

# 客户端集合
read_only_clients = set()
read_write_clients = set()

def handle_client(conn, addr, client_set):
    print(f"Connected by {addr}")
    client_set.add(conn)
    try:
        while True:
            data = ser.read(ser.in_waiting or 1)
            if data:
                data_queue.put(data)
            # 特定于读写客户端的逻辑
            if client_set is read_write_clients:
                data = conn.recv(1024)
                if data:
                    ser.write(data)
    except socket.error as e:
        print(f"Client {addr} disconnected: {e}")
    finally:
        conn.close()
        client_set.remove(conn)

def start_server(port, handler, client_set):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((host, port))
        s.listen()
        print(f"Listening on {host}:{port}")
        while True:
            conn, addr = s.accept()
            threading.Thread(target=handler, args=(conn, addr, client_set)).start()

# 启动数据分发线程
threading.Thread(target=distribute_data).start()

# 启动服务器
threading.Thread(target=start_server, args=(port_read_only, handle_client, read_only_clients)).start()
threading.Thread(target=start_server, args=(port_read_write, handle_client, read_write_clients)).start()