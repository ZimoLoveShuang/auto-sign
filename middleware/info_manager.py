# 邮件发送模块
def send_email(msg, to, headers='<今日校园>打卡情况推送'):
    """
    写死管理者账号，群发邮件
    :param msg: 正文内容
    :param to: 发送对象
    :param headers:
    :return:
    """
    # 发送邮件通知
    import smtplib
    from email.header import Header
    from email.mime.text import MIMEText

    sender = '' #发送邮件的邮箱
    password = '' #该邮箱的授权码 Help >> https://service.mail.qq.com/cgi-bin/help?subtype=1&&no=1001256&&id=28
    smtp_server = 'smtp.qq.com'

    if to != '':
        message = MIMEText(msg, 'plain', 'utf-8')
        message['From'] = Header(sender, 'utf-8')  # 发送者
        message['To'] = Header(to, 'utf-8')  # 接收者
        message['Subject'] = Header("{}".format(headers), 'utf-8')
        server = smtplib.SMTP_SSL(smtp_server, 465)
        try:
            server.login(sender, password)
            server.sendmail(sender, to, message.as_string())
            print('>>> 发送成功')
            return True
        except smtplib.SMTPRecipientsRefused:
            print('>>> 邮箱填写错误或不存在')
            return False
        except Exception as e:
            print('>>> 发送失败 || {}'.format(e))
            return False
        finally:
            server.quit()
