# CAS_Auto_Login
SUSTC network account auto login. Coded in Python. Java version with GUI is coming soon.      
[caslogin-gui](https://github.com/NorrisHua/caslogin-gui)
## Requirements
Python 2.7+
requests 2.10.0
### Installation
    pip install requests
## Configuration items
'username': Your SUSTC studnet ID   
'password': CAS login password  
'interval_retry_connection': In second. If the status check failed (e.g. the server was down or there is no Internet connection), how long the program will wait before next attempt. Default value is 20.  
'interval_check_status':  In second. Determine how long the program will wait before next status check. Default value is 300.  
'interval_retry_login':  In second. If the login failed (e.g. wrong username & password combination, or the CAS server was down), how long the program will wait before next attempt. Default value is 10.  
'max_times_retry_login': Maximum time the program will try to login to the server. Default value is 5.
## Contacts
If there are any questions, please reach me on Telegram.   
[@NorrisHua](https://www.telegram.me/NorrisHua)