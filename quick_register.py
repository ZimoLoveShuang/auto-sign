data = {
    'username': '',  # 账号
    'password': '',  # 密码
    'email': 'example@qq.com',  # 联系邮箱
    'school': '海南大学',
}


def register():
    try:
        import requests

        url = 'http://t.qinse.top:8080' + '/cpdaily/api/item/quick_start'
        res = requests.post(url, data=data)
        print(res.json())

        if res.json().get('msg') == 'success':
            data.update({'token': input('>>> 请输入邮箱验证令牌:').strip()})

            res_token = requests.post(url, data=data)

            print(res_token.json())
        else:
            print('验证失败')
    except ModuleNotFoundError:
        import os
        os.system('pip install requests')

        register()


if __name__ == '__main__':
    register()
