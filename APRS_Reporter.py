import sys
import os
import time
import re
import serial
import configparser
import aprs
import socket
import requests
import math
from datetime import datetime, timezone
from OLED_Driver.Display import OLED
from watchdog import reset_watchdog
from watchdog import boot_watchdog
import GNSS_NMAE
from Radio_GPIO import read_gpio
from save_log import save_log
import threading

from collections import deque
FAILED_QUEUE = deque(maxlen=2000) 


# 设置全局的socket超时时间，例如10秒
socket.setdefaulttimeout(5)

CONFIG_FILE='/etc/GPS_config.ini'
VERSION='main_0301.01'

# 读取配置文件
config = configparser.ConfigParser()
config.read(CONFIG_FILE)



def get_cpu_temperature():
	try:
		with open("/sys/class/thermal/thermal_zone0/temp", "r") as f:
			temp = int(f.read().strip()) / 1000.0  # 单位是毫摄氏度，需要转换
		return f"{temp:.2f}"
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
	global report_APRS_timestamp, disp_update_time, NMEA_timestamp, lat, lat_dir, lon, lon_dir, course, speed, altitude, GNSS_Type, SSID, CALLSIGN, APRS_PASSWORD, SSID_ICON, APRS_Server
	while True:
		try:
			# 确保 current_timestamp 已经被定义
			if 'current_timestamp' not in globals():
				time.sleep(1)  # 等待1秒再检查
				continue

			if current_timestamp-report_APRS_timestamp>=APRS_REPORT_INTERVAL and read_gpio(Radio_CONTROL_ENABLE,GPIO_PIN):
				report_APRS_timestamp=current_timestamp
				frame_text=(f'{SSID}>PYTHON,TCPIP*,qAC,{SSID}:!{lat}{lat_dir}/{lon}{lon_dir}{SSID_ICON}{course}/{speed}/A={altitude} APRS by RPI with GNSS {GNSS_Type} at UTC {NMEA_timestamp} {Message}').encode()
				callsign = CALLSIGN.encode('utf-8')
				password = APRS_PASSWORD.encode('utf-8')
				
				# 定义 APRS 服务器地址和端口（字节形式）
				server_host = APRS_Server.encode('utf-8')  # 使用 rotate.aprs2.net 服务器和端口 14580
				
				# 创建 TCP 对象并传入服务器信息
				a = aprs.TCP(callsign, password, servers=[server_host])
				a.start()
				aprs_return=a.send(frame_text)
				if aprs_return==len(frame_text)+2:
					save_log('APRS Report Good Length:%s'%aprs_return)
					disp_update_time=datetime.now()
				else:
					save_log('APRS Report Return:%s Frame Length: %s Retrying..'%(aprs_return,frame_text))
					disp_update_time=datetime.min
			time.sleep(1)  # 按照设定间隔等待
		except Exception as err:
			save_log(f"APRS Report Error: {err}")

def traccar_report():
	global report_traccar_timestamp, FAILED_QUEUE

	# 首次兜底
	try:
		report_traccar_timestamp
	except NameError:
		report_traccar_timestamp = 0

	# 简单的状态码是否重试的判定集合
	RETRYABLE_HTTP = {408, 429, 500, 502, 503, 504}
	still_wait_count=0

	while True:
		try:
			if 'current_timestamp' not in globals():
				time.sleep(1)
				continue

			# 1) 先处理重试队列：每轮只尝试 1 条，避免长时间阻塞
			now = time.time()
			if FAILED_QUEUE and FAILED_QUEUE[0].get("next_ts", 0) <= now:
				item = FAILED_QUEUE.popleft()
				payload_retry = item.get("payload", {})
				attempts = int(item.get("attempts", 0)) + 1
				try:
					resp = requests.post(TRACCAR_URL, data=payload_retry, timeout=3)  # 重试用短超时
					if 200 <= resp.status_code < 300:
						save_log(f"Traccar Retry OK: id={payload_retry.get('id')} "
								 f"lat={payload_retry.get('lat')} lon={payload_retry.get('lon')} "
								 f"status={resp.status_code}")
					elif resp.status_code in RETRYABLE_HTTP:
						backoff = min(600, 2 ** min(attempts, 10))
						FAILED_QUEUE.append({
							"payload": payload_retry,
							"attempts": attempts,
							"next_ts": now + backoff
						})
						save_log(f"Traccar Retry Defer: http={resp.status_code} "
								 f"attempts={attempts} next={int(backoff)}s "
								 f"queue={len(FAILED_QUEUE)}")
					else:
						save_log(f"Traccar Retry Drop: HTTP {resp.status_code} "
								 f"Body={str(resp.text).strip()[:200]}")
				except Exception as e:
					backoff = min(600, 2 ** min(attempts, 10))
					FAILED_QUEUE.append({
						"payload": payload_retry,
						"attempts": attempts,
						"next_ts": now + backoff
					})
					save_log(f"Traccar Retry Error: {e}; "
							 f"attempts={attempts} next={int(backoff)}s "
							 f"queue={len(FAILED_QUEUE)}")


			# 移动状态逻辑+新点上报
			#if (float(speed) > STILL_SPEED_THRESHOLD and current_timestamp - report_traccar_timestamp >= TRACCAR_REPORT_INTERVAL) or current_timestamp - report_traccar_timestamp >= STILL_LOG_INTERVAL:
			# 2) 到上报周期则发送新点
			if current_timestamp - report_traccar_timestamp >= TRACCAR_REPORT_INTERVAL:
				report_traccar_timestamp = current_timestamp

				lat = GPSd_raw_data.get("lat")
				lon = GPSd_raw_data.get("lon")
				if lat is None or lon is None:
					time.sleep(1)
					continue

				# 时间戳
				ts = datetime.utcnow().replace(tzinfo=timezone.utc).isoformat().replace("+00:00", "Z")
				payload={"id": str(SSID),"event":"heartbeat"}
				still_wait_count+=1
				if float(speed) > STILL_SPEED_THRESHOLD or still_wait_count>60:
					still_wait_count=0
					payload = {
						"id": str(SSID),
						"lat": f"{float(lat):.7f}",
						"lon": f"{float(lon):.7f}",
						"timestamp": ts,
						"deviceTemp": f"{float(get_cpu_temperature()):.1f}",
					}
	
					# m/s -> knots
					if GPSd_raw_data.get("speed") is not None:
						payload["speed"] = f"{float(GPSd_raw_data['speed']) * 3600 / 1852:.2f}"
	
					if GPSd_raw_data.get("track") is not None:
						payload["bearing"] = f"{float(GPSd_raw_data['track']):.1f}"
	
					if GPSd_raw_data.get("alt") is not None:
						payload["altitude"] = f"{float(GPSd_raw_data['alt']):.1f}"
	
					if GPSd_raw_data.get("eph") is not None:
						payload["accuracy"] = f"{float(GPSd_raw_data['eph']):.1f}"
	
				print(payload)
				try:
					resp = requests.post(TRACCAR_URL, data=payload, timeout=3)
					if 200 <= resp.status_code < 300:
						print(f"Traccar Report OK: id={SSID} payload: {payload}")
					elif resp.status_code in RETRYABLE_HTTP:
						FAILED_QUEUE.append({"payload": payload, "attempts": 0, "next_ts": time.time() + 1})
						save_log(f"Traccar Report Enqueue (HTTP {resp.status_code}) queue={len(FAILED_QUEUE)}")
					else:
						save_log(f"Traccar Report Fail: HTTP {resp.status_code} "
								 f"Body={str(resp.text).strip()[:200]}")
				except Exception as req_err:
					FAILED_QUEUE.append({"payload": payload, "attempts": 0, "next_ts": time.time() + 1})
					save_log(f"Traccar Report Request Error: {req_err}; queued={len(FAILED_QUEUE)}")

			time.sleep(0.1)

		except Exception as loop_err:
			save_log(f"Traccar Report Error: {loop_err}")
			time.sleep(1)


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
	STILL_LOG_INTERVAL=int(config['SFTP_Config']['STILL_LOG_INTERVAL'])
	STILL_SPEED_THRESHOLD=int(config['SFTP_Config']['STILL_SPEED_THRESHOLD'])

	TRACCAR_ENABLE=config.getboolean('Traccar_Config', 'enable')
	TRACCAR_URL=config['Traccar_Config']['TRACCAR_URL']
	TRACCAR_REPORT_INTERVAL=int(config['Traccar_Config']['TRACCAR_REPORT_INTERVAL'])

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
	save_log(f"Param STILL_LOG_INTERVAL:{STILL_LOG_INTERVAL}")
	save_log(f"Param STILL_SPEED_THRESHOLD:{STILL_SPEED_THRESHOLD}")


	disp_update_time=datetime.min
	log_timestamp=0
	report_APRS_timestamp=0
	report_traccar_timestamp=0
	last_still_log_time = 0
	altitude='000000'
	speed='000'
	course='000'
	GPSd_raw_data={}

	#--------------------
	aprs_thread = threading.Thread(target=aprs_report, name="aprs_report")
	aprs_thread.daemon = True
	aprs_thread.start()

	if TRACCAR_ENABLE:
		traccar_thread = threading.Thread(target=traccar_report, name="traccar_report")
		traccar_thread.daemon = True
		traccar_thread.start()
	#--------------------

	while True:
		try:
			while True:
				try:
					if GPS_Method=="COM":
						lat,lat_dir,lon,lon_dir,altitude,NMEA_timestamp,speed,course,GNSS_Type,lat_raw,lon_raw,GPS_Source = GNSS_NMAE.Get_GNSS_Position.COM(Test_Flag,com_port,baud_rate)
					if GPS_Method=="TCP":
						lat,lat_dir,lon,lon_dir,altitude,NMEA_timestamp,speed,course,GNSS_Type,lat_raw,lon_raw,GPS_Source = GNSS_NMAE.Get_GNSS_Position.TCP(Test_Flag,tcp_host,tcp_port)
					if GPS_Method=="GPSd":
						lat,lat_dir,lon,lon_dir,altitude,NMEA_timestamp,speed,course,GNSS_Type,lat_raw,lon_raw,GPS_Source,GPSd_raw_data = GNSS_NMAE.Get_GNSS_Position.GPSd(altitude,speed,course)
					break  # 成功获取GNSS数据时退出循环
				except Exception as err:
					save_log(f"Retrying get_gnss_position with {GPS_Method}")
					time.sleep(0.1)  # 等待0.1秒后重试
			current_timestamp=time.time()
			if OLED_Enable:
				try:
					lat_disp=lat_dir+" "+"%08.4f"%(float(lat_raw)/100)
					lon_disp=lon_dir+" "+"%08.4f"%(float(lon_raw)/100)
					if disp_update_time==datetime.min:
						time_diff="00"
					else:
						time_diff="%02.0f"%(datetime.now()-disp_update_time).total_seconds()
					invert=False
					OLED.OLED_Position(oled,lat_disp,lon_disp,GNSS_Type,disp_update_time.strftime('%H:%M:%S'),time_diff,speed,invert)
				except Exception as err:
					save_log(f"main_OLED: {err}")

			# 主判断逻辑
			if float(speed) > STILL_SPEED_THRESHOLD:
				# 移动状态，正常记录
				if current_timestamp - log_timestamp >= NMEA_LOG_INTERVAL:
					log_timestamp = current_timestamp
					save_log(f"gpx:{lat_raw,lat_dir,lon_raw,lon_dir,altitude,NMEA_timestamp,speed,course,GPS_Source,GNSS_Type,get_cpu_temperature(),get_uptime()}")
			else:
				if current_timestamp - log_timestamp >= STILL_LOG_INTERVAL:
					log_timestamp = current_timestamp
					save_log(f"gpx:{lat_raw,lat_dir,lon_raw,lon_dir,altitude,NMEA_timestamp,speed,course,GPS_Source,GNSS_Type,get_cpu_temperature(),get_uptime()}")


		except Exception as err:
			save_log(f"main: {err}")
			#raise
			#切记全部改完了之后这里把raise注释掉，仅调试期间使用






