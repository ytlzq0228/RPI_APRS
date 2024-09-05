# 使用串口GPS模块上报APRS信息
## NMEA读取GPGGS获取位置信息
## NMEA读取GPRMA获取航向和航速信息
## Python aprs模块上报GPS信息
技术指导参考：
[【逗老师的无线电】骚活，GPS热点盒子自动上报APRS位置](https://blog.csdn.net/ytlzq0228/article/details/130228867)
# 三、上报APRS数据
## 1、APRS基本上报方式
HTTP方式连接：
服务器地址：china.aprs2.net
服务器端口：14580

telnet上去之后输入
user XXXXXX pass YYYYY(换行回车符)

XXXXXX为你的呼号，YYYYY为你呼号的passcode
passcode的生成方式google一下，就有好多在线工具可以帮忙生成。
下面的网站就是一个可以生成passcode的站点

[https://apps.magicbug.co.uk/passcode/index.php](https://apps.magicbug.co.uk/passcode/index.php)
![在这里插入图片描述](https://i-blog.csdnimg.cn/blog_migrate/e5cb7c8ddc8d28bbef41d2295da14b7f.png)
![在这里插入图片描述](https://i-blog.csdnimg.cn/blog_migrate/a210b145ce89e574491287a1b5468fea.png)
哎，这玩意就是这样，明文生成密码，还没有鉴权，所以，大家自觉遵守道德规范就好。

输入user和pass之后，等待几秒（我设置是等待5秒），收到验证通过的反馈后
![在这里插入图片描述](https://i-blog.csdnimg.cn/blog_migrate/a84c2a66baac2ed24f8a35a662ecc347.png)

之后再发送符合APRS的数据帧字符串即可。
例如：

`
BI1FQO-13>APDG03,TCPIP*,qAC,BI1FQO-CS:!4008.22ND11632.89E&/A=000000440 HelloWorld!
`

![在这里插入图片描述](https://i-blog.csdnimg.cn/blog_migrate/e6ef0a20563d83e1df967917e1c805cc.png)
之后再去APRS网站上查一下，诶嘿，这不就出来啦
![在这里插入图片描述](https://i-blog.csdnimg.cn/blog_migrate/4962ce2335d7f7216333bf755c756ef2.png)


## 2、脚本上报
Python中有一个包，名字就叫aprs，导入此包之后方便了很多，无需构建HTTP Request报文，只需调用时候传递拼好的字符串即可。

```
pip install aprs
```
然后，写个sheel脚本，开机自动运行，就OKK啦
这个小项目基本就这样了，对于开发者来说，这个项目非常简单。但是对于HAM们来说，如果理解起来费劲的话，也可以私信联系我帮忙处理。
这里是**BI1FQO**，DMR ID：**4606666**，希望各位HAM通联愉快！
