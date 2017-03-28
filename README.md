# CAS_Auto_Login
SUSTC network account auto login. Coded in Python. 
Java version with GUI (discontinued): [caslogin-gui](https://github.com/CubicPill/caslogin-gui)
## Requirements
Python3
requests 2.10.0
BeautifulSoup4

## Configuration items

>'captive_portal_server': see [here](https://www.noisyfox.cn/45.html). Default is "http://captive.v2ex.co/generate_204"
'username': Your SUSTC studnet ID
'password': CAS login password
'interval_retry_connection': In second. If the status check failed (e.g. the server was down or there is no Internet connection), how long the program will wait before next attempt. Default value is 30.
'interval_check_status':  In second. Determine how long the program will wait before next status check. Default value is 60.
'interval_retry_login':  In second. If the login failed (e.g. wrong username & password combination, login params were changed, or the CAS server was down), how long the program will wait before next attempt. Default value is 30.
'max_times_retry_login': Maximum time the program will try to login to the server. Default value is 5.

## Contact
If there are any questions, please reach me on Telegram.   
[@CubicPill](https://www.telegram.me/CubicPill)