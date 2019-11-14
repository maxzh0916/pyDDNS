import re
import os
import requests
import configparser
import json
import time


def current_time():
    return time.strftime("%H:%M:%S", time.localtime())


def creat_config():
    config.add_section('General')
    config.set('General', 'wait_time', '60')

    config.add_section('Godaddy')
    config.set('Godaddy', 'enable', 'True')
    config.set('Godaddy', 'domain', 'example.com')
    config.set('Godaddy', 'key', 'UzQxLikm_46KxDFnbjN7cQjmw6wocia')
    config.set('Godaddy', 'secret', '46L26ydpkwMaKZV6uVdDWe')

    config.write(open('config.ini', 'w'))


def get_local_ip():
    response = requests.get("http://txt.go.sohu.com/ip/soip").content.decode()
    ip = re.search('\d+.\d+.\d+.\d+', response).group(0)
    print('[' + current_time() + ']' + '已获取本机公网IP，地址为：' + ip)
    return ip


def get_godaddy_record(url):
    response = requests.get('https://api.godaddy.com/v1/domains/' + url + '/records/A/@', headers=headers)
    if response.status_code == 200:
        record = response.json()[0]['data']
        print('[' + current_time() + ']' + '已获取Godaddy域名A记录，地址为：' + record)
        return record
    elif response.status_code == 401:
        print('[' + current_time() + ']' + 'Error:身份验证信息无效，请检查后重试！')
        exit()


def put_godaddy_record(url, ip):
    data = {
        "data": ip,
        "ttl": 600
    }
    response = requests.put('https://api.godaddy.com/v1/domains/' + url + '/records/A/@', headers=headers,
                            data=json.dumps([data]))
    if response.status_code == 200:
        print('[' + current_time() + ']' + 'Godaddy A记录更新成功！')
    elif response.status_code == 401:
        print('[' + current_time() + ']' + 'Error:身份验证信息无效，请检查后重试！')
        exit()


if __name__ == '__main__':
    config = configparser.ConfigParser()
    config.read('config.ini')
    # 创建config
    if not os.path.isfile('config.ini'):
        creat_config()
    headers = {
        'accept': 'application/json',
        'Content-Type': 'application/json',
        'Authorization': 'sso-key ' + config['Godaddy']['key'] + ':' + config['Godaddy']['secret']
    }
    while True:
        # 测试网络
        try:
            requests.get('https://baidu.com')
        except requests.exceptions.ConnectionError:
            print('[' + current_time() + ']' + 'Error:未连接网络，请连接后重试。')
            exit()

        local_ip = get_local_ip()  # 本机公网IP
        if config.getboolean('Godaddy', 'enable'):
            godaddy_record = get_godaddy_record(config['Godaddy']['domain'])
            if local_ip == godaddy_record:
                print('[' + current_time() + ']' + '本机公网IP与Godaddy域名A记录相同，等待' + config['General'][
                    'wait_time'] + '秒后重新检测。')
            else:
                put_godaddy_record(config['Godaddy']['domain'], local_ip)
        time.sleep(int(config['General']['wait_time']))
