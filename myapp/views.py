from flask import Flask, render_template, request
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, EqualTo, Length

app = Flask(__name__)
app.secret_key = 'CampusDailyAutoSign'


class Register(FlaskForm):
    username = StringField(label='username',
                           validators=[DataRequired()],
                           render_kw={
                               'placeholder': 'username',
                               'class': 'input_text'
                           })
    password = PasswordField(label='password',
                             validators=[DataRequired(),
                                         Length(3, 8, '密码长度必须在3-8之间')])
    cpassword = PasswordField(label='cpassword',
                              validators=[DataRequired(),
                                          EqualTo('password', '两次密码不一致')])
    submit = SubmitField('提交')


@app.route('/testform', methods=['get', 'post'])
def testform():
    form = Register()
    if request.method == 'GET':
        return render_template('form.html', form=form)
    if request.method == 'POST':
        # 验证表单
        if form.validate_on_submit():
            print(form.data)
            return "success"
        else:
            # 验证失败
            print(form.errors)
            error_msg = form.errors
            for k, v in error_msg.items():
                print(k, v[0])
            return "failed"


if __name__ == '__main__':
    app.run(debug=True, port=6563, host='0.0.0.0')
