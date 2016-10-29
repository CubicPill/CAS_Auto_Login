import requests
from bs4 import BeautifulSoup
from time import sleep
import json
import sys
import os
import logging

config = None
logging.basicConfig(format="%(asctime)s - %(levelname)s - %(message)s", level=logging.DEBUG)


def load_config():
    global config
    with open('config.json') as f:
        config = json.load(f)
    return config


def main():
    logging.info('Program started.')
    try:
        os.chdir(os.path.dirname(sys.argv[0]))  # To read config in the same directory
    except OSError:
        pass
    logging.info('Reading configurations...')
    global config
    config = load_config()
    times_retry_login = config['max_times_retry_login']
    test_url = config['captive_portal_server'] + '/generate_204'
    logging.info('Configurations successfully imported.')
    while True:
        logging.info('Checking network status...')
        try:
            login = requests.Session()
            test = login.get(test_url, timeout=30)
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

            info = {}
            for element in soup_login.find('form').find_all('input'):
                if element.has_attr('value'):
                    info[element['name']] = element['value']

            logging.debug(info)

            logging.info('Login information acquired.')

            info['username'] = config['username']
            info['password'] = config['password']

            url = 'https://cas.sustc.edu.cn{}'.format(action)

            h = {
                # 'Host': 'cas.sustc.edu.cn',
                # 'Connection': 'keep-alive',
                'Cache-Control': 'max-age=0',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Origin': 'http://cas.sustc.edu.cn',
                # 'Upgrade-Insecure-Requests': '1',
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.112 Safari/537.36',
                'Content-Type': 'application/x-www-form-urlencoded',
                'DNT': '1',
                'Referer': url,
                'Accept-Encoding': 'gzip, deflate', 'Accept-Language': 'en-US,en;q=0.8,zh-CN;q=0.6,zh;q=0.4'
            }

            logging.info('Login as ' + config['username'])

            r = login.post(url, data=info, headers=h, timeout=30)
            logging.info('Login information posted to the CAS server.')
            soup_response = BeautifulSoup(r.content, 'html5lib')
            success = soup_response.find('div', {'class': 'success'})
            err = soup_response.find('div', {'class': 'errors'})
            if err:
                times_retry_login -= 1
                logging.error('An error occurred.')
                logging.error(err.h2.text)
                logging.error(err.p.text)
                if times_retry_login > 0:  # If keep trying to login too many times, it may trigger security alarm on the CAS server
                    logging.info(
                        'Login FAILED. Try again in ' + str(config['interval_retry_login']) + ' sec. ' + str(
                            times_retry_login) + r' attempt(s) remaining.')
                else:
                    logging.info('Login FAILED.' + r'Attempts used up. The program will quit.')
                    sys.exit('Login FAILED')

                sleep(config['interval_retry_login'])

            elif success:
                logging.info('Login successful')
                times_retry_login = config['max_times_retry_login']
                logging.info('Login attempts reset to ' + str(times_retry_login) + ' .')
                break

        logging.info('Online. Re-check status in ' + str(config['interval_check_status']) + ' sec.')

        sleep(config['interval_check_status'])


if __name__ == '__main__':
    main()
