import requests
from bs4 import BeautifulSoup
from time import sleep
import json
import sys
import os
import logging

config = None
logging.basicConfig(format="%(asctime)s - %(levelname)s - %(message)s", level=logging.INFO)


def load_config():
    global config
    with open('config.json') as f:
        config = json.load(f)
    return config


def main():
    logging.info('Program started.')
    os.chdir(os.path.dirname(sys.argv[0]))  # To read config in the same directory
    logging.info('Reading configurations...')
    config = load_config()
    times_retry_login = config['max_times_retry_login']
    test_url = config['captive_portal_server'] + '/generate_204'
    logging.info('Configurations successfully imported.')
    while True:
        logging.info('Checking network status...')
        try:
            login = requests.Session()
            test = login.get(test_url)
        except:
            logging.info('Connection FAILED. Try again in ' + str(config['interval_retry_connection']) + ' sec.')
            sleep(config['interval_retry_connection'])
            continue
        while test.status_code != 204:

            soup_login = BeautifulSoup(test.content, 'html5lib')
            if 'CAS' not in soup_login.title.string:
                logging.warning('Not connected to a SUSTC network')
                sleep(config['interval_retry_connection'])
                break

            logging.info('You are offline. Starting login...')
            logging.info('Start to get login information')

            action = soup_login.find('form', id='fm1')['action']  # get login url
            logging.debug('action= ' + action)

            lt = soup_login.find('input', attrs={'name': 'lt'})['value']  # Get parameter "lt"
            logging.debug('lt= ' + lt)

            execution = soup_login.find('input', attrs={'name': 'execution'})['value']  # Get parameter "execution"
            logging.debug('execution= ' + execution)

            logging.info('Login information acquired.')

            url = 'http://weblogin.sustc.edu.cn{}'.format(action)

            data = 'username={}&password={}&lt={}&execution={}&_eventId=submit&submit=LOGIN'. \
                format(config['username'], config['password'], lt, execution)

            h = {'Host': 'weblogin.sustc.edu.cn', 'Connection': 'keep-alive', 'Cache-Control': 'max-age=0',
                 'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                 'Origin': 'http://weblogin.sustc.edu.cn', 'Upgrade-Insecure-Requests': '1',
                 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.112 Safari/537.36',
                 'Content-Type': 'application/x-www-form-urlencoded', 'DNT': '1', 'Referer': url,
                 'Accept-Encoding': 'gzip, deflate', 'Accept-Language': 'en-US,en;q=0.8,zh-CN;q=0.6,zh;q=0.4'}

            logging.info('Login as ' + config['username'])

            r = login.post(url, data=data, headers=h)
            logging.info('Login information posted to the CAS server.')
            soup_response = BeautifulSoup(r.content, 'html5lib')

            if soup_response.find('div', id='msg')['class'][0] != 'success':
                times_retry_login -= 1
                if times_retry_login > 0:  # If keep trying to login too many times, it may trigger security alarm on the CAS server
                    logging.info(
                        'Login FAILED. Try again in ' + str(config['interval_retry_login']) + ' sec. ' + str(
                            times_retry_login) + r' attempt(s) remaining.')
                else:
                    logging.info('Login FAILED.' + r'Attempts used up. The program will quit.')
                    sys.exit('Login FAILED')

                sleep(config['interval_retry_login'])
            else:
                logging.info('Login successful')
                times_retry_login = config['max_times_retry_login']
                logging.info('Login attempts reset to ' + str(times_retry_login) + ' .')
                break

        logging.info('Online. Re-check status in ' + str(config['interval_check_status']) + ' sec.')

        sleep(config['interval_check_status'])


if __name__ == '__main__':
    main()
