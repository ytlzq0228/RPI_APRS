import sys
import os
import time
import re
import serial
import configparser
import aprs
from datetime import datetime
import socket
from Display import OLED
from watchdog import reset_watchdog
from watchdog import boot_watchdog
import GNSS_NMAE
from Radio_GPIO import read_gpio
from save_log import save_log


# 设置全局的socket超时时间，例如10秒
socket.setdefaulttimeout(5)

CONFIG_FILE='/etc/GPS_config.ini'
VERSION='main_0218.01'

# 读取配置文件
config = configparser.ConfigParser()
config.read(CONFIG_FILE)

def get_cpu_temperature():
    try:
        with open("/sys/class/thermal/thermal_zone0/temp", "r") as f:
            temp = int(f.read().strip()) / 1000.0  # 单位是毫摄氏度，需要转换
        return f"{temp:.2f}°C"
    except Exception as e:
        return f"获取温度失败: {e}"

def get_uptime():
    try:
        # 方法 1：使用 uptime 命令
        uptime_cmd = os.popen("uptime -p").read().strip()
        
        return uptime_cmd
    except Exception as e:
        return f"获取开机时间失败: {e}"


def aprs_report():
    global report_timestamp, update_time, timestamp, lat, lat_dir, lon, lon_dir, course, speed, altitude, GNSS_Type, SSID, CALLSIGN, APRS_PASSWORD, SSID_ICON, APRS_Server
    while True:
        try:
            # 确保时间戳是最新的，并检查是否达到了上报间隔
            current_timestamp = float(timestamp)
            if current_timestamp - float(report_timestamp) >= APRS_REPORT_INTERVAL and read_gpio(Radio_CONTROL_ENABLE, GPIO_PIN):
                report_timestamp = timestamp  # 更新上报时间戳
                # 构建APRS消息
                frame_text = f'{SSID}>PYTHON,TCPIP*,qAC,{SSID}:!{lat}{lat_dir}/{lon}{lon_dir}{SSID_ICON}{course}/{speed}/A={altitude} APRS by RPI with GNSS Module using {GNSS_Type} at UTC {timestamp} {Message}'
                callsign = CALLSIGN.encode('utf-8')
                password = APRS_PASSWORD.encode('utf-8')
                server_host = APRS_Server.encode('utf-8')  # 将服务器地址转换为字节

                # 使用APRS库建立TCP连接并发送数据
                with aprs.TCP(callsign, password, servers=[server_host]) as a:
                    aprs_return = a.send(frame_text)
                    if aprs_return:
                        save_log(f'APRS Report Success: {aprs_return}')
                        update_time = datetime.now()
                    else:
                        save_log(f'APRS Report Failed: Retrying..')
                time.sleep(APRS_REPORT_INTERVAL)  # 按照设定间隔等待
        except Exception as err:
            save_log(f"APRS Report Error: {err}")


if __name__ == '__main__':

	Test_Flag=config.getboolean('Test_Flag', 'enable')
	SSID=config['SSID_Config']['SSID']
	CALLSIGN=config['SSID_Config']['CALLSIGN']
	APRS_PASSWORD=config['SSID_Config']['APRS_PASSWORD']
	Message=config['SSID_Config']['Message']
	SSID_ICON=config['SSID_Config']['ICON']
	APRS_Server=config['SSID_Config']['APRS_Server']
	OLED_Enable=config.getboolean('OLED_Config', 'OLED_Enable')
	OLED_Address=int(config.get('OLED_Config', 'OLED_Address'), 16)
	GPS_Device=config['GPS_Config']['GPS_Device']
	Radio_CONTROL_ENABLE=config['GPIO_CONTROL']['enable']
	GPIO_PIN=int(config['GPIO_CONTROL']['GPIO_PIN'])
	if GPS_Device[:8]=="/dev/tty":
		GPS_Method="COM"
		com_port=GPS_Device
		baud_rate=config.getint('GPS_Config', 'GPS_Option')
	elif GPS_Device=='GPSd':
		GPS_Method=GPS_Device
		GPS_addition_Source=config['GPS_Config']['GPS_Option'].split(',') if 'GPS_Option' in config['GPS_Config'] else []
		#for source in GPS_addition_Source:
		#	GNSS_NMAE.add_gps_source(source)
	else:
		GPS_Method="TCP"
		tcp_host=GPS_Device
		tcp_port=config.getint('GPS_Config', 'GPS_Option')

	OLED_Enable,oled=OLED.OLED_Init(OLED_Enable,OLED_Address)
	
	APRS_REPORT_INTERVAL=int(config['SSID_Config']['APRS_REPORT_INTERVAL'])
	NMEA_LOG_INTERVAL=int(config['SFTP_Config']['NMEA_LOG_INTERVAL'])

	save_log(f"APRS Repoeter {VERSION} Starting...")
	save_log("Get Config Params:")
	save_log(f"Param Test_Flag:{Test_Flag}")
	save_log(f"Param SSID:{SSID}")
	save_log(f"Param CALLSIGN:{CALLSIGN}")
	save_log(f"Param APRS_PASSWORD:{APRS_PASSWORD}")
	save_log(f"Param Message:{Message}")
	save_log(f"Param SSID_ICON:{SSID_ICON}")
	save_log(f"Param APRS_Server:{APRS_Server}")
	save_log(f"Param OLED_Enable:{OLED_Enable}")
	save_log(f"Param OLED_Address:{OLED_Address}")
	save_log(f"Param GPS_Device:{GPS_Device}")
	save_log(f"Param Radio_CONTROL_ENABLE:{Radio_CONTROL_ENABLE}")
	save_log(f"Param GPIO_PIN:{GPIO_PIN}")
	save_log(f"Param APRS_REPORT_INTERVAL:{APRS_REPORT_INTERVAL}")
	save_log(f"Param NMEA_LOG_INTERVAL:{NMEA_LOG_INTERVAL}")

	update_time=datetime.min
	update_timestamp=report_timestamp='0'
	altitude='000000'
	speed='000'
	course='000'
	#--------------------
	aprs_thread = threading.Thread(target=aprs_report)
    aprs_thread.daemon = True  # 设为守护线程，确保主程序退出时线程也会退出
    aprs_thread.start()
	#--------------------
	while True:
		try:
			while True:
				try:
					if GPS_Method=="COM":
						lat,lat_dir,lon,lon_dir,altitude,timestamp,speed,course,GNSS_Type,lat_raw,lon_raw,GPS_Source = GNSS_NMAE.Get_GNSS_Position.COM(Test_Flag,com_port,baud_rate)
					if GPS_Method=="TCP":
						lat,lat_dir,lon,lon_dir,altitude,timestamp,speed,course,GNSS_Type,lat_raw,lon_raw,GPS_Source = GNSS_NMAE.Get_GNSS_Position.TCP(Test_Flag,tcp_host,tcp_port)
					if GPS_Method=="GPSd":
						lat,lat_dir,lon,lon_dir,altitude,timestamp,speed,course,GNSS_Type,lat_raw,lon_raw,GPS_Source = GNSS_NMAE.Get_GNSS_Position.GPSd(altitude,speed,course)
					break  # 成功获取GNSS数据时退出循环
				except Exception as err:
					save_log(f"Retrying get_gnss_position with {GPS_Method}")
					time.sleep(0.1)  # 等待0.1秒后重试
			
			if OLED_Enable:
				try:
					lat_disp=lat_dir+" "+"%08.4f"%(float(lat_raw)/100)
					lon_disp=lon_dir+" "+"%08.4f"%(float(lon_raw)/100)
					if update_time==datetime.min:
						time_diff="00"
					else:
						time_diff="%02.0f"%(datetime.now()-update_time).total_seconds()
					invert=False
					OLED.OLED_Position(oled,lat_disp,lon_disp,GNSS_Type,update_time.strftime('%H:%M:%S'),time_diff,speed,invert)
				except Exception as err:
					save_log(f"main_OLED: {err}")

			if float(timestamp)-float(update_timestamp)>=NMEA_LOG_INTERVAL:
				update_timestamp=timestamp
				save_log(f"gpx:{lat_raw,lat_dir,lon_raw,lon_dir,altitude,timestamp,speed,course,GPS_Source,GNSS_Type,get_cpu_temperature(),get_uptime()}")

			global report_timestamp, update_time, timestamp, lat, lat_dir, lon, lon_dir, course, speed, altitude, GNSS_Type, SSID, CALLSIGN, APRS_PASSWORD, SSID_ICON, APRS_Server

			#if float(timestamp)-float(report_timestamp)>=APRS_REPORT_INTERVAL and read_gpio(Radio_CONTROL_ENABLE,GPIO_PIN):
			#	report_timestamp=timestamp
			#	frame_text=(f'{SSID}>PYTHON,TCPIP*,qAC,{SSID}:!{lat}{lat_dir}/{lon}{lon_dir}{SSID_ICON}{course}/{speed}/A={altitude} APRS by RPI with GNSS Module using {GNSS_Type} at UTC {timestamp} {Message}').encode()
			#	callsign = CALLSIGN.encode('utf-8')
			#	password = APRS_PASSWORD.encode('utf-8')
			#	
			#	# 定义 APRS 服务器地址和端口（字节形式）
			#	server_host = APRS_Server.encode('utf-8')  # 使用 rotate.aprs2.net 服务器和端口 14580
			#	
			#	# 创建 TCP 对象并传入服务器信息
			#	a = aprs.TCP(callsign, password, servers=[server_host])
			#	a.start()
			#	aprs_return=a.send(frame_text)
			#	if aprs_return==len(frame_text)+2:
			#		save_log('APRS Report Good Length:%s'%aprs_return)
			#		update_time=datetime.now()
			#	else:
			#		save_log('APRS Report Return:%s Frame Length: %s Retrying..'%(aprs_return,frame_text))
			#		update_time=datetime.min

		except Exception as err:
			save_log(f"main: {err}")
			#raise
			#切记全部改完了之后这里把raise注释掉，仅调试期间使用






