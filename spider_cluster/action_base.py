import json
import base64
from datetime import datetime

import requests
import uuid
from pyDes import des, CBC, PAD_PKCS5
from middleware.info_manager import send_email

from config import ADDRESS, LONGITUDE, LATITUDE, QnA, LOGGING_API, ABNORMAL_REASON, TIME_ZONE_CN, DEBUG


# 交互仓库
class ActionBase(object):
    """交互仓库"""

    for_hainanu_server = True
    silence = False

    # 获取今日校园api
    @staticmethod
    def get_campus_daily_apis(user):
        if ActionBase.for_hainanu_server:
            return {
                'host': 'hainanu.campusphere.net',
                'login-url': 'https://authserver.hainanu.edu.cn/authserver/login?service=https%3A%2F%2Fhainanu.campusphere.net%2Fportal%2Flogin'
            }

    # 登陆并获取session
    @staticmethod
    def get_session(user, apis):
        params = {
            'login_url': apis['login-url'],
            'needcaptcha_url': '',
            'captcha_url': '',
            'username': user['username'],
            'password': user['password']
        }

        cookies = dict()
        res = requests.post(url=LOGGING_API, data=params, verify=not DEBUG)
        # cookieStr可以使用手动抓包获取到的cookie，有效期暂时未知，请自己测试
        # cookieStr = str(res.json()['cookies'])
        cookieStr = str(res.json()['cookies'])
        ActionBase.log(cookieStr)
        if cookieStr == 'None':
            return None

        # 解析cookie
        for line in cookieStr.split(';'):
            name, value = line.strip().split('=', 1)
            cookies[name] = value
        session = requests.session()
        session.cookies = requests.utils.cookiejar_from_dict(cookies, cookiejar=None, overwrite=True)
        return session

    # 获取最新未签到任务
    @staticmethod
    def get_unsigned_tasks(session, apis):
        headers = {
            'Accept': 'application/json, text/plain, */*',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36',
            'content-type': 'application/json',
            'Accept-Encoding': 'gzip,deflate',
            'Accept-Language': 'zh-CN,en-US;q=0.8',
            'Content-Type': 'application/json;charset=UTF-8'
        }
        # 第一次请求每日签到任务接口，主要是为了获取MOD_AUTH_CAS
        res = session.post(
            url='https://{host}/wec-counselor-sign-apps/stu/sign/queryDailySginTasks'.format(host=apis['host']),
            headers=headers, data=json.dumps({}), verify=not DEBUG)

        # 第二次请求每日签到任务接口，拿到具体的签到任务
        res = session.post(
            url='https://{host}/wec-counselor-sign-apps/stu/sign/queryDailySginTasks'.format(host=apis['host']),
            headers=headers, data=json.dumps({}), verify=not DEBUG)

        # fixme:debug module-- response status code :404
        try:
            if len(res.json()['datas']['unSignedTasks']) < 1:
                pass
        except json.decoder.JSONDecodeError:
            ActionBase.log(
                f'the response of queryClass is None! ({res.status_code})|| Base on function(get_unsigned_tasks)')
            try:
                if res.status_code != 200:
                    ActionBase.log('the status code of response is ({})'.format(res.status_code))
                ActionBase.log('当前没有未签到任务')
            finally:
                return None

        latestTask = res.json()['datas']['unSignedTasks'][0]

        return {
            'signInstanceWid': latestTask['signInstanceWid'],
            'signWid': latestTask['signWid']
        }

    # 获取签到任务详情
    @staticmethod
    def get_detail_task(session, params, apis):
        headers = {
            'Accept': 'application/json, text/plain, */*',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36',
            'content-type': 'application/json',
            'Accept-Encoding': 'gzip,deflate',
            'Accept-Language': 'zh-CN,en-US;q=0.8',
            'Content-Type': 'application/json;charset=UTF-8'
        }
        res = session.post(
            url='https://{host}/wec-counselor-sign-apps/stu/sign/detailSignTaskInst'.format(host=apis['host']),
            headers=headers, data=json.dumps(params), verify=not DEBUG)
        data = res.json()['datas']
        return data

    # 填充表单
    @staticmethod
    def fill_form(task: dict, session, user, apis, ):
        form = {
            'longitude': LONGITUDE,
            'latitude': LATITUDE,
            'position': ADDRESS,
            'abnormalReason': ABNORMAL_REASON,
        }

        if ActionBase.for_hainanu_server:
            extraFields = task.get('extraField')
            if extraFields and extraFields.__len__() == 1:
                question = extraFields[0].get('title')
                answer = QnA[question]
                extraFieldItems = extraFields[0]['extraFieldItems']
                for extraFieldItem in extraFieldItems:
                    if extraFieldItem['content'] == answer:
                        form['extraFieldItems'] = [{'extraFieldItemValue': answer,
                                                    'extraFieldItemWid': extraFieldItem['wid']}]
        form['signPhotoUrl'] = ''
        form['signInstanceWid'] = task['signInstanceWid']
        form['isMalposition'] = task['isMalposition']
        return form

    # DES加密
    @staticmethod
    def DESEncrypt(s, key='ST83=@XV'):
        key = key
        iv = b"\x01\x02\x03\x04\x05\x06\x07\x08"
        k = des(key, CBC, iv, pad=None, padmode=PAD_PKCS5)
        encrypt_str = k.encrypt(s)
        return base64.b64encode(encrypt_str).decode()

    # 提交签到任务
    @staticmethod
    def submitForm(session, user, form, apis):
        # campus daily Extension
        extension = {
            "lon": LONGITUDE,
            "model": "OPPO R11 Plus",
            "appVersion": "8.1.14",
            "systemVersion": "4.4.4",
            "userId": user['username'],
            "systemName": "android",
            "lat": LATITUDE,
            "deviceId": str(uuid.uuid1())
        }

        headers = {
            # 'tenantId': '1019318364515869',
            'User-Agent': 'Mozilla/5.0 (Linux; Android 4.4.4; OPPO R11 Plus Build/KTU84P) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/33.0.0.0 Safari/537.36 okhttp/3.12.4',
            'CpdailyStandAlone': '0',
            'extension': '1',
            'Cpdaily-Extension': ActionBase.DESEncrypt(json.dumps(extension)),
            'Content-Type': 'application/json; charset=utf-8',
            'Accept-Encoding': 'gzip',
            # 'Host': 'swu.cpdaily.com',
            'Connection': 'Keep-Alive'
        }
        res = session.post(
            url='https://{host}/wec-counselor-sign-apps/stu/sign/completeSignIn'.format(host=apis['host']),
            headers=headers, data=json.dumps(form), verify=not DEBUG)
        message = res.json()['message']
        if message == 'SUCCESS':
            ActionBase.log('自动签到成功')
            send_email('自动签到成功', user['email'])
        else:
            ActionBase.log('自动签到失败，原因是：' + message)
            send_email('自动签到失败，原因是:' + message, user['email'])
            return False

    @staticmethod
    def send_email(msg, to):
        send_email(msg, to)

    @staticmethod
    # 打印调试信息
    def log(content):
        if not ActionBase.silence:
            print('>>> {} {}'.format(str(datetime.now(TIME_ZONE_CN)).split('.')[0], content))
