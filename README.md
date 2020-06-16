# auto-sign

受人之托，写的今日校园自动签到脚本，适用于西南大学，长江师范学院

# 设计思路

1. 模拟登陆
2. 获取每日未签到任务
3. 获取未签到任务详情
4. 提交未签到任务

# 使用

1. 下载或者克隆此仓库到本地
    ```shell script
    git clone https://github.com/ZimoLoveShuang/auto-sign.git
    ```
2. 修改`index_xxxx.py`中的对应配置`xxxx`对应学校英文简称，如西南大学的简称是`swu`，对应的脚本就是`index_swu.py`，以此类推
3. 浏览器访问[腾讯云函数控制台](https://console.cloud.tencent.com/scf/index?rid=1)
4. 登陆认证之后，点击左侧菜单中的函数服务，然后新建一个云函数，名称随意，运行环境选择`python3.6`，创建方式选空白函数，然后点击下一步
5. 提交方法选择本地上传文件夹，选择下载配置好的仓库文件夹，点击下面的高级设置，设置超时时间为60秒，然后点击完成
6. 进入新建好的云函数，左边点击触发管理，点击创建触发器，名称随意，触发周期选择自定义，配置好cron表达式后，点击提交，下面的cron表达式代表每天早、晚的7:10分都会执行
    ```shell script
    0 10 7,19 * * * *
    ```
7. enjoy it!!!

# 注意

模拟登陆API目前有白嫖限制，具体请看我[auto-submit项目](https://github.com/ZimoLoveShuang/auto-submit)的说明

# 其他

1. 项目依赖于[模拟登陆 金智教务统一登陆系统 的API](https://github.com/ZimoLoveShuang/wisedu-unified-login-api)
2. `Cpdaily-Extension`是逆向今日校园APK后得到的，本质上就是对一个json对象进行了des加密，然后编码为了Base64字符串，加密解密实现可以参考[DESHelper](https://github.com/ZimoLoveShuang/yibinu-score-crawler/blob/master/src/main/java/wiki/zimo/scorecrawler/helper/DESHelper.java)
3. 也欢迎其他学校学子在此提交适用于自己学校的脚本，命名规则为`index_xxxx.py`，`xxxx`为学校简称