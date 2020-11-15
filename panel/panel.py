import easygui
import requests

DEBUG = 0
CDN_HOST = 'IP:Port'
INTERFACE_API = '/cpdaily/api/item/'
INTERFACE_REGISTER = f'http://{CDN_HOST}{INTERFACE_API}' + 'quick_start'
INTERFACE_TOS = f'http://{CDN_HOST}{INTERFACE_API}' + 'tos'


class InformationRegister(object):
    def __init__(self):
        # TITLE
        self.title = '信息验证向导_v1.0'
        self.home_page()

    # 首页
    def home_page(self):

        # 检控--页面跳转控制:False退出
        keep_ = False

        # 单选
        choice_list = ['[1]信息验证', '[2]项目说明', '[3]退出']
        usr_c = easygui.choicebox('欢迎使用CampusDailyAutoSign', self.title, choices=choice_list)
        try:
            if isinstance(usr_c, str):
                if usr_c == '[1]信息验证':
                    try:
                        self.register()
                        keep_ = True
                    except TypeError:
                        pass
                    finally:
                        keep_ = True
                elif usr_c == '[2]项目说明':
                    self.tos_page()
                    keep_ = True
        finally:
            if keep_:
                self.home_page()

    def register(self):
        data = {
            'username': '',  # 账号
            'password': '',  # 密码
            'email': '',  # 联系邮箱
            'school': '海南大学',
        }
        if DEBUG:
            debug_value = ['test_username', 'test_email@qq.com', 'test_password']

            user_input = easygui.multpasswordbox('请输入今日校园验证信息[仅海大学子可用]', self.title, fields=['账号', '邮箱', '密码'],
                                                 values=debug_value)
        else:
            user_input = easygui.multpasswordbox('请输入今日校园验证信息[仅海大学子可用]', self.title, fields=['账号', '邮箱', '密码'])
        data['username'] = user_input[0]
        data['email'] = user_input[1]
        data['password'] = user_input[-1]

        # print(data)
        res = requests.post(INTERFACE_REGISTER, data=data)
        # print(res.json())
        if res.json().get('msg') == 'success':

            user_input = easygui.enterbox('请输入邮箱验证令牌', self.title)

            data.update({'token': user_input.strip()})

            res_token = requests.post(INTERFACE_REGISTER, data=data)

            easygui.msgbox('登记成功', self.title)
        else:
            logo_msg = '请求异常，可能原因有：\n\n' \
                       '1.账号或密码错误；\n\n' \
                       '2.账号已在库;\n\n' \
                       '3.请求接口已更新，请联系脚本开发者。'
            easygui.msgbox('输入参数有误或接口繁忙；请稍后再试', self.title)

        return True

    # 脚本声明
    def tos_page(self, ):
        """脚本声明"""

        try:
            response = requests.get(INTERFACE_TOS, timeout=15)
            response.raise_for_status()
            response = response.json()

            title = response['title']
            tos = response['tos']

            easygui.msgbox(tos, title)

        except requests.exceptions.RequestException:
            easygui.msgbox('链接超时', '异常提醒', self.title)
        finally:
            return 'tos'


if __name__ == '__main__':
    InformationRegister()
