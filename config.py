# coding=utf-8
import os
import random
import pytz

# ------------------------------
# 系统文件路径
# ------------------------------

ROOT_DIR_PROJECT = os.path.dirname(__file__)
ROOT_DIR_DATABASE = os.path.join(ROOT_DIR_PROJECT, 'database')
ROOT_PATH_CONFIG_USER = os.path.join(ROOT_DIR_DATABASE, 'config_user.csv')

# ------------------------------
# 脚本全局参数
# ------------------------------

# 消息验证模式
DEBUG = False

# 时区校准--BeijingTimeZone
TIME_ZONE_CN = pytz.timezone('Asia/Shanghai')

# 管理员账号，接收debug邮件
MANAGER_EMAIL = 'xyh.hainanu@qq.com'

TITLE = ['username', 'password', 'email', 'stu_id', 'stu_name', 'sex', 'grade', 'dept', 'major', 'cls']

# ------------------------------
# 用户组全局变量
# ------------------------------

LOGGING_API = "http://www.zimo.wiki:8080/wisedu-unified-login-api-v1.0/api/login"
LONGITUDE: str = f'{round(random.uniform(110.331974, 110.339974), 6)}'
LATITUDE: str = f'{round(random.uniform(20.061120, 20.066120), 6)}'
SCHOOL: str = '海南大学'
ADDRESS: str = '中国海南省海口市美兰区云翮南路'
ABNORMAL_REASON = None
QnA = {
    '早晨您的体温是': '37.2℃及以下',
    '您中午的体温是': '37.2℃及以下',
    '晚上您的体温是': '37.2℃及以下',
}
