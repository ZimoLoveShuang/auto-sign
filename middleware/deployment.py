from config import TIME_ZONE_CN, MANAGER_EMAIL
from middleware.info_manager import send_email


def deployment(task_name):
    """
    Linux 云端部署
    :param task_name: CampusDailySpeedUp(HainanUniversity).run
    :return:
    """
    import time
    import schedule
    from datetime import datetime

    schedule.every().day.at("07:30").do(task_name)
    schedule.every().day.at("12:00").do(task_name)
    schedule.every().day.at("21:00").do(task_name)

    try:
        while True:
            schedule.run_pending()
            time.sleep(1)
    except Exception as e:
        now_ = str(datetime.now(TIME_ZONE_CN)).split('.')[0]
        send_email(f'{now_} || {e}', to=MANAGER_EMAIL)
