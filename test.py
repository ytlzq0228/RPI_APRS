import gps
import time

def connect_gpsd():
    """连接到 GPSd 服务"""
    try:
        # 创建 GPS 对象并连接到 GPSd
        session = gps.gps(host="127.0.0.1", port=2947, mode=gps.WATCH_ENABLE)
        print("Connected to GPSd")
        return session
    except Exception as e:
        print(f"Failed to connect to GPSd: {e}")
        return None

def fetch_gps_data(session):
    """从 GPSd 获取数据"""
    try:
        while True:
            # 等待 GPS 数据更新
            session.poll()

            # 检查是否有有效定位信息
            if session.fix.mode >= 2:  # 2D 或 3D 定位
                latitude = session.fix.latitude
                longitude = session.fix.longitude
                altitude = session.fix.altitude if session.fix.mode == 3 else None
                speed = session.fix.speed  # 单位为 m/s
                timestamp = session.fix.time

                print(f"Time: {timestamp}")
                print(f"Latitude: {latitude}°")
                print(f"Longitude: {longitude}°")
                print(f"Altitude: {altitude} m")
                print(f"Speed: {speed} m/s")
                
                time.sleep(1)
            else:
                print("Waiting for GPS signal...")
                time.sleep(1)
    except KeyboardInterrupt:
        print("Exiting...")
    except Exception as e:
        print(f"Error fetching GPS data: {e}")

if __name__ == "__main__":
    gpsd_session = connect_gpsd()
    if gpsd_session:
        fetch_gps_data(gpsd_session)