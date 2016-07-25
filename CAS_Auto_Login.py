import requests
from time import sleep
import time
import json
import sys
import os
import datetime

config = None


def log(s):
    ms = int(datetime.datetime.now().microsecond / 1000)
    ms = '%03d' % ms
    print('[' + time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())) + '.' + ms + '] ' + s)


def load_config():
    global config
    with open('config.json') as f:
        config = json.load(f)
    return config


def main():
    log("Program started.")
    os.chdir(os.path.dirname(sys.argv[0]))  # To read config in the same directory
    log('Reading configurations...')
    config = load_config()
    times_retry_login = config['max_times_retry_login']
    log('Configurations successfully imported.')
    while True:
        log('Checking network status...')
        try:
            login = requests.Session()
            test = login.get(config['testUrl'])
        except:
            log('Connection FAILED. Try again in ' + str(config['interval_retry_connection']) + ' sec.')
            sleep(config['interval_retry_connection'])
            continue
        while test.status_code != 204:

            log('You are offline. Starting login...')
            log('Start to get login information')

            start = test.text.find(r'action') + 8
            end = test.text.find(r'" method="post"')
            action = test.text[start:end]
            log('action= ' + action + ';')

            start = test.text.find(r'name="lt"') + 17
            lt = test.text[start:]
            end = lt.find(r'" />')
            lt = lt[0:end]
            # Get parameter "lt"
            log('lt= ' + lt + ';')

            start = test.text.find(r'name="execution"') + 24
            execution = test.text[start:]
            end = execution.find(r'" />')
            execution = execution[0:end]
            # Get parameter "execution"
            log('execution= ' + execution + ';')

            start = test.text.find(r'name="_eventId"') + 23
            end = start + 10
            _eventId = test.text[start:end]
            end = _eventId.find(r'" />')
            _eventId = _eventId[0:end]
            # Get parameter "_eventld"
            log('_eventId= ' + _eventId + ';')

            log('Login information acquired.')

            url = 'http://weblogin.sustc.edu.cn' + action
            username = config['username']
            password = config['password']
            # SUSTC CAS username (StudentID) and password
            data = 'username=' + username + '&password=' + password + '&lt=' + lt + '&execution=' + execution + '&_eventId=submit&submit=LOGIN'

            h = {'Host': 'weblogin.sustc.edu.cn', 'Connection': 'keep-alive', 'Cache-Control': 'max-age=0',
                 'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                 'Origin': 'http://weblogin.sustc.edu.cn', 'Upgrade-Insecure-Requests': '1',
                 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.112 Safari/537.36',
                 'Content-Type': 'application/x-www-form-urlencoded', 'DNT': '1', 'Referer': url,
                 'Accept-Encoding': 'gzip, deflate', 'Accept-Language': 'en-US,en;q=0.8,zh-CN;q=0.6,zh;q=0.4'}

            log('Login as ' + username)

            login.post(url, data=data, headers=h)
            log('Login information posted to the CAS server.')

            test = requests.get(config['testUrl'])

            if test.status_code != 204:
                times_retry_login -= 1
                if times_retry_login > 0:  # If keep trying to login too many times, it may trigger security alarm on the CAS server
                    log(
                        'Login FAILED. Try again in ' + str(config['interval_retry_login']) + ' sec. ' + str(
                            times_retry_login) + r' attempt(s) remaining.')
                else:
                    log('Login FAILED.' + r'Attempts used up. The program will quit.')
                    sys.exit('Login FAILED')

                sleep(config['interval_retry_login'])
            else:
                log('Login successful. Current user: ' + username)
                times_retry_login = config['max_times_retry_login']
                log('Login attempts reset to ' + str(times_retry_login) + ' .')

        log('Online. Re-check status in ' + str(config['interval_check_status']) + ' sec.')

        sleep(config['interval_check_status'])


if __name__ == '__main__':
    main()
