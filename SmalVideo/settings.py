# 短视频配置文件
import platform

# 本地mysql配置信息

mysql_host = "127.0.0.1"
mysql_user = "root"
mysql_password = "123456"
mysql_port = 3306
mysql_db = "video"


SYSTEM_STATUS=True if "windows" in platform.platform().lower() else False #操作系统
LOGPATH = "./logs/"