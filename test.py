from flask import Flask, jsonify, render_template_string
from gps3 import gps3
import json

# 创建GPSD连接
gps_socket = gps3.GPSDSocket()
data_stream = gps3.DataStream()
gps_socket.connect()
gps_socket.watch()

app = Flask(__name__)

@app.route('/')
def index():
    return '''
        <h1>GPS Data</h1>
        <div id="gps-data">Waiting for GPS data...</div>
        <div id="pps-data">Waiting for PPS data...</div>
        <script>
            async function fetchData() {
                const gpsResponse = await fetch('/gps-data');
                const gpsData = await gpsResponse.json();
                document.getElementById('gps-data').innerHTML = `<pre>${JSON.stringify(gpsData, null, 2)}</pre>`;
                
                const ppsResponse = await fetch('/pps-data');
                const ppsData = await ppsResponse.json();
                document.getElementById('pps-data').innerHTML = `<pre>${JSON.stringify(ppsData, null, 2)}</pre>`;

                setTimeout(fetchData, 500);  // 更新频率为1秒
            }
            fetchData(); // 初始化调用
        </script>
    '''

@app.route('/gps-data')
def gps_data():
    for new_data in gps_socket:
        if new_data:
            try:
                data = json.loads(new_data)
                if data.get('class') == 'TPV':
                    return jsonify(data)
            except json.JSONDecodeError:
                print("GPSd received invalid JSON")
    return jsonify({'error': 'No TPV data available'})

@app.route('/pps-data')
def pps_data():
    for new_data in gps_socket:
        if new_data:
            try:
                data = json.loads(new_data)
                if data.get('class') == 'PPS':
                    return jsonify(data)
            except json.JSONDecodeError:
                print("GPSd received invalid JSON")
    return jsonify({'error': 'No PPS data available'})

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0')