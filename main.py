from gevent import monkey

monkey.patch_all()
from middleware.sys_interface import sys_interface

# 今日校园疫情体温检测－－自动上报脚本
if __name__ == '__main__':
    sys_interface(coroutine_speed_up=True)
