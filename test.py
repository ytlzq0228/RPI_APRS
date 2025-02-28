import gps  # 导入gps模块

# 创建一个gps会话
session = gps.gps("localhost", "2947")
session.stream(gps.WATCH_ENABLE | gps.WATCH_NEWSTYLE)

try:
    while True:
        try:
            report = session.next()  # 从gpsd获取下一条报告
            # 检查报告是否是NMEA原始数据
            if report['class'] == 'RAW' and 'nmea' in report:
                print(report['nmea'])  # 打印NMEA原始句子
        except KeyError:
            pass  # 忽略关键字错误
        except KeyboardInterrupt:
            break  # 允许手动中断程序
        except StopIteration:
            session = None
            print("GPSD has terminated")
except Exception as e:
    print("Error occurred:", e)