还记得之前这个项目嘛，当时作为实验性项目，整了一个脚本在树莓派上运行，自动上报APRS位置。
[【逗老师的无线电】骚活，GPS热点盒子自动上报APRS位置](https://blog.csdn.net/ytlzq0228/article/details/130228867)
![在这里插入图片描述](https://i-blog.csdnimg.cn/direct/d4b51db08b01454f8f8e9e8609f6f7be.png)
当时这个项目写的，纯粹是为了技术验证。所以各种Bug哈哈哈
现在，经过1年多的各种优化之后，我们完善了这个项目，并致力于尽可能让各位可以简单的使用它

![在这里插入图片描述](https://i-blog.csdnimg.cn/direct/6ce0d72877b840fea050d68935511622.png)
项目地址传送门：
代码部分[**https://github.com/ytlzq0228/RPI_APRS**](https://github.com/ytlzq0228/RPI_APRS)

# 一、硬件
1、Raspberry OS，Pi-star OS等其他基于Debian派生的Linux系统均可以运行。
2、树莓派、香橙派、XX派，X86等，只要能运行上述操作系统的，都能跑。这个项目不挑硬件
3、串口GPS模块，或者TCP协议网络GPS服务器均可。只要支持NMEA语句的GPS设备，都能支持。
# 一、安装

```bash
cd ~
sudo git clone https://github.com/ytlzq0228/RPI_APRS.git
cd RPI_APRS
sudo ./install.sh
```
# 二、准备配置文件

```bash
sudo nano /etc/GPS_config.ini 
```

```clike
[Test_Flag]
enable=False
#测试模式，无GPS信号时，串口和TCP模式下可以模拟定位，GPSd模式下无效/Test mode: When there is no GPS signal, simulation is available in serial and TCP modes, but not in GPSd mode
#模拟定位坐标4104.6300,N,10618.2178,E。要改的话自己去代码里改/Simulated location: 4104.6300,N,10618.2178,E. Modify in the code if needed

[SSID_Config]
SSID=BI1FQO-ZZ
CALLSIGN=BI1FQO
APRS_PASSWORD=20898
#密码生成/Password generation: https://apps.magicbug.co.uk/passcode/index.php
ICON = I
Message=Test

[OLED_Config]
OLED_Enable=True
OLED_Address=0x3c
#OLED配置/OLED configuration
#支持0.96寸OLED，默认I2C地址0x3c，支持修改地址/Support 0.96-inch OLED, default I2C address 0x3c, support address modification

[SFTP_Config]
REMOTE_USER=
REMOTE_HOST=
REMOTE_DIR=
REMOTE_PORT=
#SFTP配置/SFTP configuration
#支持定时将日志文件发送到SFTP服务器/Supports sending log files to SFTP server at regular intervals

[GPS_Config]
GPS_Device=GPSd
GPSd_TCP_SOURCE=tcp://10.0.6.116:12321
#使用GPSd服务(推荐)/Using GPSd Service (recommended)

#GPS_Device="/dev/ttyAMA0"
#GPS_Option=115200
#使用串口GPS模块/Using serial GPS module

#GPS_Device=10.0.6.116
#GPS_Option=12321
#使用TCP GPS服务器/Using TCP GPS server

[PROJECT_PATH]
PROJECT_DIR=/etc/RPI_APRS
#项目路径配置/Project path configuration

[GPIO_CONTROL]
enable=True
GPIO_PIN=20
#支持通过GPIO控制是否上报APRS，默认配置BCM GPIO 20，对应树莓派PIN 38。低电平有效。
#浮空状态不上报APRS，但仍然会记录GPS日志。
```

如果使用GPSd服务获取定位，需要配置GPSd服务

```bash
sudo nano /etc/default/gpsd 
```

```shell
# Devices gpsd should collect to at boot time.
# They need to be read/writeable, either by user gpsd or the group dialout.
DEVICES="/dev/ttyAMA0"

# Other options you want to pass to gpsd
GPSD_OPTIONS="-n -G -b -s 115200"
#注意串口波特率与模块波特率匹配/Note that the serial port baud rate matches the GPS module baud rate

# Automatically hot add/remove USB GPS devices via gpsdctl
USBAUTO="false"
START_DAEMON="true"
GPSD_SOCKET="/var/run/gpsd.sock"
```
修改完成之后重启gpsd
```bash
sudo systemctl restart gpsd
```


# 三、运行状态
## 1、aprs_reporter.service
目前这个脚本已经写成了服务，检查服务是否正常运行

```bash
sudo systemctl status aprs_reporter.service
```
![在这里插入图片描述](https://i-blog.csdnimg.cn/direct/8358488357964460bda07fd4e5c54d8f.png)
检查日志，日志位于/var/log/GPS_NMEA.log
![在这里插入图片描述](https://i-blog.csdnimg.cn/direct/14562fb86baf421abdd921f566cc6516.png)
## 2、GPSd
如果获取GPS的模式为GPSd，可以使用gpsmon来测试GPSd服务时候正常运行，是否可以获取GPS坐标

```xml
gpsmon
```
![在这里插入图片描述](https://i-blog.csdnimg.cn/direct/8b8cbafc5da24fbab5b14d5361983f50.png)
# 四、GPSd使用TCP GPS源
我估计很少有人这么用，但是这里还是特别说明一下，如果使用TCP网络GPS服务器。
GPSd支持通过TCP连接支持网络功能的GPS模块，市面上也有类似的模块可以选择。
几乎所有支持GNSS的DTU数传模块，都可以通过TCP透传NMEA语句。
![在这里插入图片描述](https://i-blog.csdnimg.cn/direct/f91ac112717440a381ec580542e5979a.png)
连接这类模块的时候，在GPSd的配置文件里可以写

```clike
DEVICES="tcp://10.0.6.116:12321"
```
但是这种GPSd没有丢失TCP连接后的重连机制，所以本项目提供了检测TCP连接，并在断连后尝试重连。
如果需要添加TCP GPS模块，编辑/etc/GPS_config.ini
```bash
sudo nano /etc/GPS_config.ini 
```
修改如下配置，其中GPSd_TCP_SOURCE中写TCP服务器地址
```clike
[GPS_Config]
GPS_Device=GPSd
GPSd_TCP_SOURCE=tcp://10.0.6.116:12321
```
编辑完成后添加一个检测服务
```shell
cd /etc/RPI_APRS/
sudo ./monitor_tcp_gps_add_service.sh 
```
监控服务会根据GPSd输出的TPV语句来检测TCP GPS源是否存活，并在检测到TCP GPS源离线后重新添加该GPS源
![在这里插入图片描述](https://i-blog.csdnimg.cn/direct/6f1423ac064c4304a38de82ffe50b9b4.png)
# 搞定
这个项目抠抠搜搜整了1年，现在终于可以向各位交出一个完美的成品了。
谢谢各位的支持
这里是BI1FQO，DMR ID：4606666，希望各位HAM通联愉快！