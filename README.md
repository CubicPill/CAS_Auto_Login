# CAS_Auto_Login
SUSTC network account auto login. Coded in Python.
Java version with GUI (discontinued): [caslogin-gui](https://github.com/CubicPill/caslogin-gui)
## Requirements
Python2.7+
requests==2.11.1
beautifulsoup4==4.5.3

## Configuration items

**captive_portal_server:** see [here](https://www.noisyfox.cn/45.html). Default is "http://captive.v2ex.co/generate_204"

**username**: Your SUSTC studnet ID

**password**: CAS login password

**interval_retry_connection**: In second. If the status check failed (e.g. the server was down or there is no Internet connection), how long the program will wait before next attempt. Default value is 30.

**interval_check_status**:  In second. Determine how long the program will wait before next status check. Default value is 60.

**interval_retry_login**:  In second. If the login failed (e.g. wrong username & password combination, login params were changed, or the CAS server was down), how long the program will wait before next attempt. Default value is 30.

**max_times_retry_login**: Maximum time the program will try to login to the server. Default value is 5.

## Settings for OpenWrt routers
If you use a router which has OpenWrt, then it's strongly recommended that you use the following script to reconnect to wan interface when the connection was down.

For the server will drop connections at a random period, then login script won't work if the interface is not reconnected.
use the following script:

	#!/bin/sh
	date > /root/rec_status
	if ! ping -c 1 114.114.114.114 > /dev/null
	then
	  date >> /root/reconnect.log
	  ifdown wan
	  sleep 2
	  ifup wan
	  echo 'successfully reconnected!' >> /root/reconnect.log
	fi
	exit 0

Save it to /etc/config/reconnect_wan.sh, then

>chmod 0775 /etc/config/reconnect_wan.sh

and add this to crontab in your luci configuration page, or use crontab -e

>\* * * * * /etc/config/reconnect_wan.sh

this script will run every 1 minute

## Contact
If there are any questions, please reach me on Telegram.   
[@CubicPill](https://www.telegram.me/CubicPill)