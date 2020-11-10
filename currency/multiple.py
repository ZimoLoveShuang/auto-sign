#!/usr/bin/python3
#-*-coding:utf-8;-*-
import sys
import index as cpdaily
import yaml
import json
import requests
import uuid

log = cpdaily.login.log

def getTaskList(yaml_file='tasks.yml'):
    file_data = '[]'
    with open(yaml_file, 'r', encoding="utf-8") as f:
        file_data = f.read()
    tasks = yaml.load(file_data, Loader=yaml.SafeLoader)
    return tasks

def ReloadCpdailyLogin(config_file):
    # Ugly hack :(
    # 全局配置
    cpdaily.login.config = cpdaily.login.getYmlConfig(config_file)
    cpdaily.login.session = requests.session()
    cpdaily.login.user = cpdaily.login.config['user']
    # Cpdaily-Extension
    cpdaily.login.extension = {
        "lon": cpdaily.login.user['lon'],
        "model": "PCRT00",
        "appVersion": "8.0.8",
        "systemVersion": "4.4.4",
        "userId": cpdaily.login.user['username'],
        "systemName": "android",
        "lat": cpdaily.login.user['lat'],
        "deviceId": str(uuid.uuid1())
    }
    cpdaily.login.CpdailyInfo = cpdaily.login.DESEncrypt(json.dumps(cpdaily.login.extension))
    cpdaily.login.apis = cpdaily.login.getCpdailyApis(cpdaily.login.user)
    cpdaily.login.host = cpdaily.login.apis['host']

def ReloadCpdaily(config_file, session_file):
    ReloadCpdailyLogin(config_file)
    cpdaily.config = cpdaily.getYmlConfig(config_file)
    cpdaily.user = cpdaily.config['user']
    cpdaily.restoreSessionFromYml(session_file)

def main():
    count = 0
    for task in getTaskList():
        count += 1
        try:
            log("Reloading config for Task #{} ...".format(count))
            config_file, session_file = task['config'], task['session']
            ReloadCpdaily(config_file, session_file)
            data = {
                'sessionToken': cpdaily.sessionToken
            }
            cpdaily.login.getModAuthCas(data)
            params = cpdaily.getUnSignedTasks()
            # log(params)
            task = cpdaily.getDetailTask(params)
            # log(task)
            form = cpdaily.fillForm(task)
            # log(form)
            cpdaily.submitForm(form)
        except Exception as e:
            log("Error in task {}: {}".format(count, str(e)))
            raise e

if __name__ == '__main__':
    main()
