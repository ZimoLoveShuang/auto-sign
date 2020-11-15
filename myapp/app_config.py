import sys

SECRET_KEY = 'CampusDailyAutoSign'

# ------------------------------
# 路由接口
# ------------------------------

# 快速注册
QUICK_START = '/cpdaily/api/item/quick_start'

# 验证今日校园账号（学号+密码）是否正确
VERITY_CPDAILY_ACCOUNT = '/cpdaily/api/item/verity_cpdaily_account'

# 验证该用户是否已在本项目数据库
VERITY_ACCOUNT_EXIST = '/cpdaily/api/item/verity_account_exist'

# 验证邮箱格式是否合法
VERITY_EMAIL_PASSABLE = '/cpdaily/api/item/verity_email_passable'

# 发送验证码
SEND_VERITY_CODE = '/hainanu/api/item/send_verify_code'

# 项目声明
TOS_ = '/cpdaily/api/item/tos'

# ------------------------------
# todo:部署参数:: 修改服务器ip
# ------------------------------
SERVER_HOST = 'master ip' if 'linux' in sys.platform else '127.0.0.1'
SERVER_PORT = '443' if 'linux' in sys.platform else '8080'
SERVER_HEADER = f'http://{SERVER_HOST}:{SERVER_PORT}'
