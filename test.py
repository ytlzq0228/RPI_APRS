from gps3 import gps3

def fetch_gps_data():
    """通过 gps3 获取 GPS 数据"""
    gps_socket = gps3.GPSDSocket()
    data_stream = gps3.DataStream()
    
    # 连接到 GPSd
    gps_socket.connect(host="127.0.0.1", port=2947)
    gps_socket.watch()

    try:
        for new_data in gps_socket:
            if new_data:
                data_stream.unpack(new_data)
                latitude = data_stream.TPV['lat']
                longitude = data_stream.TPV['lon']
                altitude = data_stream.TPV['alt']
                speed = data_stream.TPV['speed']
                timestamp = data_stream.TPV['time']

                if latitude and longitude:
                    print(f"Time: {timestamp}")
                    print(f"Latitude: {latitude}°")
                    print(f"Longitude: {longitude}°")
                    print(f"Altitude: {altitude} m")
                    print(f"Speed: {speed} m/s")
                else:
                    print("Waiting for GPS signal...")
    except KeyboardInterrupt:
        print("Exiting...")
    except Exception as e:
        print(f"Error fetching GPS data: {e}")

if __name__ == "__main__":
    fetch_gps_data()