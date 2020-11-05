from spider_cluster.action_base import ActionBase
from middleware.data_IO import refresh_database


class HainanUniversity(ActionBase):
    """海南大学驱动"""

    def __init__(self):
        super(HainanUniversity, self).__init__()

    def run(self, user=None):
        apis = self.get_campus_daily_apis(user)
        session = self.get_session(user, apis)
        if session:
            params = self.get_unsigned_tasks(session, apis)
            task = self.get_detail_task(session, params, apis)
            form = self.fill_form(task, session, user, apis)
            self.submitForm(session, user, form, apis)
        else:
            self.log('账号密码错误,登录失败')
            # self.send_email('账号密码错误', user['email'])


if __name__ == '__main__':
    tasks = refresh_database()
    for key, value in tasks.items():
        print(key, value)
        HainanUniversity().run(value)
