#!/bin/bash
source /home/eespjul/prj/miniIPA/gasdk/env/bin/activate
source /home/pi/env/bin/activate
amixer -c 0 set PCM unmute
amixer -c 0 set PCM 100%
python /opt/ipaem/gaIpaDispatcher/gaIpaDispatcher.py 
