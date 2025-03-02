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
        <h1>GPS Satellite SNR Chart</h1>
        <div>
            <canvas id="snrChart" width="800" height="400"></canvas>
        </div>
        <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
        <script>
            const ctx = document.getElementById('snrChart').getContext('2d');
            const snrChart = new Chart(ctx, {
                type: 'bar',
                data: {
                    labels: [],
                    datasets: []
                },
                options: {
                    scales: {
                        y: {
                            beginAtZero: true
                        }
                    }
                }
            });

            async function fetchSNRData() {
                const response = await fetch('/sky-data');
                const { satellites } = await response.json();
                snrChart.data.labels = satellites.map(sat => `PRN ${sat.PRN}`);
                satellites.forEach((sat, index) => {
                    if (!snrChart.data.datasets[index]) {
                        snrChart.data.datasets.push({
                            label: `SNR for PRN ${sat.PRN}`,
                            data: [],
                            backgroundColor: `rgba(${Math.random()*255}, ${Math.random()*255}, ${Math.random()*255}, 0.2)`,
                            borderColor: `rgba(${Math.random()*255}, ${Math.random()*255}, ${Math.random()*255}, 1)`,
                            borderWidth: 1
                        });
                    }
                    snrChart.data.datasets[index].data.push(sat.snr || 0);
                });
                snrChart.update();
                setTimeout(fetchSNRData, 5000);  // 每5秒更新一次
            }
            fetchSNRData();
        </script>
    '''

@app.route('/sky-data')
def sky_data():
    sky_records = []
    for new_data in gps_socket:
        if new_data:
            try:
                data = json.loads(new_data)
                if data.get('class') == 'SKY':
                    sky_records.append(data)
            except json.JSONDecodeError:
                print("GPSd received invalid JSON")
    if sky_records:
        # 处理多条SKY记录，选择最近的一条或者聚合它们
        latest_sky = max(sky_records, key=lambda x: x.get('time', ''))
        return jsonify({'satellites': latest_sky.get('satellites', [])})
    return jsonify({'error': 'No SKY data available'})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')