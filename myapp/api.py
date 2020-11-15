import re

from email_validator import validate_email, EmailNotValidError
from spider_cluster.action_slaver.hainanu import HainanUniversity
from middleware.data_IO import refresh_database

hnu = HainanUniversity()


# 验证今日校园账号正确
def verify_input_account(user=None, ):
    """
    Just hainan university server !!
    :param user:
    :return:
    """
    if user is None:
        user = {}
    for i in list(user.values()):
        if not i:
            return False

    # user.update({'username': cp_username, 'password': cp_password})
    hnu.user_info = user
    apis = hnu.get_campus_daily_apis(user)
    session = hnu.get_session(user, apis, max_retry_num=10, delay=1)
    if session:
        print('{} 账号验证通过'.format(user['username']))
        try:
            params = hnu.get_unsigned_tasks(session, apis)
            if params:
                task = hnu.get_detail_task(session, params, apis)
                hnu.private_extract(task, save_method=json)
        finally:
            return 'success'
    else:
        hnu.log('Session is None||可能的错误原因：账号或密码错误')
        return 'failed'
        # ActionBase.send_email('账号密码错误', user['email'])


# 验证邮箱合法
def verify_input_email(email: str) -> bool:
    """
    验证邮箱合法条件：
    1.正则合法
    2.非临时邮箱
    3.邮箱存在且通过验证
    :param email:
    :return:
    """
    # 第一层过滤：正则合法
    response = re.search("^\w+([-+.]\w+)*@\w+([-.]\w+)*\.\w+([-.]\w+)*$", email)
    if response:
        # 第二层过滤，协议合规
        try:
            valid = validate_email(email)
            return True
        except EmailNotValidError:
            return False
    else:
        return False


def temp_coroutine(target):
    while not target.empty():
        user_ = target.get_nowait()
        verify_input_account(user_)


def test_():
    from gevent import monkey

    monkey.patch_all()
    import gevent
    from gevent.queue import Queue

    test_Q = Queue()
    max_len = 0
    task_list = []
    for key, value in refresh_database().items():
        user = {
            'username': value['username'],
            'password': value['password']
        }
        test_Q.put_nowait(user)
    max_len = test_Q.qsize()

    for x in range(max_len):
        task = gevent.spawn(temp_coroutine, test_Q)
        task_list.append(task)

    gevent.joinall(task_list)
