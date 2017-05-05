import json
import logging
import os
import re
import sys
from time import sleep

import requests
from bs4 import BeautifulSoup

logging.basicConfig(format="%(asctime)s - %(levelname)s - %(message)s", level=logging.DEBUG)
logging.getLogger('requests').setLevel(logging.WARNING)
login = requests.session()

CONNECTED = 10001
CONNECTION_TIMEOUT = 10002
NEED_LOGIN = 10003


def load_config():
   with open('./config.json') as f:
      config = json.load(f)
   return config


def do_login(url, username, password):
   soup_login = BeautifulSoup(login.get(url).content, 'html5lib')
   logging.info('Start to get login information')

   action = soup_login.find('form', id='fm1')['action']  # get login url
   logging.debug('action= ' + action)

   info = {}
   for element in soup_login.find('form').find_all('input'):
      if element.has_attr('value'):
         info[element['name']] = element['value']

   logging.debug(info)

   logging.info('Login information acquired.')

   info['username'] = username
   info['password'] = password

   url = 'https://cas.sustc.edu.cn{}'.format(action)

   logging.info('Login as ' + username)

   r = login.post(url, data=info, timeout=30)
   logging.info('Login information posted to the CAS server.')
   soup_response = BeautifulSoup(r.content, 'html5lib')
   success = soup_response.find('div', {'class': 'success'})
   err = soup_response.find('div', {'class': 'errors', 'id': 'msg'})
   return success, err


def test_network(url):
   try:
      test = login.get(url, timeout=30)
      content = test.content
      if test.status_code == 204:
         status = CONNECTED
      else:
         status = NEED_LOGIN
   except requests.Timeout:
      status = CONNECTION_TIMEOUT
      content = None

   return status, content


def main():
   logging.info('Program started.')
   try:
      os.chdir(os.path.dirname(sys.argv[0]))  # To read config in the same directory
   except OSError:
      pass
   config = load_config()
   times_retry_login = config['max_times_retry_login']
   test_url = config['captive_portal_server']
   logging.info('Configurations successfully imported.')
   while True:
      logging.info('Checking network status...')
      status, content = test_network(test_url)
      if status == CONNECTION_TIMEOUT:
         logging.info('Connection FAILED. Try again in ' + str(config['interval_retry_connection']) + ' sec.')
         sleep(config['interval_retry_connection'])
         continue

      while status == NEED_LOGIN:
         soup_login = BeautifulSoup(content, 'html5lib')
         if 'CAS' not in soup_login.title.string:
            logging.warning('Not connected to a SUSTC network')
            sleep(config['interval_retry_connection'])
            continue

         logging.info('You are offline. Starting login...')

         hostname = 'http://enet.10000.gd.cn:10001/sz/sz112/'
         rem_link = re.search(r'window\.location = \'(.*)\';', soup_login.text).group(1)
         url = hostname + rem_link

         success, err = do_login(url, config['username'], config['password'])

         if err:
            times_retry_login -= 1
            logging.error('Error occurred: ' + err.text)
            if times_retry_login > 0:
               # If keep trying to login too many times, it may trigger security alarm on the CAS server
               logging.info(
                  'Login FAILED. Try again in {time} sec. {attempt} attempt(s) remaining.'
                     .format(time=config['interval_retry_login'], attempt=times_retry_login))
            else:
               logging.info('Login FAILED. Attempts used up. The program will quit.')
               sys.exit(1)
            sleep(config['interval_retry_login'])

         elif success:
            logging.info('Login successful')
            times_retry_login = config['max_times_retry_login']
            logging.info('Login attempts reset to {attempt}.'.format(attempt=times_retry_login))
            break

      logging.info('Online. Re-check status in {time} sec.'.format(time=config['interval_check_status']))

      sleep(config['interval_check_status'])


if __name__ == '__main__':
   main()
