import requests
from time import sleep
import time
import json
import sys
import os
import datetime

    
    
def printWithTimeStamp(s):
    ms=int(datetime.datetime.now().microsecond/1000)
    ms='%03d'%ms
    print ('['+time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))+'.'+ms+'] '+s)     
    
def newConfig():
    username=input('Username: ')
    passwd=input('Password: ')
    f=open('config.json','w')
    config={"username": username, "password": passwd, "testUrl": "http://g.cn", "interval_retry_connection": "20", "interval_retry_login": "10", "interval_check_status": "300"}
    f.write(json.dumps(config))
    f.close()
    printWithTimeStamp('Configurations successfully saved.')    
    return config
    
def readConfig():
    try:
        f=open('config.json')
        try:
            config=json.loads(f.readline())
            config and config['interval_retry_login'] and config['interval_check_status'] and config['username'] and config['password'] and config['interval_retry_connection'] and config['testUrl']
        except KeyError as err:
            printWithTimeStamp('Parameter '+str(err)+' not found.')
            printWithTimeStamp('Configuration file is broken. Create a new one.')
            f.close()
            os.remove('config.json')
            newConfig()
    except PermissionError as err:
        sys.exit(err)
    return config

def loadConfig():
    if os.path.isfile('config.json'):
        return readConfig()
    else:
        printWithTimeStamp('No configuration file found.')
        return newConfig()

def ifLoggedIn(test):
    if test.text.find(r'Central Authentication Service') == -1:
        return True
    return False
  
def main():    
    printWithTimeStamp('Reading configurations...')
    config=loadConfig()
    printWithTimeStamp('Configurations successfully imported.')
    while True:
        printWithTimeStamp('Checking network status...')
        try:
            test=requests.get(config['testUrl'])
        except:
            printWithTimeStamp('Connection FAILED. Try again in '+config['interval_retry_connection']+' sec.')
            sleep(int(config['interval_retry_connection']))
            continue
        while not ifLoggedIn(test):
            printWithTimeStamp('You are offline. Starting login...')
            start=test.text.find(r'wlanuserip')+13
            end=test.text.find(r'&locale=')
            if start != 12:
                wlanuserip=test.text[start:end]

            start=test.text.find(r'wlanacip')+11
            end=test.text.find(r'%26wlanuserip')
            if start != 10:
                wlanacip=test.text[start:end]
        
            printWithTimeStamp('Parameters successfully acquired. wlanacip = '+wlanacip+', wlanuserip = '+wlanuserip)

            h={'Host': 'weblogin.sustc.edu.cn', 'Connection': 'keep-alive', 'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8', 'Upgrade-Insecure-Requests': '1' ,'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.112 Safari/537.36', 'DNT': '1', 'Accept-Encoding': 'gzip, deflate, sdch', 'Accept-Language': 'en-US,en;q=0.8,zh-CN;q=0.6,zh;q=0.4'}
        
            url='http://weblogin.sustc.edu.cn/cas/login?service=http%3A%2F%2Fenet.10000.gd.cn%3A10001%2Fsz%2Fsz112%2Findex.jsp%3Fwlanacip%3D'+wlanacip+'%26wlanuserip%3D'+wlanuserip
        
            printWithTimeStamp('Start to get login information')

            prelogin=requests.get(url,headers=h)
        
            printWithTimeStamp('Login information acquired.')
        
            start=prelogin.text.find(r'name="lt"')+17
            end=start+50
            lt=prelogin.text[start:end]
            end=lt.find(r'" />')
            lt=lt[0:end]
        
            start=prelogin.text.find(r'name="execution"')+24
            end=start+10
            execution=prelogin.text[start:end]
            end=execution.find(r'" />')
            execution=execution[0:end]
        
            start=prelogin.text.find(r'name="_eventId"')+23
            end=start+10
            _eventId=prelogin.text[start:end]
            end=_eventId.find(r'" />')
            _eventId=_eventId[0:end]
        
            end=prelogin.headers['Set-Cookie'].find(r'; Path=/cas/;')
            JSESSIONID_SUSTC= prelogin.headers['Set-Cookie'][11:end]
        
            printWithTimeStamp('Parameter JSESSIONID acquired. JSESSIONID = '+JSESSIONID_SUSTC)

            url='http://weblogin.sustc.edu.cn/cas/login;jsessionid='+JSESSIONID_SUSTC+'?service=http://enet.10000.gd.cn%3A10001%2Fsz%2Fsz112%2Findex.jsp%3Fwlanacip%3D'+wlanacip+'%26wlanuserip%3D'+wlanuserip
            username=config['username']
            passwd=config['password']
            data='username='+username+'&password='+passwd+'&lt='+lt+'&execution='+execution+'&_eventId='+_eventId+'&submit=LOGIN'

            h={'Host': 'weblogin.sustc.edu.cn', 'Connection': 'keep-alive', 'Cache-Control': 'max-age=0', 'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8', 'Origin': 'http://weblogin.sustc.edu.cn', 'Upgrade-Insecure-Requests': '1', 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.112 Safari/537.36', 'Content-Type': 'application/x-www-form-urlencoded', 'DNT': '1', 'Referer': url, 'Accept-Encoding': 'gzip, deflate', 'Accept-Language': 'en-US,en;q=0.8,zh-CN;q=0.6,zh;q=0.4'}
        
            cookies=dict({'Cookie': 'JSESSIONID='+JSESSIONID_SUSTC})
            login=requests.Session()
            printWithTimeStamp('Login as '+username)

            login.post(url,data=data,headers=h,cookies=cookies)        
            printWithTimeStamp('Login information posted to the CAS server.')

            test=requests.get(config['testUrl'])
            if not ifLoggedIn(test):
                printWithTimeStamp('Login FAILED. Try again in '+config['interval_retry_login']+' sec. ')
                sleep(int(config['interval_retry_login']))
            if ifLoggedIn(test):
                printWithTimeStamp('Login successful. Current user: '+username)
    
        printWithTimeStamp('Online. Re-check status in '+config['interval_check_status']+' sec.')    
        
        
        sleep(int(config['interval_check_status']))

if __name__ == '__main__':
    main()   