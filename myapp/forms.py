import csv
from uuid import uuid4
from flask import Flask, request, jsonify, render_template

from myapp.api import verify_input_email, verify_input_account, hnu
from config import ROOT_PATH_CONFIG_USER
from myapp.app_config import *

app = Flask(__name__)

# {email:token}
verify_code_token = dict()


@app.route('/register', methods=['POST'])
def register():
    form: dict = request.form  # 解析请求
    school = form.get('school')  # 学校
    username = form.get('username')  # 用户名
    password = form.get('password')  # 密码
    email = form.get('email')  # 邮箱

    # check database-user
    with open(ROOT_PATH_CONFIG_USER, 'r', encoding='utf8') as f:
        data = [i for i in csv.reader(f)]
        ids = [i[1] for i in data[1:]]
        if username in ids:
            return 'failed'

    # check account register
    if school and password and email:
        with open(ROOT_PATH_CONFIG_USER, 'a', encoding='utf-8', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([school, username, password, email])

    return 'success'


@app.route(TOS_, methods=['GET'])
def item_tos():
    tos = '1.本项目仅为海南大学提供服务；\n\n' \
          '2.本项目引用ZiMo·API，由海南大学机器人与人工智能协会参与维护；\n\n' \
          '3.禁止任何人使用此项目提供任何收费服务；\n\n'
    title = 'CampusDailyAutoSign[For.HainanUniversity]_v1.0'
    response = {'tos': tos, 'title': title}
    return jsonify(response)


@app.route(VERITY_CPDAILY_ACCOUNT, methods=['POST'])
def verity_cpdaily_account(call=False):
    # 解析post参数
    form: dict = request.form
    user = {
        'username': form.get('username'),
        'password': form.get('password')
    }

    # 验证函数
    res = verify_input_account(user=user, )

    # 构造响应
    response_json = dict()
    response_json['msg'], response_json['status'] = res, 200
    return jsonify(response_json)


@app.route(VERITY_ACCOUNT_EXIST, methods=['POST'])
def verity_account_exist(call=False):
    form: dict = request.form
    username = form.get('username')
    response = {'args': username}
    try:
        if isinstance(username, str):
            with open(ROOT_PATH_CONFIG_USER, 'r', encoding='utf8') as f:
                data = [i for i in csv.reader(f)]
                ids = [i[1] for i in data[1:]]
                if username in ids:
                    response.update({'msg': 'failed', 'info': '账号已登记'})
                else:
                    response.update({'msg': 'success', 'info': '账号可登记'})
        else:
            response.update({'msg': 'failed', 'info': 'post 信息为空'})
    finally:
        return jsonify(response)


@app.route(VERITY_EMAIL_PASSABLE, methods=['POST'])
def verity_email_passable():
    form: dict = request.form
    email = form.get('email')
    response = {'args': email}
    try:
        if isinstance(email, str):
            response_ = verify_input_email(email)
            if response_:
                temp_token = str(uuid4())
                response.update({'msg': 'success', 'info': '邮箱合法', 'token': temp_token})
                verify_code_token.update({temp_token: {'email': email}})
            else:
                response.update({'msg': 'failed', 'info': '邮箱不合规', })
        else:
            response.update({'msg': 'empty', 'info': '参数不合法', })
    finally:
        return jsonify(response)


@app.route('/hello')
def hello():
    import os
    ddt = os.path.join(os.path.dirname(__file__), 'templates')
    ddt = os.path.join(os.path.dirname(__file__), 'login')
    index_path = os.path.join(os.path.dirname(__file__), 'form.html')
    print(index_path)
    return render_template('form.html')


@app.route(SEND_VERITY_CODE, methods=['POST'])
def send_verify_code():
    from middleware.info_manager import send_email
    form: dict = request.form
    token = form.get('token')
    email = form.get('email')
    response = {'args': email}

    try:
        if isinstance(token, str) and isinstance(email, str):
            target_email = verify_code_token.get(token).get('email')
            if isinstance(target_email, str) and target_email == email:
                send_email(msg=str(uuid4()).split('-')[1], to=email)
                response.update({'msg': 'success', 'info': '验证码已发送'})
            else:
                response.update({'msg': 'failed', 'info': 'token验证失败'})
        else:
            response.update({'msg': 'failed', 'info': '请求参数有误'})
    finally:
        return jsonify(response)


@app.route(QUICK_START, methods=['POST'])
def quick_start():
    import requests
    from middleware.info_manager import send_email
    form: dict = request.form  # 解析请求
    school = form.get('school')  # 学校
    username = form.get('username')  # 用户名
    password = form.get('password')  # 密码
    email = form.get('email')  # 邮箱

    user_token = form.get('token')
    sentinel = verify_code_token.get(user_token)

    token = str(uuid4())
    response = dict()
    try:
        if isinstance(user_token, str) and user_token != '':
            print('user_token:{}'.format(user_token))
            if isinstance(sentinel, dict):
                with open(ROOT_PATH_CONFIG_USER, 'a', encoding='utf-8', newline='') as f:
                    writer = csv.writer(f)
                    writer.writerow([school, username, password, email])
                    requests.post('http://123.56.77.6:443/register', data=dict(form))
                    response.update({'msg': 'success', 'info': '注册成功', 'args': sentinel})
        else:

            with open(ROOT_PATH_CONFIG_USER, 'r', encoding='utf8') as f:
                data = [i for i in csv.reader(f) if i]

            if isinstance(school, str) and isinstance(password, str) \
                    and isinstance(email, str) and isinstance(username, str):
                ids = [i[1] for i in data[1:]]
                if username not in ids:
                    user = {'username': username, 'password': password}
                    hnu.user_info = user
                    apis = hnu.get_campus_daily_apis(user)
                    session = hnu.get_session(user, apis, max_retry_num=10, delay=1)
                    if session:
                        res = verify_input_email(email)
                        if res:
                            send_email(msg=token, to=email, headers='【今日校园】VerifyToken')
                            verify_code_token.update(
                                {token: user}
                            )
                            print(verify_code_token)
                            response.update({'msg': 'success', 'info': '验证成功'})
                        else:
                            response.update({'msg': 'failed', 'info': '邮箱不合法'})
                    else:
                        response.update({'msg': 'failed', 'info': '账号或密码错误'})
                else:
                    response.update({'msg': 'failed', 'info': '账号已验证'})
            else:
                response.update({'msg': 'failed', 'info': '请求参数有误'})
    except Exception as e:
        print(e)
    finally:
        return jsonify(response)


from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, EqualTo, Length


class Register(FlaskForm):
    username = StringField(
        label='username',
        validators=[DataRequired()],
        render_kw={
            'placeholder': 'username',
            'class': 'input_text'
        }
    )
    password = PasswordField(label='password',
                             validators=[DataRequired(),
                                         Length(3, 20, '密码长度必须在3-20之间')])
    password2 = PasswordField(label='password2',
                              validators=[DataRequired(),
                                          EqualTo('password', '两次密码不一致')])
    submit = SubmitField('提交')


@app.route('/cpdaily/api/item/registe', methods=['GET', 'POST'])
def html_register():
    form = Register()
    if request.method == 'GET':
        return render_template('form.html', form=form)
    if request.method == 'POST':
        if form.validate_on_submit():
            print(type(form.data))
            print(form.data)
            return 'success'
        else:
            print(form.errors)
            error_msg = form.errors
            for key, value in error_msg.items():
                print(key, value[0])
            return 'failed'


if __name__ == '__main__':
    app.run(port=8080, host='0.0.0.0', debug=True)
