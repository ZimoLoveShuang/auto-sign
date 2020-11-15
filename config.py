# coding=utf-8
import os
import random
import pytz

SECRET_NAME = 'CampusDailyAutoSign'

# ------------------------------
# 系统文件路径
# ------------------------------

ROOT_DIR_PROJECT = os.path.dirname(__file__)
ROOT_DIR_DATABASE = os.path.join(ROOT_DIR_PROJECT, 'database')
ROOT_DIR_FLASK = os.path.join(ROOT_DIR_PROJECT, 'myapp')
ROOT_PATH_CONFIG_USER = os.path.join(ROOT_DIR_DATABASE, 'config_user.csv')
ROOT_PATH_CACHE = os.path.join(ROOT_DIR_DATABASE, 'stu_info')

FLASK_PATH_FORMS = os.path.join(ROOT_DIR_FLASK, 'forms.py')
# ------------------------------
# 项目全局参数
# ------------------------------

# 消息验证模式
DEBUG = False

# 时区校准--BeijingTimeZone
TIME_ZONE_CN = pytz.timezone('Asia/Shanghai')
TIME_ZONE_US = pytz.timezone('America/New_York')
# 管理员账号,接收debug邮件,为系统鲁棒性考虑，该项强制(有效)填写 不能为空
MANAGER_EMAIL = 'example@temp.com'

TITLE = ['school', 'username', 'password', 'email']

# ------------------------------
# 用户组全局变量
# ------------------------------


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
