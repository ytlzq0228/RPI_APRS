import socket
import threading
import serial
import time

# 串行端口配置
serial_port = '/dev/ttyAMA0'
baud_rate = 115200

# 服务器设置
host = '0.0.0.0'
port_read_only = 12321  # 只读端口
port_read_write = 12322  # 读写端口

# 初始化串行端口
ser = serial.Serial(serial_port, baud_rate, timeout=1)

# 客户端集合和锁
clients_lock = threading.Lock()
read_only_clients = set()
read_write_clients = set()

def distribute_serial_data():
    """从串行端口读取数据并分发给所有TCP客户端"""
    while True:
        if ser.in_waiting > 0:
            data = ser.read(ser.in_waiting)
            with clients_lock:
                for conn in read_only_clients:
                    conn.sendall(data)
                for conn in read_write_clients:
                    conn.sendall(data)
        time.sleep(0.1)

def handle_client(conn, addr, client_set):
    """处理客户端，区分只读和读写客户端"""
    with clients_lock:
        client_set.add(conn)
    print(f"Connected by {addr}")

    try:
        while True:
            if client_set is read_write_clients:
                data = conn.recv(1024)
                if not data:
                    break
                ser.write(data)  # 写入到串行端口
    except socket.error as e:
        print(f"Client {addr} disconnected: {e}")
    finally:
        with clients_lock:
            client_set.remove(conn)
        conn.close()

def start_server(port, client_set):
    """启动TCP服务器"""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((host, port))
        s.listen()
        print(f"Listening on {host}:{port}")

        while True:
            conn, addr = s.accept()
            threading.Thread(target=handle_client, args=(conn, addr, client_set)).start()

def main():
    """启动串行数据分发和TCP服务器"""
    threading.Thread(target=distribute_serial_data).start()  # 开始分发串行数据
    threading.Thread(target=start_server, args=(port_read_only, read_only_clients)).start()  # 只读端口
    start_server(port_read_write, read_write_clients)  # 读写端口

if __name__ == '__main__':
    main()