# -*- coding: utf-8 -*-
import index as app
import yaml


# 生成默认配置
def generate():
    params = app.getUnSignedTasks()
    task = app.getDetailTask(params)
    extraFields = task['extraField']
    if len(extraFields) < 1:
        app.log('没有附加选项需要填写')
        exit(-1)
    defaults = []
    for i in range(0, len(extraFields)):
        extraField = extraFields[i]
        extraFieldItems = extraField['extraFieldItems']
        print('额外选项%d ' % (i + 1) + extraField['title'])
        default = {}
        one = {}
        for j in range(0, len(extraFieldItems)):
            extraFieldItem = extraFieldItems[j]
            print('\t%d ' % (j + 1) + extraFieldItem['content'])
        choose = int(input("请输入对应的序号："))
        if choose < 1 or choose > len(extraFieldItems):
            app.log('输入错误')
            exit(-1)
        one['title'] = extraField['title']
        one['value'] = extraFieldItems[choose - 1]['content']
        default['default'] = one
        defaults.append(default)
    print('======================分隔线======================')
    print(yaml.dump(defaults, allow_unicode=True))


if __name__ == "__main__":
    generate()
