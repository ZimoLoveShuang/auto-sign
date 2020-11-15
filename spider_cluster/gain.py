import requests
from requests.exceptions import *

ip_list = []
use_proxy = False


class ProxyGenerator(object):

    @staticmethod
    def get_proxy_ip() -> str:
        return requests.get('http://yao.qinse.top:5555/random').text

    def generate_proxies(self, test_task: dict, retry=0):
        if retry >= 3:
            print('重试{}次，获取失败，任务结束'.format(retry))
            return False
        try:
            proxies = {
                'http': test_task['ip'],
            }
            test_url = test_task['url']

            res = requests.get(test_url, proxies=proxies, timeout=1)
            res.raise_for_status()
            if res.status_code == 200:
                print('>>> 代理获取成功 || {}'.format(proxies))
                return proxies
        except RequestException:
            retry += 1
            print('代理超时，即将重试，重试次数{}'.format(retry))
            self.generate_proxies(test_task, retry)

    # 模块接口
    def run(self):
        task = {
            'ip': self.get_proxy_ip(),
            'url': 'https://www.baidu.com'
        }
        return self.generate_proxies(task)


def loads_proxy():
    ip_list.append(ProxyGenerator().run())
    return True


if __name__ == '__main__':
    print(loads_proxy())
