#!/bin/bash
# TUNE TO TEST IN PC source $HOME/ROUTE TO /env/bin/activate
source /home/pi/env/bin/activate
amixer -c 0 set PCM unmute
amixer -c 0 set PCM 100%
#NOTE IT WILL PICK AS DEFAULT:
# --configfile  '/etc/ipaem/ipaem.conf'
# --credentials '/etc/ipaem/google-oauthlib-tool/credentials.json'
python /opt/PROJECT_NAME/ipaDispatcher/ipaDispatcher.py  --configfile  /etc/ipaDispatcher.conf 
