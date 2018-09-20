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
import re




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
  rt = {}
  try:
      if kodiAlive():
        rt['result']='OK'
        helper.internalLogger.debug("status OK")
        aux=kodi.Player.GetActivePlayers()
        helper.internalLogger.debug("GetActivePlayers: {0}".format(aux))
        ''' TODO ONLY CONSIDER FIRST ITEM IN PLAYERS LIST '''
        if not aux['result']:
          helper.internalLogger.debug("Video Off")
          rt['play']=False
        else:
          rt['play']=True
          pid=aux['result'][0]['playerid']
          helper.internalLogger.debug("Player Id:{0}".format(pid))
          aux=kodi.Player.GetItem({"properties": ["title"], "playerid": pid })
          helper.internalLogger.debug("Video On Player {0}: {1}".format(1,aux))
          title=aux['result']['item']['title']
          label=aux['result']['item']['label']
          rt['title']=title+"-"+label
      rtjson=json.dumps(rt)

  except Exception as e:
    e = sys.exc_info()[0]
    helper.internalLogger.error('Error: kodi seems not be ready to ping')
    helper.einternalLogger.exception(e)  
    rtjson=jsonify({'result': 'KO'})
    helper.internalLogger.debug("status failed")

  return rtjson


'''----------------------------------------------------------'''
'''----------------       kodiAlive         -------------------'''
'''----------------------------------------------------------'''
def kodiAlive():
  rt=False
  try:
      aux=kodi.JSONRPC.Ping()
      #helper.internalLogger.debug("Ping: {0}".format(aux))      
      if aux['result'] == "pong":
        rt=True
  except Exception as e:
    e = sys.exc_info()[0]
    helper.internalLogger.error('Error: kodi seems not be ready to ping')
  return rt

'''----------------------------------------------------------'''
'''----------------       what2track        -------------------'''
'''----------------------------------------------------------'''

def what2track(config):
  rt={}
  try:
    with open(config["what"]) as json_data:
      rt = json.load(json_data)

  except Exception as e:
    helper.internalLogger.error("Error processing what to track in config".format(config))
    helper.einternalLogger.exception(e)

  return rt;

'''----------------------------------------------------------'''
'''----------------       fullMatch         -------------------'''
'''----------------------------------------------------------'''
def fullMatch(listOfkeys,target):
 rt=False
 matchedItems=0
 items=len(listOfkeys)
 for x in listOfkeys:
   #helper.internalLogger.debug("Trying to match'{0}' and '{1}'".format(target,x))
   #simple word base match 
   if x.lower() in target.lower() :
   #m = re.search(x,target)
   #if m:
     matchedItems=matchedItems+1

 if matchedItems>0:
     if matchedItems == items:
       helper.internalLogger.debug("Full match detected FOUND")
       rt=True
     else:
       helper.internalLogger.debug("Almost there but not enough matching: {0}/{1} - title  {2}, target content {3}".format(matchedItems,items,target,listOfkeys))

   
 return rt

'''----------------------------------------------------------'''
'''----------------       amIwatchingIt         -------------------'''
'''----------------------------------------------------------'''
def amIwatchingIt(c):
 rt=False
 try:
  aux=kodi.Player.GetActivePlayers()
  #helper.internalLogger.debug("GetActivePlayers: {0}".format(aux))
  ''' TODO ONLY CONSIDER FIRST ITEM IN PLAYERS LIST '''
  if not aux['result']:
   helper.internalLogger.debug("Video Off")
  else:
   pid=aux['result'][0]['playerid']
   #helper.internalLogger.debug("Player Id:{0}".format(pid))
   aux=kodi.Player.GetItem({"properties": ["title"], "playerid": pid })
   title=aux['result']['item']['title']
   label=aux['result']['item']['label']
   #Try to match keystrings on it title
   if "keystrings" in c:
     if fullMatch(c["keystrings"],title) or fullMatch(c["keystrings"],label):
       rt=True
     
 except Exception as e:
    e = sys.exc_info()[0]
    helper.internalLogger.error('Error: something goes bad trying to matching content keystring and now playing title')
    helper.einternalLogger.exception(e)  

 return rt

'''----------------------------------------------------------'''
'''----------------       pollAutoTracker        -------------------'''
'''----------------------------------------------------------'''

def pollAutoTracker(config):

  if not kodiAlive():
    helper.internalLogger.error("Tracker: kodi is ko, useless to try to track anything")
    return
  what= what2track(config)
  if not "content" in what:
    helper.internalLogger.debug("Tracker: nothing to track yet")
    return
  if not what["content"]:
    helper.internalLogger.debug("Tracker: empty list to track")
    return
  for c in what["content"]:
    helper.internalLogger.debug("Tracker: Checking status of content".format(c))
    amIwatchingIt(c)
    '''am i watching it
    ok
    else
    have i the tracker list
      try gather one /in ordered list
    else
      get the list livetv now
      filter by STRING
      get tracket list'''


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


  enableTracker=False
  pollingInterval=5
  if "auto-tracker" in configuration:
    if "enable" in configuration["auto-tracker"]:
      enableTracker=configuration["auto-tracker"]["enable"]
    if "polling-interval" in configuration["auto-tracker"]:
      pollingInterval=configuration["auto-tracker"]["polling-interval"]
        



  try:

    global kodi
    #Login with default kodi/kodi credentials
    if "login" in configuration["kodi"]:
      kodi = Kodi(configuration["kodi"]["url"],configuration["kodi"]["login"],configuration["kodi"]["password"])
    else:
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

     while True:
       if enableTracker:
         pollAutoTracker(configuration["auto-tracker"])
       time.sleep(pollingInterval)


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
