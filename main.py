# coding=utf-8
import os
import sys
import time
import json
import base64
from datetime import datetime

try:
    from gevent import monkey

    monkey.patch_all()
    import gevent
    from gevent.queue import Queue
    import requests
    import pytz
    import yaml
    import oss2
    import uuid
    from urllib.parse import urlparse
    from pyDes import des, CBC, PAD_PKCS5
except ModuleNotFoundError:
    os.system('pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple some-package')

"""全局参数"""

# 消息验证模式
DEBUG = False
# 读取配置文件
# TODO:改用csv管理多用户组
CONFIG_OPTION = os.path.join(os.path.abspath('.'), 'config_hainanu.yml')
# 时区校准--BeijingTimeZone
TIME_ZONE_CN = pytz.timezone('Asia/Shanghai')
# 管理员账号，接收debug邮件
MANAGER_EMAIL = 'xyh.hainanu@qq.com'

# 多任务协程队列
work_Q = Queue()


# 打印调试信息
def log(content):
    print('>>> {} {}'.format(str(datetime.now(TIME_ZONE_CN)).split('.')[0], content))


# 载入用户数据
def load_user_config():
    with open(CONFIG_OPTION, 'r', encoding='utf-8') as f:
        return dict(yaml.load(f.read(), Loader=yaml.FullLoader))


config = load_user_config()

"""任务调度模块"""


# 交互仓库
class CampusDailyAutoSign(object):
    """交互仓库"""

    # 获取今日校园api
    @staticmethod
    def get_campus_daily_apis(user):
        apis = {}
        user = user['user']
        schools = requests.get(url='https://www.cpdaily.com/v6/config/guest/tenant/list').json()['data']
        flag = True
        for one in schools:
            if one['name'] == user['school']:
                if one['joinType'] == 'NONE':
                    log(user['school'] + ' 未加入今日校园')
                    exit(-1)
                flag = False
                params = {'ids': one['id']}
                res = requests.get(url='https://www.cpdaily.com/v6/config/guest/tenant/info', params=params, )
                data = res.json()['data'][0]
                joinType = data['joinType']
                idsUrl = data['idsUrl']

                target_url = data['ampUrl'] if 'campusphere' in data['ampUrl'] or 'cpdaily' in data['ampUrl'] else data[
                    'ampUrl2']
                parse = urlparse(target_url)
                host = parse.netloc
                res = requests.get(parse.scheme + '://' + host)
                parse = urlparse(res.url)
                apis[
                    'login-url'] = idsUrl + '/login?service=' + parse.scheme + r"%3A%2F%2F" + host + r'%2Fportal%2Flogin'
                apis['host'] = host

                break
        if flag:
            log(user['school'] + ' 未找到该院校信息，请检查是否是学校全称错误')
            return False
        log(apis)
        return apis

    # 登陆并获取session
    @staticmethod
    def get_session(user, apis):
        user = user['user']
        params = {
            'login_url': apis['login-url'],
            'needcaptcha_url': '',
            'captcha_url': '',
            'username': user['username'],
            'password': user['password']
        }

        cookies = dict()
        res = requests.post(url=config['login']['api'], data=params, verify=not DEBUG)
        # cookieStr可以使用手动抓包获取到的cookie，有效期暂时未知，请自己测试
        # cookieStr = str(res.json()['cookies'])
        cookieStr = str(res.json()['cookies'])
        log(cookieStr)
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
            log(f'the response of queryClass is None! ({res.status_code})|| Base on function(get_unsigned_tasks)')
            try:
                if res.status_code != 200:
                    log('the status code of response is ({})'.format(res.status_code))
                log('当前没有未签到任务')
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
    def fill_form(task, session, user, apis):
        user = user['user']
        form = {}
        if task['isPhoto'] == 1:
            fileName = CampusDailyAutoSign.uploadPicture(session, user['photo'], apis)
            form['signPhotoUrl'] = CampusDailyAutoSign.get_picture_url(session, fileName, apis)
        else:
            form['signPhotoUrl'] = ''
        if task['isNeedExtra'] == 1:
            extraFields = task['extraField']
            defaults = config['cpdaily']['defaults']
            extraFieldItemValues = []
            for i in range(0, len(extraFields)):
                default = defaults[i]['default']
                extraField = extraFields[i]
                if config['cpdaily']['check'] and default['title'] != extraField['title']:
                    log('第%d个默认配置项错误，请检查' % (i + 1))
                    exit(-1)
                extraFieldItems = extraField['extraFieldItems']
                for extraFieldItem in extraFieldItems:
                    if extraFieldItem['content'] == default['value']:
                        extraFieldItemValue = {'extraFieldItemValue': default['value'],
                                               'extraFieldItemWid': extraFieldItem['wid']}
                        # 其他，额外文本
                        if extraFieldItem['isOtherItems'] == 1:
                            extraFieldItemValue = {'extraFieldItemValue': default['other'],
                                                   'extraFieldItemWid': extraFieldItem['wid']}
                        extraFieldItemValues.append(extraFieldItemValue)
            # log(extraFieldItemValues)
            # 处理带附加选项的签到
            form['extraFieldItems'] = extraFieldItemValues
        # form['signInstanceWid'] = params['signInstanceWid']
        form['signInstanceWid'] = task['signInstanceWid']
        form['longitude'] = user['lon']
        form['latitude'] = user['lat']
        form['isMalposition'] = task['isMalposition']
        form['abnormalReason'] = user['abnormalReason']
        form['position'] = user['address']
        return form

    # 上传图片到阿里云oss
    @staticmethod
    def uploadPicture(session, image, apis):
        url = 'https://{host}/wec-counselor-sign-apps/stu/sign/getStsAccess'.format(host=apis['host'])
        res = session.post(url=url, headers={'content-type': 'application/json'}, data=json.dumps({}), verify=not DEBUG)
        data = res.json().get('datas')
        fileName = data.get('fileName')
        accessKeyId = data.get('accessKeyId')
        accessSecret = data.get('accessKeySecret')
        securityToken = data.get('securityToken')
        endPoint = data.get('endPoint')
        bucket = data.get('bucket')
        bucket = oss2.Bucket(oss2.Auth(access_key_id=accessKeyId, access_key_secret=accessSecret), endPoint, bucket)
        with open(image, "rb") as f:
            data = f.read()
        bucket.put_object(key=fileName, headers={'x-oss-security-token': securityToken}, data=data)
        res = bucket.sign_url('PUT', fileName, 60)
        # log(res)
        return fileName

    # 获取图片上传位置
    @staticmethod
    def get_picture_url(session, fileName, apis):
        url = 'https://{host}/wec-counselor-sign-apps/stu/sign/previewAttachment'.format(host=apis['host'])
        data = {
            'ossKey': fileName
        }
        res = session.post(url=url, headers={'content-type': 'application/json'}, data=json.dumps(data),
                           verify=not DEBUG)
        photoUrl = res.json().get('datas')
        return photoUrl

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
        user = user['user']
        # campus daily Extension
        extension = {
            "lon": user['lon'],
            "model": "OPPO R11 Plus",
            "appVersion": "8.1.14",
            "systemVersion": "4.4.4",
            "userId": user['username'],
            "systemName": "android",
            "lat": user['lat'],
            "deviceId": str(uuid.uuid1())
        }

        headers = {
            # 'tenantId': '1019318364515869',
            'User-Agent': 'Mozilla/5.0 (Linux; Android 4.4.4; OPPO R11 Plus Build/KTU84P) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/33.0.0.0 Safari/537.36 okhttp/3.12.4',
            'CpdailyStandAlone': '0',
            'extension': '1',
            'Cpdaily-Extension': CampusDailyAutoSign.DESEncrypt(json.dumps(extension)),
            'Content-Type': 'application/json; charset=utf-8',
            'Accept-Encoding': 'gzip',
            # 'Host': 'swu.cpdaily.com',
            'Connection': 'Keep-Alive'
        }
        res = session.post(url='https://{host}/wec-counselor-sign-apps/stu/sign/completeSignIn'.format(host=apis['host']),
                           headers=headers, data=json.dumps(form), verify=not DEBUG)
        message = res.json()['message']
        if message == 'SUCCESS':
            log('自动签到成功')
            email_manager('自动签到成功', user['email'])
        else:
            log('自动签到失败，原因是：' + message)
            email_manager('自动签到失败，原因是:' + message, user['email'])
            return False


cds = CampusDailyAutoSign()


# 协程插件
class CoroutineEngine(object):
    """使用协程调度多用户组"""

    def __init__(self):
        # todo:改用csv管理多用户组
        for user in config['users']:
            work_Q.put_nowait(user)

    @staticmethod
    def multi_launch():
        def task_pending():
            while not work_Q.empty():
                try:
                    user = work_Q.get_nowait()
                    apis = cds.get_campus_daily_apis(user)
                    session = cds.get_session(user, apis)
                    params = cds.get_unsigned_tasks(session, apis)
                    task = cds.get_detail_task(session, params, apis)
                    form = cds.fill_form(task, session, user, apis)
                    # form = getDetailTask(session, user, params, apis)
                    cds.submitForm(session, user, form, apis)
                except Exception as e:
                    log(e)
            else:
                return True

        result = task_pending()

    @staticmethod
    def single_launch():
        for user in config['users']:
            user = work_Q.get_nowait()
            apis = cds.get_campus_daily_apis(user)
            session = cds.get_session(user, apis)
            if session:
                params = cds.get_unsigned_tasks(session, apis)
                if params:
                    task = cds.get_detail_task(session, params, apis)
                    form = cds.fill_form(task, session, user, apis)
                    # form = getDetailTask(session, user, params, apis)
                    cds.submitForm(session, user, form, apis)

    def run(self, speed_up=True):
        """
        协程任务接口
        :param speed_up:
        :return:
        """
        if speed_up:
            task_name = self.multi_launch
            # 写死极限协程功率
            power: int = len(config['users']) if len(config['users']) <= 4 else 4
        else:
            task_name = self.single_launch
            power = 1

        task_list = []

        for x in range(power):
            task = gevent.spawn(task_name)
            task_list.append(task)
        gevent.joinall(task_list)


# ---------------------------
# 邮件发送模块
# ---------------------------
def email_manager(msg, to):
    """
    写死管理者账号，群发邮件
    :param msg: 正文内容
    :param to: 发送对象
    :return:
    """
    # 发送邮件通知
    from email.header import Header
    from email.mime.text import MIMEText
    import smtplib

    sender = 'xyh.hainanu@qq.com'
    password = ''
    smtp_server = 'smtp.qq.com'

    message = MIMEText(msg, 'plain', 'utf-8')
    message['From'] = Header(sender, 'utf-8')  # 发送者
    message['To'] = Header(to, 'utf-8')  # 接收者
    message['Subject'] = Header("今日校园打卡情况推送-{}".format(str(datetime.now()).split('.')[0]), 'utf-8')
    server = smtplib.SMTP_SSL(smtp_server, 465)

    if to != '':
        try:
            log('正在发送邮件通知。。。')
            server.login(sender, password)
            server.sendmail(sender, to, message.as_string())
            print('发送成功')
        except Exception as e:
            print('发送失败 || {}'.format(e))
        finally:
            server.quit()


# ---------------------------
# 部署接口
# ---------------------------

def deployment():
    import schedule

    schedule.every().day.at("07:30").do(CoroutineEngine().run)
    schedule.every().day.at("12:00").do(CoroutineEngine().run)
    schedule.every().day.at("21:00").do(CoroutineEngine().run)

    try:
        while True:
            schedule.run_pending()
            time.sleep(1)
    except Exception as e:
        now_ = str(datetime.now(TIME_ZONE_CN)).split('.')[0]
        email_manager(f'{now_} || {e}', to=MANAGER_EMAIL)


def system_interface(deployPlan: bool = None, coroutine_speed_up: bool = None):
    """

    :param deployPlan: 提供本地调试及云端部署两套方案
    :param coroutine_speed_up: 协程加速||云端默认启动
    :return:
    """
    if deployPlan is None:
        deployPlan = True if 'linux' in sys.platform else False
    elif coroutine_speed_up is None:
        coroutine_speed_up = True if 'linux' in sys.platform else False

    if deployPlan:
        deployment()
    else:
        CoroutineEngine().run(speed_up=coroutine_speed_up)


if __name__ == '__main__':
    system_interface()
