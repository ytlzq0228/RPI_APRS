import socket
import base64
from gps import gps, WATCH_ENABLE, WATCH_NEWSTYLE

def generate_gga(latitude, longitude, timestamp):
    # GGA消息生成，确保格式正确
    gga = f"GPGGA,{timestamp},{latitude:.6f},N,{longitude:.6f},E,1,12,1.0,0.0,M,0.0,M,,"
    checksum = 0
    for char in gga:
        checksum ^= ord(char)
    return f"${gga}*{checksum:02X}"

def send_gga_to_ntrip(gga, ntrip_socket):
    try:
        ntrip_socket.sendall(gga.encode('ascii') + b'\r\n')
        return True
    except socket.error as e:
        print(f"Socket error while sending GGA: {e}")
        return False

def connect_to_ntrip_server(user, password, server, port, mountpoint):
    while True:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(10)
            print(f"Attempting to connect to NTRIP server at {server}:{port}")
            s.connect((server, port))
            auth = f"{user}:{password}"
            auth_encoded = base64.b64encode(auth.encode('ascii')).decode('ascii')
            ntrip_request = f"GET /{mountpoint} HTTP/1.1\r\nHost: {server}:{port}\r\nAuthorization: Basic {auth_encoded}\r\nUser-Agent: PythonNtripClient/1.0\r\nAccept: */*\r\n\r\n"
            s.sendall(ntrip_request.encode('ascii'))
            resp = s.recv(1024)
            if resp:
                print(f"Server response: {resp.decode('ascii')}")
                if b'200 OK' in resp or b'ICY 200 OK' in resp:
                    print("Connected to NTRIP server successfully.")
                    return s
                else:
                    print(f"Failed to connect, server response: {resp.decode('ascii')}")
            else:
                print("No response received from server.")
        except Exception as e:
            print(f"Failed to connect to NTRIP server: {e}")
        print("Retrying in 5 seconds...")
        time.sleep(5)

def main():
    # 设置GPSD连接
    session = gps(mode=WATCH_ENABLE | WATCH_NEWSTYLE)
    ntrip_socket = connect_to_ntrip_server("qxymtq002", "c4bcfd9", "rtk.ntrip.qxwz.com", 8002, "AUTO")

    while True:
        try:
            report = session.next()
            if report['class'] == 'TPV':
                if hasattr(report, 'lat') and hasattr(report, 'lon'):
                    gga_message = generate_gga(report.lat, report.lon, report.time)
                    if send_gga_to_ntrip(gga_message, ntrip_socket):
                        response = ntrip_socket.recv(4096)
                        print(response.decode('ascii'))
        except KeyError:
            pass
        except StopIteration:
            session = None
            print("GPSD has terminated")
        except socket.error as e:
            print(f"Socket error: {e}")
            ntrip_socket.close()
            ntrip_socket = connect_to_ntrip_server("qxymtq002", "c4bcfd9", "rtk.ntrip.qxwz.com", 8002, "AUTO")
        except KeyboardInterrupt:
            print("Script stopped by user.")
            ntrip_socket.close()
            print("NTRIP connection closed.")
            break

if __name__ == '__main__':
    main()