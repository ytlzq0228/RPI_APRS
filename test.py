from flask import Flask, jsonify, render_template
from gps3 import gps3
import json
import time

app = Flask(__name__)

# 创建 GPSD 连接
gps_socket = gps3.GPSDSocket()
data_stream = gps3.DataStream()
gps_socket.connect()
gps_socket.watch()


def get_constellation(prn):
    # 定义PRN号与星座的对应关系
    constellation_map = {
        'GPS': range(1, 33),  # GPS uses PRNs from 1 to 32
        'GLONASS': range(33, 66),  # GLONASS uses PRNs from 33 to 65
        'Galileo': range(301, 337),  # Galileo uses PRNs from 301 to 336
        'BeiDou': range(201, 237),  # BeiDou uses PRNs from 201 to 236
        'QZSS': range(193, 198),  # QZSS uses PRNs from 193 to 197
        'IRNSS': range(401, 408),  # IRNSS uses PRNs from 401 to 407
        'WAAS': range(133, 139),  # WAAS (North America) uses PRNs from 133 to 138
        'EGNOS': range(120, 139),  # EGNOS (Europe) uses PRNs from 120 to 138
        'GAGAN': range(127, 129),  # GAGAN (India) uses PRNs 127 and 128
        'MSAS': range(129, 138)  # MSAS (Japan) uses PRNs from 129 to 137
    }

    # 遍历字典，找到相应的星座
    for constellation, prns in constellation_map.items():
        if prn in prns:
            return f"{constellation}_{prn}"
    return f"Unknow_{prn}"


@app.route('/')
def index():
    return render_template('index.html')

#@app.route('/snr-data')
#def snr_data():
#    # 这里直接返回模拟数据
#    return jsonify(data)


@app.route('/snr-data')
def snr_data():
    satellites_data = {}
    try:
        start_time = time.time()
        while True:
            new_data = gps_socket.next()  # 使用 next() 从 socket 获取数据
            if new_data:
                data_stream.unpack(new_data)
                if 'satellites' in data_stream.SKY:
                    for sat in data_stream.SKY['satellites']:
                        if 'ss' in sat:
                            sat_name=get_constellation(sat['PRN'])
                            satellites_data[sat_name] = sat['ss']
            if time.time() - start_time > 2:  # 设置10秒超时，避免无限循环
                break
        #print(satellites_data)  # 调试输出合并后的数据
        return jsonify({'satellites': [{'PRN': prn, 'ss': ss} for prn, ss in satellites_data.items()]})
    except Exception as e:
        print(f"Error: {str(e)}")  # 打印错误
        return jsonify({'error': str(e)})

@app.route('/tpv-data')
def tpv_data():
    try:
        for new_data in gps_socket:  # 迭代从 GPSD 接收的数据
            if new_data:
                data_stream.unpack(new_data)
                print(data_stream.TPV)
                return jsonify(data_stream.TPV)  # 返回 TPV 数据为 JSON
    except Exception as e:
        return jsonify({'error': str(e)})  # 处理任何异常

    return jsonify({})


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)