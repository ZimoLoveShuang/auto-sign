<div align="center">
    <h1 align="center">
      今日校园辅导猫自动签到
    </h1>
  </div>

## 这是什么 ？

受人之托，写的今日校园自动签到脚本，可能已经通用了在今日校园签到的所有学校了
* [x] 图片签到
* [x] 位置签到
* [x] 额外选项


## 设计思路

1. 模拟登陆
2. 获取每日未签到任务
3. 获取未签到任务详情
4. 根据配置，自动填写表单
5. 提交未签到任务


## Actions 方式

1. 先 Fork 本项目
2. 配置好自己的config.yml和default.png[**如不需要图片,请自行修改actions脚本**]
3. 将上面两个文件分别转为Base64,可使用[这个网站](https://www.hitoy.org/tool/file_base64.php)
4. 进入项目 **Settings -> Secrets** 后 点击**New repository secret**按钮 依次添加以下 2 个 Secrets。

| Name       | Value               |
| ---------- | ------------------  |
| CONFIG     | config.yml的Base64  |
| IMAGE      | default.png的Base64 |


5. 修改.github/trigger内的内容为on(随便创建一个文件也可以)
6. 检查能否**正常**签到




## 云函数方式
 请参考[auto-submit项目](https://github.com/ZimoLoveShuang/auto-submit)如遇到依赖问题，请去[`auto-sumit`](https://github.com/ZimoLoveShuang/auto-submit)项目下载`dependency.zip`，然后参考`auto-submit`项目的说明将函数依赖层添加到腾讯云函数, 如果一天签到多次，除了问题不一样之外，其他都一样，你又不想配置多个云函数的话，配置文件设置不检查就行了
 
 
 

## Config.yml的 配置方式
 如果你不会配置表单组默认选项配置，请下载本项目到本地输入`pip install -r requirements.txt`后配置好Config.yml内的user部分的信息之后本地执行`generate.py`然后将分割线下的内容复制到配置文件中对应位置,如果不知道怎么配置经纬度信息可以访问[这里](http://zuobiao.ay800.com/s/27/index.php)，将经纬度**四舍五入保留六位小数**之后的放入配置文件对应位置即可




# 其他
1. 禁止任何人使用此项目提供付费的代挂服务
2. 项目依赖于我的开源项目[模拟登陆 金智教务统一登陆系统 的API](https://github.com/ZimoLoveShuang/wisedu-unified-login-api)
3. `Cpdaily-Extension`本质上就是对一个json对象进行了des加密，然后编码为了Base64字符串，加密解密实现可以参考[Java版](https://github.com/ZimoLoveShuang/yibinu-score-crawler/blob/master/src/main/java/wiki/zimo/scorecrawler/helper/DESHelper.java) [python版](https://github.com/ZimoLoveShuang/auto-submit/blob/master/currency/encrypt.py)
4. 也欢迎其他学校学子在此提交适用于自己学校的配置，命名规则为`config_xxxx.yml`，`xxxx`为学校英文简称
5. 如果需要针对特定签到任务的黑名单(如出入校等)，可自行修改代码
