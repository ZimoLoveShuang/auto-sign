# auto-sign

# 禁止任何人使用此项目提供付费的代挂服务

受人之托，写的今日校园自动签到脚本，支持图片，定位，额外选项等，**可能已经通用了在今日校园签到的所有学校了**，目前测试通过的学校如下表：

<table>
    <tr>
        <th>学校名称</th>
        <th>学校英文简称</th>
        <th>加入今日校园的方式</th>
        <th>签到说明</th>
    </tr>
    <tr>
        <td>西南大学</td>
        <td>swu</td>
        <td>NOTCLOUD</td>
        <td>定位+额外选项</td>
    </tr>
    <tr>
        <td>长江师范学院</td>
        <td>yznu</td>
        <td>NOTCLOUD</td>
        <td>定位+额外选项</td>
    </tr>
    <tr>
        <td>安阳工学院</td>
        <td>ayit</td>
        <td>CLOUD</td>
        <td>定位+照片</td>
    </tr>
    <tr>
        <td>新乡医学院</td>
        <td>xxmu</td>
        <td>CLOUD</td>
        <td>定位+照片</td>
    </tr>
    <tr>
        <td>福州大学</td>
        <td>fzu</td>
        <td>NOTCLOUD</td>
        <td>定位+两个额外选项</td>
    </tr>
</table>

# 设计思路

1. 模拟登陆
2. 获取每日未签到任务
3. 获取未签到任务详情
4. 根据配置，自动填写表单
5. 提交未签到任务

# 使用

## 参考[auto-submit项目](https://github.com/ZimoLoveShuang/auto-submit)

1. 下载或者克隆此仓库到本地
    ```shell script
    git clone https://github.com/ZimoLoveShuang/auto-sign.git
    ```
2. 修改`config_xxxx.yml`中的对应配置，`xxxx`对应学校英文简称，如西南大学的简称是`swu`，对应的配置就是`config_swu.yml`，以此类推，修改`index.py`30行读取的配置文件参数
    ```python
    # 全局配置
    config = getYmlConfig(yaml_file='config.yml')
    ```
3. 浏览器访问[腾讯云函数控制台](https://console.cloud.tencent.com/scf/index?rid=1)
4. 登陆认证之后，点击左侧菜单中的函数服务，然后新建一个云函数，名称随意，运行环境选择`python3.6`，创建方式选空白函数，然后点击下一步
5. 提交方法选择本地上传文件夹，选择下载配置好的仓库文件夹，点击下面的高级设置，设置超时时间为60秒，然后点击完成
6. 进入新建好的云函数，左边点击触发管理，点击创建触发器，名称随意，触发周期选择自定义，配置好cron表达式后，点击提交，下面的cron表达式代表每天早、晚的7:10分都会执行
    ```shell script
    0 10 7,19 * * * *
    ```
7. enjoy it!!!
8. 默认配置`config.yml`适用于`新乡医学院`

#### 如果你不会配置表单组默认选项配置，请先配置好user信息之后本地执行generate.py然后将分割线下的内容复制到配置文件中对应位置

#### 如遇到依赖问题，请去[`auto-sumit`](https://github.com/ZimoLoveShuang/auto-submit)项目下载`dependency.zip`，然后参考`auto-submit`项目的说明将函数依赖层添加到腾讯云函数

#### 如果不知道怎么配置经纬度信息，可以访问[这里](http://zuobiao.ay800.com/s/27/index.php)，将经纬度四舍五入保留六位小数之后的放入配置文件对应位置即可

# 注意

模拟登陆API目前有白嫖限制，具体请看我[auto-submit项目](https://github.com/ZimoLoveShuang/auto-submit)的说明

# 其他

1. 项目依赖于我的开源项目[模拟登陆 金智教务统一登陆系统 的API](https://github.com/ZimoLoveShuang/wisedu-unified-login-api)
2. `Cpdaily-Extension`是逆向今日校园APK后得到的，本质上就是对一个json对象进行了des加密，然后编码为了Base64字符串，加密解密实现可以参考[DESHelper](https://github.com/ZimoLoveShuang/yibinu-score-crawler/blob/master/src/main/java/wiki/zimo/scorecrawler/helper/DESHelper.java)
3. 也欢迎其他学校学子在此提交适用于自己学校的配置，命名规则为`config_xxxx.yml`，`xxxx`为学校英文简称