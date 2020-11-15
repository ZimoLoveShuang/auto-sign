import math
import os
import random

import gevent
from gevent.queue import Queue
from Crypto.Cipher import AES

from config import TITLE, ROOT_PATH_CACHE

from spider_cluster.action_base import *
from spider_cluster.gain import ProxyGenerator
from middleware.data_IO import refresh_database
from config import SECRET_NAME

USE_PROXY = False
proxy_ip = dict()
user_id = dict()
user_q = Queue()


def loads_proxy():
    global proxy_ip
    proxy_ip = ProxyGenerator().run()
    return True


class HainanUniversity(ActionBase):
    """海南大学驱动"""

    def __init__(self):
        super(HainanUniversity, self).__init__()
        self.school_token = '海南大学'

        self.apis = {
            'login-url': 'https://authserver.hainanu.edu.cn/authserver/login?service=https%3A%2F%2Fhainanu.campusphere.net%2Fportal%2Flogin',
            'host': 'hainanu.campusphere.net'
        }

    @staticmethod
    def AESEncrypt(data, secret_key):
        def getRandomString(length):
            chs = 'ABCDEFGHJKMNPQRSTWXYZabcdefhijkmnprstwxyz2345678'
            result = ''
            for i in range(0, length):
                result += chs[(math.floor(random.random() * len(chs)))]
            return result

        def EncryptAES(s, middleware_key, iv='1' * 16, charset='utf-8'):
            middleware_key = middleware_key.encode(charset)
            iv = iv.encode(charset)
            BLOCK_SIZE = 16
            _pad_ = lambda i: (i + (BLOCK_SIZE - len(i) % BLOCK_SIZE) * chr(BLOCK_SIZE - len(i) % BLOCK_SIZE))
            raw = _pad_(s)
            cipher = AES.new(middleware_key, AES.MODE_CBC, iv)
            encrypted = cipher.encrypt(bytes(raw, encoding=charset))
            return str(base64.b64encode(encrypted), charset)

        return EncryptAES(getRandomString(64) + data, secret_key, secret_key)

    def get_session(self, user, apis=None, retry=0, use_proxy=False, delay=0.5, max_retry_num=100):
        global proxy_ip
        import re

        if retry >= max_retry_num:
            self.error_msg = self.log('get_session 接口异常，请手动打卡')
            print(f'接口异常_请手动打卡,{user["username"]}')
            self.send_email('接口异常，请手动打卡', to=user['email'])
            return None

        if not apis:
            apis = self.apis
        """=============================替换====================================="""
        # PartI. -- loads login cookie
        try:
            response = requests.get(apis['login-url'], timeout=1)
        except ConnectionError or Timeout:
            retry += 1
            return self.get_session(user, apis, retry)

        cookie = requests.utils.dict_from_cookiejar(response.cookies)
        JSESSIONID = cookie['JSESSIONID']
        route = cookie['route']

        cookie = 'route=' + route + '; JSESSIONID=' + JSESSIONID + '; org.springframework.web.servlet.i18n.CookieLocaleResolver.LOCALE=zh_CN'
        headers = {'Cookie': cookie}

        # PartII. -- loads session cookie
        try:
            if not use_proxy:
                response = requests.post(url=apis['login-url'], headers=headers, timeout=1)
            else:
                response = requests.post(url=apis['login-url'], headers=headers, timeout=1,
                                         proxies=proxy_ip)
        # IP may be frozen
        except ConnectionError or Timeout:
            retry += 1
            return self.get_session(user, apis, retry, use_proxy=True)

        try:
            params = {
                'username': user['username'],
                'password': self.AESEncrypt(user['password'],
                                            re.findall('id="pwdDefaultEncryptSalt" value="(.*?)"', response.text)[0]),
                'lt': re.findall('name="lt" value="(.*)"', response.text)[0],
                'dllt': re.findall('name="dllt" value="(.*)"', response.text)[0],
                'execution': re.findall('name="execution" value="(.*?)"', response.text)[0],
                '_eventId': 'submit',
                'rmShown': re.findall('name="rmShown" value="(.*?)"', response.text)[0],
            }
        # IP was frozen
        except IndexError:
            retry += 1
            # if retry % 5 == 0:
            #     self.log('IP被封禁，即将更换代理')
            #     loads_proxy()
            #     return self.get_session(user, apis, retry, use_proxy=True)
            self.log('IP被封禁，即将载入代理')
            return self.get_session(user, apis, retry, use_proxy=False)

        cookies = dict()
        res = requests.post(url=apis['login-url'], headers=headers, data=params, allow_redirects=False)
        if res.status_code <= 400:
            secret_key = requests.utils.dict_from_cookiejar(
                requests.get(url=f'https://{apis["host"]}/portal/login',
                             params={'ticket': re.findall('(?<==).*', res.headers.get('Location'))[0]},
                             allow_redirects=False).cookies
            )
            try:
                # if '用户名或者密码错误' in res.json()['msg']:
                #     self.error_msg = self.log('{} 请检查账号信息是否改动'.format(res.json()['msg']))
                #     return None
                # elif '空' in res.json()['msg']:
                #     self.error_msg = self.log(''.format(res.json()['msg']))
                #     return None
                #
                # self.log('{} -- {}'.format(res.json()['msg'], user['username']))
                cookie_str = res.headers.get('SET-COOKIE')

                # json提取正常但cookieStr为空，视为HTTP异常，使用递归方案重新发起请求
                if not cookie_str:
                    retry += 1
                    gevent.sleep(delay)
                    return self.get_session(user, apis, retry=retry, max_retry_num=max_retry_num, delay=delay)

                # 解析cookie
                for line in cookie_str.split(';'):
                    try:
                        name, value_ = line.replace(',', '').strip().split('=', 1)
                        if name == 'CASTGC' or name == 'CASPRIVACY':
                            cookies[name] = value_
                        elif 'iPlanetDirectoryPro' in name:
                            cookies['iPlanetDirectoryPro'] = value_.split('=')[-1]
                    except ValueError:
                        pass
                cookies.update({'route': route, 'JSESSIONID': JSESSIONID, })
                cookies.update(secret_key)

                # self.log("cookies:{}".format(cookies))
                """=============================替换====================================="""
                session = requests.session()
                session.cookies = requests.utils.cookiejar_from_dict(cookies, cookiejar=None, overwrite=True)
                return session

            # json提取异常，接口返回数据为空，重试(max_retry_num - 3)次
            except json.decoder.JSONDecodeError:
                return self.get_session(user, apis, retry=max_retry_num - 3, delay=delay, max_retry_num=max_retry_num)

    def fill_form(self, task: dict, session, user, apis=None, ):
        if not apis:
            apis = self.apis
        form = {
            'longitude': LONGITUDE,
            'latitude': LATITUDE,
            'position': ADDRESS,
            'abnormalReason': ABNORMAL_REASON,
            'signPhotoUrl': ''
        }

        extraFields = task.get('extraField')
        if extraFields and extraFields.__len__() == 1:
            question = extraFields[0].get('title')
            answer = QnA[question]
            extraFieldItems = extraFields[0]['extraFieldItems']
            for extraFieldItem in extraFieldItems:
                if extraFieldItem['content'] == answer:
                    form['extraFieldItems'] = [{'extraFieldItemValue': answer,
                                                'extraFieldItemWid': extraFieldItem['wid']}]
        form['signInstanceWid'] = task['signInstanceWid']
        form['isMalposition'] = task['isMalposition']
        return form

    @staticmethod
    def private_extract(response: dict, user=None, save_method='json'):
        """
        Obfuscated instructions
        :param response:
        :param user:
        :param save_method:
        :return:
        """
        clear_response = {}

        for key_, value_ in response.get('signedStuInfo').items():
            if key_ in ['schoolStatus', 'malposition'] or value_ == '':
                continue
            clear_response.update({key_: value_})

        for key_, value_ in clear_response.items():
            if key_ == 'userId':
                user_id[value_].update(clear_response)
                user_id[value_].update({'request_time': str(datetime.now(TIME_ZONE_CN)).split('.')[0]})
                user_q.put_nowait(user_id[value_])

        if not user_q.empty():
            stu_info: dict = user_q.get_nowait()
            output = os.path.join(ROOT_PATH_CACHE, '{}.json'.format(stu_info['userId']))
            with open(output, 'w', encoding='utf8') as f:
                f.write(json.dumps(stu_info, indent=4, ensure_ascii=False))

    def run(self, user=None):
        global user_id
        user_id.update({user.get('username'): user})

        # loads user unified data
        self.user_info = user

        # (√) apis -- get the login url of AASoHainanU(Academic Affairs System of Hainan University)
        # apis = self.get_campus_daily_apis(user)

        # (√ A++Decoupling) session -- Simulated login the AASoHainanU
        session = self.get_session(user)

        # session success -- get the cookie and hold the session
        if session:
            params = self.get_unsigned_tasks(session)
            # (√) params success -- get the secret_key-des file of sign-in information
            if params:

                # (√) task -- sign in tasks(but only one)
                task = self.get_detail_task(session, params)

                # (*)stu_info -- extract private information of students

                # (√) form -- requests post data
                form = self.fill_form(task, session, user)

                # (√) message -- API response json data
                message = self.submitForm(session, user, form)

                # message success -- (model output):task over!send notification SMS
                # TODO：Function Add: WeChat Push by <server Kishida>
                if message == 'SUCCESS':
                    self.send_email(f'[{str(datetime.now(TIME_ZONE_CN)).split(".")[0]}]自动签到成功<From.{SECRET_NAME}>',
                                    user['email'])

                # message error -- (ignore warning):The sign-in task of the next stage has not started
                # message error -- (stale panic):An unknown error occurred
                else:
                    if '任务未开始' not in message:
                        self.log('{}||{}'.format(message, user['username']))
                        # self.send_email('自动签到失败，原因是:' + message, user['email'])

            # params error -- from the web interface of server.hainanu.net
            # params error -- The task for this student in the next time period is empty
            else:
                # print('The task for this student in the next time period is empty :{} '.format(user['username']))
                # self.send_email(self.error_msg, MANAGER_EMAIL)
                self.log('Params is None||可能错误原因：该时间段无签到任务||{}'.format(user['username']))

        # session error -- Account error: user or password is None;user or password is mismatch
        # session error -- HTTP error: connection time out; too many retries
        else:
            self.log('Session is None||可能的错误原因：账号或密码错误||{}'.format(user['username']))


if __name__ == '__main__':
    tasks = refresh_database()
    for key, value in tasks.items():
    	HainanUniversity().run(value)	
