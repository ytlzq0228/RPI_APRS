from flask import Flask, jsonify
import gpsd

# 连接到本地GPSd
gpsd.connect()

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
                setTimeout(fetchGPSData, 1000);  // 每秒更新数据
            }
            fetchGPSData();
        </script>
    '''

@app.route('/gps-data')
def gps_data():
    try:
        packet = gpsd.get_current()
        data = {
            'latitude': packet.lat,
            'longitude': packet.lon,
            'altitude': packet.alt,
            'speed': packet.hspeed,
            'satellites': packet.sats
        }
    except Exception as e:
        data = {'error': str(e)}
    return jsonify(data)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')