import requests
from json.decoder import JSONDecodeError


# 端口参数封装
def __detection__(response) -> dict or bool:
    if response.status_code == 200:
        try:
            return response.json()
        except JSONDecodeError:
            return None
    else:
        return None


# 验证账号密码是否填写正确
def check_passable(user: dict) -> dict or bool:
    """验证账号密码是否正确"""
    url = 'http://yao.qinse.top:8888' + '/cpdaily/api/item/verity_cpdaily_account'

    data = {
        'username': user.get('username'),
        'password': user.get('password'),
    }
    return __detection__(requests.post(url, data=data))


# 验证学号是否已注册
def check_register(username: str) -> dict or bool:
    """验证该学号是否已注册"""
    url = 'http://yao.qinse.top:8888' + '/cpdaily/api/item/verity_account_exist'
    data = {
        'username': username,
    }
    return __detection__(requests.post(url, data=data))


# 验证邮箱是否合法
def check_email(email: str) -> dict or bool:
    url = 'http://yao.qinse.top:8888' + '/cpdaily/api/item/verity_email_passable'
    data = {
        'email': email,
    }
    return __detection__(requests.post(url, data=data))

