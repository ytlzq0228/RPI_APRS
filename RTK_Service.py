import gps

# 连接到gpsd
session = gps.gps("localhost", "2947")
session.stream(gps.WATCH_ENABLE | gps.WATCH_NEWSTYLE)

while True:
    try:
        report = session.next()
        # 检查报告类型是否为TPV，表明位置数据
        if report['class'] == 'TPV':
            if hasattr(report, 'lat') and hasattr(report, 'lon'):
                # 这里生成GGA消息，具体格式依据你的需求调整
                gga_data = f"$GPGGA,,,,{report.lat},{report.lon},1,08,0.9,{report.alt},M,,M,,*47"
                print(gga_data)
                # 发送GGA数据到NTRIP服务器的代码放在这里
    except KeyError:
        pass
    except KeyboardInterrupt:
        quit()
    except StopIteration:
        session = None
        print("GPSD has terminated")