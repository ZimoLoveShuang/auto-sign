# auto-sign

# 禁止任何人使用此项目提供付费的代挂服务

受人之托，写的今日校园自动签到脚本，支持图片，定位，额外选项等，**可能已经通用了在今日校园签到的所有学校了**。

# 设计思路

1. 模拟登陆
2. 获取每日未签到任务
3. 获取未签到任务详情
4. 根据配置，自动填写表单
5. 提交未签到任务

# 使用

## 请参考[auto-submit项目](https://github.com/ZimoLoveShuang/auto-submit)

#### 如果你不会配置表单组默认选项配置，请先配置好user信息之后本地执行generate.py然后将分割线下的内容复制到配置文件中对应位置

#### 如遇到依赖问题，请去[`auto-sumit`](https://github.com/ZimoLoveShuang/auto-submit)项目下载`dependency.zip`，然后参考`auto-submit`项目的说明将函数依赖层添加到腾讯云函数

#### 如果不知道怎么配置经纬度信息，可以访问[这里](http://zuobiao.ay800.com/s/27/index.php)，将经纬度四舍五入保留六位小数之后的放入配置文件对应位置即可

#### 如果一天签到多次，除了问题不一样之外，其他都一样，你又不想配置多个云函数的话，配置文件设置不检查就行了

# 其他

1. 项目依赖于我的开源项目[模拟登陆 金智教务统一登陆系统 的API](https://github.com/ZimoLoveShuang/wisedu-unified-login-api)
2. `Cpdaily-Extension`本质上就是对一个json对象进行了des加密，然后编码为了Base64字符串，加密解密实现可以参考[Java版](https://github.com/ZimoLoveShuang/yibinu-score-crawler/blob/master/src/main/java/wiki/zimo/scorecrawler/helper/DESHelper.java) [python版](https://github.com/ZimoLoveShuang/auto-submit/blob/master/currency/encrypt.py)
3. 也欢迎其他学校学子在此提交适用于自己学校的配置，命名规则为`config_xxxx.yml`，`xxxx`为学校英文简称