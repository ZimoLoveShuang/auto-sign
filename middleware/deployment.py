def deployment(task_name, tz='cn'):
    """
    Linux 云端部署
    :param task_name: CampusDailySpeedUp(HainanUniversity).run
    :param tz:
    :return:
    """
    import time
    import schedule
    from datetime import datetime, timedelta
    from config import TIME_ZONE_CN, MANAGER_EMAIL
    from middleware.info_manager import send_email

    # 默认北京时区
    # todo:植入截图合成脚本
    morn, noon, night = "07:30", "12:00", "21:00"

    if tz == 'us':
        # 纽约时区
        morn = (datetime(2020, 11, 6, 7, 0, 0) - timedelta(hours=13)).strftime("%H:%M")
        noon = (datetime(2020, 11, 6, 12, 0, 0) - timedelta(hours=13)).strftime("%H:%M")
        night = (datetime(2020, 11, 6, 21, 0, 0) - timedelta(hours=13)).strftime("%H:%M")

    schedule.every().day.at(morn).do(task_name)
    schedule.every().day.at(noon).do(task_name)
    schedule.every().day.at(night).do(task_name)

    try:
        while True:
            schedule.run_pending()
            time.sleep(1)
    except Exception as e:
        now_ = str(datetime.now(TIME_ZONE_CN)).split('.')[0]
        send_email(f'{now_} || {e}', to=MANAGER_EMAIL)


def AliCloud_deploy():
    from config import ROOT_PATH_CONFIG_USER
    from spider_cluster.action_slaver.hainanu import HainanUniversity
    from spider_cluster.coroutine_engine import CampusDailySpeedUp

    # 接管任务
    print('>>> 协程核心已装载，任务即将执行...')
    deployment(CampusDailySpeedUp(core=HainanUniversity(), config_path=ROOT_PATH_CONFIG_USER).run)


