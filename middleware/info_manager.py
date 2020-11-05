# 邮件发送模块
def send_email(msg, to):
    """
    写死管理者账号，群发邮件
    :param msg: 正文内容
    :param to: 发送对象
    :return:
    """
    # 发送邮件通知
    from datetime import datetime
    from email.header import Header
    from email.mime.text import MIMEText
    import smtplib

    sender = 'xyh.hainanu@qq.com'
    password = 'uaybkktfcjyxeedc'
    smtp_server = 'smtp.qq.com'

    message = MIMEText(msg, 'plain', 'utf-8')
    message['From'] = Header(sender, 'utf-8')  # 发送者
    message['To'] = Header(to, 'utf-8')  # 接收者
    message['Subject'] = Header("今日校园打卡情况推送-{}".format(str(datetime.now()).split('.')[0]), 'utf-8')
    server = smtplib.SMTP_SSL(smtp_server, 465)

    if to != '':
        try:
            print('正在发送邮件通知。。。')
            server.login(sender, password)
            server.sendmail(sender, to, message.as_string())
            print('发送成功')
        except Exception as e:
            print('发送失败 || {}'.format(e))
        finally:
            server.quit()
