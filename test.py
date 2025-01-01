import socket

# 配置服务器地址和端口
HOST = '10.0.6.117'  # 服务器地址
PORT = 12321        # 服务器端口

# 创建一个 TCP socket
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    try:
        # 连接到服务器
        s.connect((HOST, PORT))
        print(f"已连接到服务器 {HOST}:{PORT}")
        
        # 发送请求数据（如果需要）
        message = "Hello, Server!"
        s.sendall(message.encode('utf-8'))
        
        # 接收服务器响应
        while True:
            data = s.recv(1024)  # 每次接收 1024 字节
            if not data:  # 如果接收不到数据，退出循环
                break
            print("收到数据:", data.decode('utf-8'))
    except Exception as e:
        print(f"发生错误: {e}")