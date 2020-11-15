from gevent import monkey

monkey.patch_all()
from spider_cluster.coroutine_engine import CampusDailySpeedUp
from spider_cluster.action_slaver.hainanu import HainanUniversity
from middleware.deployment import deployment
from config import ROOT_PATH_CONFIG_USER


# 程序接口
def sys_interface(deployPlan: bool = None, coroutine_speed_up: bool = None, core=None, speed_up_way=None):
    """

    :param speed_up_way: 加速方案:from spider_cluster.coroutine_engine
    :param core: 驱动核心:from spider_cluster.action_slaver
    :param deployPlan: 提供本地调试及云端部署两套方案
    :param coroutine_speed_up: 协程加速||云端默认启动
    :return:
    """
    import sys

    # 读取配置文件路径
    config_path = ROOT_PATH_CONFIG_USER

    # 默认linux下自动挂起
    if deployPlan is None:
        deployPlan = True if 'linux' in sys.platform else False
    # 默认linux下启动协程
    elif coroutine_speed_up is None:
        coroutine_speed_up = True if 'linux' in sys.platform else False

    # 核心装载，任务识别
    if core is None:
        core = HainanUniversity()
    if speed_up_way is None:
        speed_up_way = CampusDailySpeedUp
    print('>>> 协程核心已装载，任务即将执行...')

    # 接管任务：调度器部署定时任务
    if deployPlan:
        print('>>> 任务已部署...')
        deployment(speed_up_way(core=core, config_path=config_path).run)
    # 调用协程控制器
    else:
        speed_up_way(core=core, config_path=config_path).run(speed_up=coroutine_speed_up)
        print('>>> 任务结束...')
