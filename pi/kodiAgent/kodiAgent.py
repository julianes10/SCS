#!/usr/bin/env python
import argparse
import time
import datetime
import sys
import json
import subprocess
import os
import platform
import threading
import helper
from random import randint
from kodijson import Kodi, PLAYER_VIDEO


#Code copy and adapted from https://github.com/adafruit/Adafruit_Python_DHT/blob/master/examples/simpletest.py


from flask import Flask, jsonify,abort,make_response,request, url_for

from helper import *


configuration={}

'''----------------------------------------------------------'''
'''----------------      API REST         -------------------'''
'''----------------------------------------------------------'''
api = Flask("api")


@api.route('/api/v1.0/kodi/status', methods=['GET'])
def get_kodi_status():
  helper.internalLogger.debug("status required")
  try:
      aux=kodi.JSONRPC.Ping()
      if aux['result'] == "pong":
        rt=jsonify({'result': 'OK'})
        helper.internalLogger.debug("status OK")

  except Exception as e:
    e = sys.exc_info()[0]
    helper.internalLogger.error('Error: kodi seems not be ready to ping')
    helper.einternalLogger.exception(e)  
    rt=jsonify({'result': 'KO'})
    helper.internalLogger.debug("status failed")

  return rt


'''----------------------------------------------------------'''
'''----------------       M A I N         -------------------'''
'''----------------------------------------------------------'''

def main(configfile):
  print('kodiAgent-start -----------------------------')

  
  # Loading config file,
  # Default values
  cfg_log_traces="kodiAgent.log"
  cfg_log_exceptions="kodiAgente.log"
  cfg_SensorsDirectory={}
  # Let's fetch data
  with open(configfile) as json_data:
      configuration = json.load(json_data)
  #Get log names
  if "log" in configuration:
      if "logTraces" in configuration["log"]:
        cfg_log_traces = configuration["log"]["logTraces"]
      if "logExceptions" in configuration["log"]:
        cfg_log_exceptions = configuration["log"]["logExceptions"]
  helper.init(cfg_log_traces,cfg_log_exceptions)
  print('See logs traces in: {0} and exeptions in: {1}-----------'.format(cfg_log_traces,cfg_log_exceptions))  
  helper.internalLogger.critical('kodiAgent-start -------------------------------')  
  helper.einternalLogger.critical('kodiAgent-start -------------------------------')


  try:

    global kodi
    #Login with default kodi/kodi credentials
    kodi = Kodi(configuration["kodi"]["url"])
  
    apiRestTask=threading.Thread(target=apirest_task,name="restapi")
    apiRestTask.daemon = True
    apiRestTask.start()

  except Exception as e:
    helper.internalLogger.critical("Error processing configuration json {0} file. Exiting".format(configfile))
    helper.einternalLogger.exception(e)
    loggingEnd()
    return  

  try:    
     ''' initialize contets '''
     while True:
        time.sleep(1000)


  except Exception as e:
    e = sys.exc_info()[0]
    helper.internalLogger.critical('Error: Exception unprocessed properly. Exiting')
    helper.einternalLogger.exception(e)  
    print('kodiAgent-General exeception captured. See log:{0}',format(cfg_log_exceptions))        
    loggingEnd()

'''----------------------------------------------------------'''
'''----------------     apirest_task      -------------------'''
def apirest_task():
  api.run(debug=True, use_reloader=False,port=5057,host='0.0.0.0')


'''----------------------------------------------------------'''
'''----------------       loggingEnd      -------------------'''
def loggingEnd():      
  helper.internalLogger.critical('kodiAgent-end -----------------------------')        
  print('kodiAgent-end -----------------------------')


'''----------------------------------------------------------'''
'''----------------     parse_args        -------------------'''
def parse_args():
    """Parse the args."""
    parser = argparse.ArgumentParser(
        description='Simple dht tracker')
    parser.add_argument('--configfile', type=str, required=False,
                        default='/etc/kodiAgent.conf',
                        help='Config file for the service')
    return parser.parse_args()

'''----------------------------------------------------------'''
'''----------------    printPlatformInfo  -------------------'''
def printPlatformInfo():
    print("Running on OS '{0}' release '{1}' platform '{2}'.".format(os.name,platform.system(),platform.release()))
    print("Uname raw info: {0}".format(os.uname()))
    print("Arquitecture: {0}".format(os.uname()[4]))
    print("Python version: {0}".format(sys.version_info))

'''----------------------------------------------------------'''
'''----------------       '__main__'      -------------------'''
if __name__ == '__main__':
    printPlatformInfo()
    args = parse_args()
    main(configfile=args.configfile)



'''
Wrapper to access kodi using jsonrpc basic commands
Here we go: --checkPlayer
Check player...
HTTP/1.1 200 OK
Connection: Keep-Alive
Content-Type: application/json
Content-Length: 65
Cache-Control: private, max-age=0, no-cache
Accept-Ranges: none
Date: Fri, 07 Sep 2018 22:00:40 GMT

{"id":1,"jsonrpc":"2.0","result":[{"playerid":1,"type":"video"}]}pi@pi32:/opt/ipaem/gaIpaDispatcher $ 
'''
