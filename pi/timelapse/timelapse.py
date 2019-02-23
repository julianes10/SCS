#!/usr/bin/env python3
import argparse
import time
import datetime
import sys
import json
import subprocess
import os
import signal
import platform
import threading
import helper
from random import randint
import re
import random


lastPictureTime = 0

def getVersion():
   rt={}
   try:
     if "vsw-file" in configuration:
       with open(configuration["vsw-file"]) as json_data:
          rt=json.load(json_data)
   except Exception as e:
        helper.internalLogger.error('no vsw json data')
        helper.einternalLogger.exception(e)  
   return rt


from flask import Flask, jsonify,abort,make_response,request, url_for

from helper import *


'''----------------------------------------------------------'''
'''----------------      API REST         -------------------'''
'''----------------------------------------------------------'''
api = Flask("api")


@api.route('/api/v1.0/timelapse/status', methods=['GET'])
def get_timelapse_status():
  return rtjson

@api.route('/api/v1.0/timelapse/project', methods=['POST'])
def post_timelapse_tracker():
    rt=jsonify({'result': 'OK'})
    if not request.json: 
        abort(400)
    abort(400)
'''
    if "auto-tracker" in configuration:
      if "what" in configuration["auto-tracker"]:
        with open(configuration["auto-tracker"]["what"], 'w') as outfile:
          json.dump(request.json, outfile)
          return rt, 201
'''




'''----------------------------------------------------------'''
'''----------------       checkOngoingPrj    -------------------'''
'''----------------------------------------------------------'''

def checkOngoingPrj(c):

  ''' helper.internalLogger.debug("Tracker: checkOngoingPrj...")
  '''
  if not "interval"  in c:
    return 

  global lastPictureTime

  now=time.time()
  if lastPictureTime == 0 or lastPictureTime + c["interval"] < now:
    lastPictureTime=now
    #TODO MAKEFOTO
    path=configuration["mediaPath"]+"/"+c["name"]
    pathfile=path+"/"+c["name"]+"."+str(lastPictureTime)
    try:
        os.makedirs(path)
    except FileExistsError:
        # directory already exists
        pass
    helper.internalLogger.debug("Tracker: Project {0}, taking photo:".format(pathfile))
    # mencoder mf://*.jpg -mf w=1920:h=1080:fps=25:type=jpg -ovc lavc -lavcopts vcodec=msmpeg4v2:vbitrate=16000:keyint=15:mbd=2:trell -oac copy -o output.avi.


'''----------------------------------------------------------'''
'''----------------       pollProjects    -------------------'''
'''----------------------------------------------------------'''

def pollProjects():



  try:
    if "projectDB" in configuration:
      with open(configuration["projectDB"]) as json_data:
        projects = json.load(json_data)
    else:
      helper.internalLogger.debug("Tracker: No projects DB found...")
      return

  except Exception as e:
    helper.internalLogger.critical("Error processing configuration json {0} file. Exiting".format(configuration["projectDB"]))
    helper.einternalLogger.exception(e)
    return 

  for c in projects:
    if "status" in c and "name" in c:
      helper.internalLogger.debug("Tracker: Checking status of project {0}:{1}".format(c['name'],c['status']))
      if c["status"] == "ONGOING":
        checkOngoingPrj(c) 

'''----------------------------------------------------------'''
'''----------------       M A I N         -------------------'''
'''----------------------------------------------------------'''

def main(configfile):
  print('timelapse-start -----------------------------')

  # Loading config file,
  # Default values
  cfg_log_traces="timelapse.log"
  cfg_log_exceptions="timelapsee.log"
  cfg_SensorsDirectory={}
  # Let's fetch data
  global configuration
  configuration={}
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
  helper.internalLogger.critical('timelapse-start -------------------------------')  
  helper.einternalLogger.critical('timelapse-start -------------------------------')


  global lastPictureTime
  lastPictureTime = 0


  if "polling-interval" in configuration:
      pollingInterval=configuration["polling-interval"]


  try:

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

       pollProjects()
       time.sleep(pollingInterval)


  except Exception as e:
    e = sys.exc_info()[0]
    helper.internalLogger.critical('Error: Exception unprocessed properly. Exiting')
    helper.einternalLogger.exception(e)  
    print('timelapse-General exeception captured. See log:{0}',format(cfg_log_exceptions))        
    loggingEnd()

'''----------------------------------------------------------'''
'''----------------     apirest_task      -------------------'''
def apirest_task():
  api.run(debug=True, use_reloader=False,port=5060,host='0.0.0.0')


'''----------------------------------------------------------'''
'''----------------       loggingEnd      -------------------'''
def loggingEnd():      
  helper.internalLogger.critical('timelapse-end -----------------------------')        
  print('timelapse-end -----------------------------')


'''----------------------------------------------------------'''
'''----------------     parse_args        -------------------'''
def parse_args():
    """Parse the args."""
    parser = argparse.ArgumentParser(
        description='Simple dht tracker')
    parser.add_argument('--configfile', type=str, required=False,
                        default='/etc/timelapse.conf',
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

