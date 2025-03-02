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
        <h1>GPS and PPS Data</h1>
        <h2>GPS Data</h2>
        <table id="gps-data">
            <tr>
                <th>Latitude</th>
                <th>Longitude</th>
                <th>Altitude</th>
                <th>Speed</th>
                <th>Time</th>
            </tr>
        </table>
        <h2>PPS Data</h2>
        <table id="pps-data">
            <tr>
                <th>Time</th>
                <th>Precision</th>
            </tr>
        </table>
        <script>
            async function fetchData() {
                const gpsResponse = await fetch('/gps-data');
                const gpsData = await gpsResponse.json();
                const gpsTable = document.getElementById('gps-data');
                if (gpsData.class === 'TPV') {
                    gpsTable.innerHTML = `
                        <tr>
                            <th>Latitude</th>
                            <th>Longitude</th>
                            <th>Altitude</th>
                            <th>Speed</th>
                            <th>Time</th>
                        </tr>
                        <tr>
                            <td>${gpsData.lat || 'N/A'}</td>
                            <td>${gpsData.lon || 'N/A'}</td>
                            <td>${gpsData.alt || 'N/A'} m</td>
                            <td>${gpsData.speed || 'N/A'} m/s</td>
                            <td>${gpsData.time || 'N/A'}</td>
                        </tr>
                    `;
                }
                
                const ppsResponse = await fetch('/pps-data');
                const ppsData = await ppsResponse.json();
                const ppsTable = document.getElementById('pps-data');
                if (ppsData.class === 'PPS') {
                    ppsTable.innerHTML = `
                        <tr>
                            <th>Time</th>
                            <th>Precision</th>
                        </tr>
                        <tr>
                            <td>${ppsData.time || 'N/A'}</td>
                            <td>${ppsData.precision || 'N/A'}</td>
                        </tr>
                    `;
                }

                setTimeout(fetchData, 1000);  // 更新频率为1秒
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
    app.run(debug=True, host='0.0.0.0')