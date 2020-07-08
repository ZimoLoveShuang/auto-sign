import sys
import requests
import json
import uuid
import base64
from pyDes import des, CBC, PAD_PKCS5
from datetime import datetime, timedelta, timezone
from urllib.parse import urlparse
import oss2

################### 配置 #####################
# 学校
school = '安阳工学院'
# 学号
username = 'text'
# 密码
password = 'text'
# 邮箱，用于接收签到成功之后的消息
email = '461009747@qq.com'
# 位置
position = '河南省驻马店市平舆县泰和路'
# 经度
lon = '114.639377'
# 纬度
lat = '32.958833'
# 原因
abnormalReason = ' 1.体温：36.5；2.健康状况：良好 3.在家'
# 图片
photo = 'default.png'
########################################

# Cpdaily-Extension
extension = {
    "lon": lon,
    "model": "OPPO R11 Plus",
    "appVersion": "8.1.14",
    "systemVersion": "4.4.4",
    "userId": username,
    "systemName": "android",
    "lat": lat,
    "deviceId": str(uuid.uuid1())
}

session = requests.session()


# 获取当前utc时间，并格式化为北京时间
def getTimeStr():
    utc_dt = datetime.utcnow().replace(tzinfo=timezone.utc)
    bj_dt = utc_dt.astimezone(timezone(timedelta(hours=8)))
    return bj_dt.strftime("%Y-%m-%d %H:%M:%S")


# 输出调试信息，并及时刷新缓冲区
def log(content):
    print(getTimeStr() + ' ' + str(content))
    sys.stdout.flush()


# 获取今日校园api
def getCpdailyApis():
    apis = {}
    schools = requests.get(url='https://www.cpdaily.com/v6/config/guest/tenant/list').json()['data']
    flag = True
    for one in schools:
        if one['name'] == school:
            if one['joinType'] == 'NONE':
                log(school + ' 未加入今日校园或者学校全称错误')
                exit(-1)
            flag = False
            params = {
                'ids': one['id']
            }
            res = requests.get(url='https://www.cpdaily.com/v6/config/guest/tenant/info', params=params)
            data = res.json()['data'][0]
            idsUrl = data['idsUrl']
            ampUrl = data['ampUrl']
            ampUrl2 = data['ampUrl2']
            joinType = data['joinType']
            if joinType == 'CLOUD':
                parse = urlparse(ampUrl)
                host = parse.netloc
                apis[
                    'login-url'] = idsUrl + '/login?service=' + parse.scheme + r"%3A%2F%2F" + host + r'%2Fportal%2Flogin'
                apis['host'] = host
            elif joinType == 'NOTCLOUD':
                parse = urlparse(ampUrl2)
                host = parse.netloc
                apis[
                    'login-url'] = idsUrl + '/login?service=' + parse.scheme + r"%3A%2F%2F" + host + r'%2Fportal%2Flogin'
                apis['host'] = host
            break
    if flag:
        log(school + ' 未加入今日校园或者学校全称错误')
        exit(-1)
    log(apis)
    return apis


apis = getCpdailyApis()


# 登陆并获取cookies
def getCookies():
    params = {
        # 'login_url': 'http://authserverxg.swu.edu.cn/authserver/login?service=https://swu.cpdaily.com/wec-counselor-sign-apps/stu/sign/getStuSignInfosInOneDay',
        'login_url': apis['login-url'],
        'needcaptcha_url': '',
        'captcha_url': '',
        'username': username,
        'password': password
    }

    cookies = {}
    # 借助上一个项目开放出来的登陆API，模拟登陆
    res = requests.post('http://www.zimo.wiki:8080/wisedu-unified-login-api-v1.0/api/login', params)
    # cookieStr可以使用手动抓包获取到的cookie，有效期暂时未知，请自己测试
    cookieStr = str(res.json()['cookies'])
    if cookieStr == 'None':
        log(res.json())
        exit(-1)
    # log(cookieStr)

    # 解析cookie
    for line in cookieStr.split(';'):
        name, value = line.strip().split('=', 1)
        cookies[name] = value
    session.cookies = requests.utils.cookiejar_from_dict(cookies, cookiejar=None, overwrite=True)


# 获取最新未签到任务
def getUnSignedTasks():
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
        url='https://{host}/wec-counselor-sign-apps/stu/sign/getStuSignInfosInOneDay'.format(host=apis['host']),
        headers=headers, data=json.dumps({}))
    # 第二次请求每日签到任务接口，拿到具体的签到任务
    res = session.post(
        url='https://{host}/wec-counselor-sign-apps/stu/sign/getStuSignInfosInOneDay'.format(host=apis['host']),
        headers=headers, data=json.dumps({}))
    if len(res.json()['datas']['unSignedTasks']) < 1:
        log('当前没有未签到任务')
        exit(-1)
    latestTask = res.json()['datas']['unSignedTasks'][0]
    return {
        'signInstanceWid': latestTask['signInstanceWid'],
        'signWid': latestTask['signWid']
    }


# 获取签到任务详情，并构造表单
def getDetailTask(params):
    headers = {
        'Accept': 'application/json, text/plain, */*',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36',
        'content-type': 'application/json',
        'Accept-Encoding': 'gzip,deflate',
        'Accept-Language': 'zh-CN,en-US;q=0.8',
        'Content-Type': 'application/json;charset=UTF-8'
    }
    res = session.post(
        url='https://{host}/wec-counselor-sign-apps/stu/sign/detailSignInstance'.format(host=apis['host']),
        headers=headers, data=json.dumps(params))
    submitForm = {
        "signInstanceWid": params['signInstanceWid'],
        "longitude": lon,
        "latitude": lat,
        "isMalposition": 1,
        "abnormalReason": abnormalReason,
        "signPhotoUrl": getPictureUrl(uploadPicture(photo)),
        "position": position,
        "isNeedExtra": 0
    }
    return submitForm


# 上传图片到阿里云oss
def uploadPicture(image):
    url = 'https://{host}/wec-counselor-sign-apps/stu/sign/getStsAccess'.format(host=apis['host'])
    res = session.post(url=url, headers={'content-type': 'application/json'}, data=json.dumps({}))
    datas = res.json().get('datas')
    fileName = datas.get('fileName')
    accessKeyId = datas.get('accessKeyId')
    accessSecret = datas.get('accessKeySecret')
    securityToken = datas.get('securityToken')
    endPoint = datas.get('endPoint')
    bucket = datas.get('bucket')
    bucket = oss2.Bucket(oss2.Auth(access_key_id=accessKeyId, access_key_secret=accessSecret), endPoint, bucket)
    with open(image, "rb") as f:
        data = f.read()
    bucket.put_object(key=fileName, headers={'x-oss-security-token': securityToken}, data=data)
    res = bucket.sign_url('PUT', fileName, 60)
    # log(res)
    return fileName


# 获取图片上传位置
def getPictureUrl(fileName):
    url = 'https://{host}/wec-counselor-sign-apps/stu/sign/previewAttachment'.format(host=apis['host'])
    data = {
        'ossKey': fileName
    }
    res = session.post(url=url, headers={'content-type': 'application/json'}, data=json.dumps(data), verify=False)
    photoUrl = res.json().get('datas')
    return photoUrl


# DES加密
def DESEncrypt(s, key='ST83=@XV'):
    key = key
    iv = b"\x01\x02\x03\x04\x05\x06\x07\x08"
    k = des(key, CBC, iv, pad=None, padmode=PAD_PKCS5)
    encrypt_str = k.encrypt(s)
    return base64.b64encode(encrypt_str).decode()


# 提交签到任务
def submit(form):
    headers = {
        # 'tenantId': '1019318364515869',
        'User-Agent': 'Mozilla/5.0 (Linux; Android 4.4.4; OPPO R11 Plus Build/KTU84P) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/33.0.0.0 Safari/537.36 okhttp/3.12.4',
        'CpdailyStandAlone': '0',
        'extension': '1',
        'Cpdaily-Extension': DESEncrypt(json.dumps(extension)),
        'Content-Type': 'application/json; charset=utf-8',
        'Accept-Encoding': 'gzip',
        # 'Host': 'swu.cpdaily.com',
        'Connection': 'Keep-Alive'
    }
    res = session.post(url='https://{host}/wec-counselor-sign-apps/stu/sign/submitSign'.format(host=apis['host']),
                       headers=headers, data=json.dumps(form))
    message = res.json()['message']
    if message == 'SUCCESS':
        sendMessage('自动签到成功')
    else:
        sendMessage('自动签到失败，原因是：' + message)


# 发送邮件通知
def sendMessage(msg):
    send = email
    if send != '':
        log('正在发送邮件通知。。。')
        res = requests.post(url='http://www.zimo.wiki:8080/mail-sender/sendMail',
                            data={'title': '今日校园自动签到结果通知', 'content': msg, 'to': send})
        code = res.json()['code']
        if code == 0:
            log('发送邮件通知成功。。。')
        else:
            log('发送邮件通知失败。。。')
            log(res.json())


# 主函数
def main():
    getCookies()
    params = getUnSignedTasks()
    form = getDetailTask(params)
    submit(form)


# 提供给腾讯云函数调用的启动函数
def main_handler(event, context):
    try:
        main()
        return 'success'
    except:
        return 'fail'


if __name__ == '__main__':
    # print(extension)
    main()
