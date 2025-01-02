import gps
import time

def connect_gpsd():
    """连接到 GPSd 服务"""
    try:
        # 创建 GPS 对象并连接到 GPSd
        session = gps.gps(host="127.0.0.1", port=2947)
        session.stream(gps.WATCH_ENABLE | gps.WATCH_NEWSTYLE)
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
            report = session.next()  # 获取下一条 GPS 数据

            # 检查是否是定位数据
            if report['class'] == 'TPV':
                latitude = getattr(report, 'lat', None)
                longitude = getattr(report, 'lon', None)
                altitude = getattr(report, 'alt', None)
                speed = getattr(report, 'speed', None)
                timestamp = getattr(report, 'time', None)

                print(f"Time: {timestamp}")
                print(f"Latitude: {latitude}°")
                print(f"Longitude: {longitude}°")
                print(f"Altitude: {altitude} m")
                print(f"Speed: {speed} m/s")

            time.sleep(1)  # 延迟 1 秒
    except KeyboardInterrupt:
        print("Exiting...")
    except StopIteration:
        print("GPSD has terminated")
    except Exception as e:
        print(f"Error fetching GPS data: {e}")

if __name__ == "__main__":
    gpsd_session = connect_gpsd()
    if gpsd_session:
        fetch_gps_data(gpsd_session)