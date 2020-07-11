import sys
import requests
import json
import uuid
import base64
from pyDes import des, CBC, PAD_PKCS5
from datetime import datetime, timedelta, timezone
import yaml
import time


# 读取yml配置
def getYmlConfig(yaml_file='config.yml'):
    file = open(yaml_file, 'r', encoding="utf-8")
    file_data = file.read()
    file.close()
    config = yaml.load(file_data, Loader=yaml.FullLoader)
    return dict(config)


# DES加密
def DESEncrypt(s, key='XCE927=='):
    iv = b"\x01\x02\x03\x04\x05\x06\x07\x08"
    k = des(key, CBC, iv, pad=None, padmode=PAD_PKCS5)
    encrypt_str = k.encrypt(s)
    return base64.b64encode(encrypt_str).decode()


# DES解密
def DESDecrypt(s, key='XCE927=='):
    s = base64.b64decode(s)
    iv = b"\x01\x02\x03\x04\x05\x06\x07\x08"
    k = des(key, CBC, iv, pad=None, padmode=PAD_PKCS5)
    return k.decrypt(s)


# 全局配置
config = getYmlConfig()
session = requests.session()
user = config['user']
# Cpdaily-Extension
extension = {
    "lon": user['lon'],
    "model": "PCRT00",
    "appVersion": "8.0.8",
    "systemVersion": "4.4.4",
    "userId": user['username'],
    "systemName": "android",
    "lat": user['lat'],
    "deviceId": str(uuid.uuid1())
}

user['SessionToken'] = DESEncrypt('')
user['CpdailyInfo'] = DESEncrypt(json.dumps(extension))
host = 'fzu.cpdaily.com'


# 获取当前utc时间，并格式化为北京时间
def getTimeStr():
    utc_dt = datetime.utcnow().replace(tzinfo=timezone.utc)
    bj_dt = utc_dt.astimezone(timezone(timedelta(hours=8)))
    return bj_dt.strftime("%Y-%m-%d %H:%M:%S")


# 输出调试信息，并及时刷新缓冲区
def log(content):
    print(getTimeStr() + ' ' + str(content))
    sys.stdout.flush()


# 通过手机号和验证码进行登陆
def login():
    # 1.获取验证码
    url = 'https://www.cpdaily.com/v6/auth/authentication/mobile/messageCode'
    headers = {
        'SessionToken': user['SessionToken'],
        'clientType': 'cpdaily_student',
        'tenantId': 'fzu',
        'User-Agent': 'Mozilla/5.0 (Linux; Android 4.4.4; PCRT00 Build/KTU84P) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/33.0.0.0 Safari/537.36 okhttp/3.8.1',
        'deviceType': '1',
        'CpdailyStandAlone': '0',
        'CpdailyInfo': user['CpdailyInfo'],
        'RetrofitHeader': '8.0.8',
        'Cache-Control': 'max-age=0',
        'Content-Type': 'application/json; charset=UTF-8',
        'Host': 'www.cpdaily.com',
        'Connection': 'Keep-Alive',
        'Accept-Encoding': 'gzip'
    }
    params = {
        'mobile': DESEncrypt(str(user['tellphone']))
    }
    res = session.post(url=url, headers=headers, data=json.dumps(params))
    log(res.text)
    log(session.cookies)
    code = input("请输入验证码：")

    # 2.登陆
    url = 'https://www.cpdaily.com/v6/auth/authentication/mobileLogin'
    params = {
        'loginToken': str(code),
        'loginId': str(user['tellphone'])
    }
    log(params)
    res = session.post(url=url, headers=headers, data=json.dumps(params))
    log(res.text)
    data = res.json()['data']
    # 处理登陆后的token等
    sessionToken = data['sessionToken']
    tgc = data['tgc']
    amp = {
        'AMP1': [{
            'value': sessionToken,
            'name': 'sessionToken'
        }],
        'AMP2': [{
            'value': sessionToken,
            'name': 'sessionToken'
        }]
    }

    # 3.更新acw_tc
    url = 'https://open.cpdaily.com/wec-open-app/app/userAppListGroupByCategory'
    # 更新headers
    del headers['Content-Type']
    headers['Host'] = 'open.cpdaily.com'
    headers['TGC'] = DESEncrypt(json.dumps(tgc))
    headers['AmpCookies'] = DESEncrypt(json.dumps(amp))
    user['SessionToken'] = headers['SessionToken'] = DESEncrypt(json.dumps(sessionToken))
    session.get(url=url, headers=headers)
    log(session.cookies)

    # 4.获取MOD_AUTH_CAS
    url = 'https://fzu.cpdaily.com/wec-counselor-sign-apps/stu/mobile/index.html?timestamp=' + str(
        int(round(time.time() * 1000)))
    # 更新headers
    headers = {
        'Host': 'fzu.cpdaily.com',
        'Connection': 'keep-alive',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'User-Agent': 'Mozilla/5.0 (Linux; Android 4.4.4; PCRT00 Build/KTU84P) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/33.0.0.0 Safari/537.36 cpdaily/8.0.8 wisedu/8.0.8',
        'Accept-Encoding': 'gzip,deflate',
        'Accept-Language': 'zh-CN,en-US;q=0.8',
        'X-Requested-With': 'com.wisedu.cpdaily',
    }

    session.get(url=url, headers=headers)
    log(session.cookies)
    print('==============CpdailyInfo填写到index.py==============')
    print(user['CpdailyInfo'])
    print('==============Cookies填写到index.py==============')
    print(requests.utils.dict_from_cookiejar(session.cookies))


if __name__ == '__main__':
    # log(config)
    # login()
    login()
