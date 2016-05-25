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
    #May cause errors when string s contains unicode characters
    
def newConfig():
#Set up new config using default settings
    username=input('Username: ')
    passwd=input('Password: ')
    f=open('config.json','w')
    config={"username": str(username), "password": str(passwd), "testUrl": "http://www.v2ex.com/generate_204", "interval_retry_connection": "30", "interval_retry_login": "30", "interval_check_status": "60", "max_times_retry_login": "5"}
    f.write(json.dumps(config))
    f.close()
    printWithTimeStamp('Configurations successfully saved.')    
    
def readConfig():
    try:
        f=open('config.json')
        try:
            initconfig=json.loads(f.readline())
            config={"username": initconfig['username'], "password": initconfig['password'], "testUrl": initconfig['testUrl'], "interval_retry_connection": int(initconfig['interval_retry_connection']), "interval_retry_login": int(initconfig['interval_retry_login']), "interval_check_status": int(initconfig['interval_check_status']), "max_times_retry_login": int(initconfig['max_times_retry_login'])}
            #Check if the parameters all exist and transform format
        except KeyError as kerr:
            printWithTimeStamp('Parameter '+str(kerr)+' not found.')
            printWithTimeStamp('Configuration file is broken. Create a new one.')
            f.close()
            os.remove('config.json')
            newConfig()
        except ValueError as verr:
            printWithTimeStamp('Parameter '+str(verr)+' is invalid.')
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
        newConfig()
        return readConfig()


  
def main():
    printWithTimeStamp("Program started.")
    os.chdir(os.path.dirname(sys.argv[0])) # To read config in the same directory
    printWithTimeStamp('Reading configurations...')
    config=loadConfig()
    times_retry_login=config['max_times_retry_login']
    printWithTimeStamp('Configurations successfully imported.')
    while True:
        printWithTimeStamp('Checking network status...')
        try:
            login=requests.Session()
            test=login.get(config['testUrl'])
        except:
            printWithTimeStamp('Connection FAILED. Try again in '+str(config['interval_retry_connection'])+' sec.')
            sleep(config['interval_retry_connection'])
            continue
        while test.status_code!=204:
        
            printWithTimeStamp('You are offline. Starting login...')
            printWithTimeStamp('Start to get login information')
            
            start=test.text.find(r'action')+8
            end=test.text.find(r'" method="post"')
            action=test.text[start:end] 

                
            start=test.text.find(r'name="lt"')+17
            end=start+50
            lt=test.text[start:end]
            end=lt.find(r'" />')
            lt=lt[0:end]
            #Get parameter "lt"
            
            start=test.text.find(r'name="execution"')+24
            end=start+10
            execution=test.text[start:end]
            end=execution.find(r'" />')
            execution=execution[0:end]
            #Get parameter "execution"
        
            start=test.text.find(r'name="_eventId"')+23
            end=start+10
            _eventId=test.text[start:end]
            end=_eventId.find(r'" />')
            _eventId=_eventId[0:end]
            #Get parameter "_eventld"
                 
            printWithTimeStamp('Login information acquired.')

        
            url='http://weblogin.sustc.edu.cn'+action
            username=config['username']
            passwd=config['password']
            #SUSTC CAS username (StudentID) and password
            data='username='+username+'&password='+passwd+'&lt='+lt+'&execution='+execution+'&_eventId='+_eventId+'&submit=LOGIN'

            h={'Host': 'weblogin.sustc.edu.cn', 'Connection': 'keep-alive', 'Cache-Control': 'max-age=0', 'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8', 'Origin': 'http://weblogin.sustc.edu.cn', 'Upgrade-Insecure-Requests': '1', 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.112 Safari/537.36', 'Content-Type': 'application/x-www-form-urlencoded', 'DNT': '1', 'Referer': url, 'Accept-Encoding': 'gzip, deflate', 'Accept-Language': 'en-US,en;q=0.8,zh-CN;q=0.6,zh;q=0.4'}

            printWithTimeStamp('Login as '+username)

            login.post(url,data=data,headers=h)        
            printWithTimeStamp('Login information posted to the CAS server.')

            test=requests.get(config['testUrl'])
            
            if test.status_code!=204 :
                times_retry_login-=1
                if times_retry_login>0: # If keep trying to login too many times, it may trigger security alarm on the CAS server
                    printWithTimeStamp('Login FAILED. Try again in '+str(config['interval_retry_login'])+' sec. '+str(times_retry_login)+r' attempt(s) remaining.')
                else:
                    printWithTimeStamp('Login FAILED.' +r'Attempts used up. The program will quit.')
                    sys.exit('Login FAILED')
                
                sleep(config['interval_retry_login'])
            else:
                printWithTimeStamp('Login successful. Current user: '+username)
                times_retry_login=config['max_times_retry_login']
                printWithTimeStamp('Login attempts reseted to '+str(times_retry_login)+' .')
                
    
        printWithTimeStamp('Online. Re-check status in '+str(config['interval_check_status'])+' sec.')    
        
        
        sleep(config['interval_check_status'])

if __name__ == '__main__':
    main()   