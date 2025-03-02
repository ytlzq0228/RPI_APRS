from flask import Flask, jsonify
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
        <div id="gps-data"></div>
        <script>
            async function fetchGPSData() {
                const response = await fetch('/gps-data');
                const data = await response.json();
                document.getElementById('gps-data').innerHTML = `<pre>${JSON.stringify(data, null, 2)}</pre>`;
                setTimeout(fetchGPSData, 500);  // 每500ms更新数据
            }
            fetchGPSData();
        </script>
    '''

@app.route('/gps-data')

def gps_data():
    try:
        for new_data in gps_socket:  # 获取新的GPS数据
            if new_data:
                try:
                    data = json.loads(new_data)
                    
                except json.JSONDecodeError:
                    print("GPSd received invalid JSON")
            if data.get('class') == 'TPV':
                return jsonify(data)
    except Exception as e:
        data = {'error': str(e)}
    

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')