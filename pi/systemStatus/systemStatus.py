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
import shutil
from flask import Flask, render_template,redirect



def getVersion():
   rt={}
   try:
     if "vsw-file" in GLB_configuration:
       with open(GLB_configuration["vsw-file"]) as json_data:
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
api = Flask("api",template_folder="templates",static_folder='static_systemStatus')

'''----------------------------------------------------------'''
@api.route('/',methods=["GET"])
def home():
    return render_home_tab('services')

'''----------------------------------------------------------'''
def render_home_tab(tab):
  display={}
  display["tab"]=tab
  st=getStatus()
  return render_template('index.html', title="System Status",st=st,display=display)


'''----------------------------------------------------------'''
def getStatus():     
  helper.internalLogger.debug("getStatus...")
  rt={}
  rt["cpu"]=getOuputCmd(GLB_configuration["plugin"]["cpu"])
  rt["mem"]=getOuputCmd(GLB_configuration["plugin"]["mem"])
  rt["disk"]=getOuputCmd(GLB_configuration["plugin"]["disk"])
  rt["network"]=getOuputCmd(GLB_configuration["plugin"]["network"])
  rt["services"]=getServices()
  return rt

'''----------------------------------------------------------'''
def getOuputCmd(cmd):     
  rt={}
  try:
    result=subprocess.check_output(cmd, shell=True)
    rt["dump"]=result.decode()
  except subprocess.CalledProcessError as execution:
    helper.internalLogger.debug("Return code: {0}. Output {1}".format(execution.returncode, execution.output))
    rt["dump"]="ERROR: " +str(execution.returncode) + execution.output.decode()
  helper.internalLogger.debug("DUMP {0}".format(rt))
  return rt


'''----------------------------------------------------------'''
def getServiceStatus(flag,service):     
  rt=False
  helper.internalLogger.debug("Get active {0}...".format(service))
  cmd="systemctl " + flag + " " + service
  try:
    result=subprocess.check_output(cmd, shell=True)
    rt=True
  except subprocess.CalledProcessError as execution:
    helper.internalLogger.debug("Return code: {0}. Output {1}".format(execution.returncode, execution.output))
  helper.internalLogger.debug("Service {0} status {1} is : {2}".format(service,flag,rt))
  return rt

'''----------------------------------------------------------'''
def getServiceShow(flag,service):     
  rt="unknown"
  helper.internalLogger.debug("Get active {0}...".format(service))
  cmd="systemctl show " + service + " -p" + flag + " | cut -d '=' -f2"
  try:
    result=subprocess.check_output(cmd, shell=True)
    rt=result.decode().rstrip()
    if rt =='':
      rt="unknown"
  except subprocess.CalledProcessError as execution:
    helper.internalLogger.debug("Return code: {0}. Output {1}".format(execution.returncode, execution.output))
  helper.internalLogger.debug("Service {0}  show  {1} is : {2}".format(service,flag,rt))
  return rt

'''----------------------------------------------------------'''
def getServiceRestarts(service):     
  rt="unknown"
  helper.internalLogger.debug("Get active {0}...".format(service))
  cmd="journalctl -u "+ service + " | grep Starting | wc -l"
  try:
    result=subprocess.check_output(cmd, shell=True)
    rt=result.decode().rstrip()
  except subprocess.CalledProcessError as execution:
    helper.internalLogger.debug("Return code: {0}. Output {1}".format(execution.returncode, execution.output))
  helper.internalLogger.debug("Service {0} restarts {1}".format(service,rt))
  return rt

'''----------------------------------------------------------'''
def getServices():     
  rt={}

  for i in GLB_configuration["services"]:
    rt[i]={}
    rt[i]["active"]=getServiceStatus("is-active",i)
    rt[i]["enable"]=getServiceStatus("is-enable",i)
    rt[i]["failed"]=getServiceStatus("is-failed",i)
    rt[i]["startTime"]=getServiceShow("ExecMainStartTimestamp",i)
    rt[i]["restarts"]=getServiceRestarts(i)

  helper.internalLogger.debug("Services: {0} ".format(rt))
  return rt

'''----------------------------------------------------------'''
@api.route('/api/v1.0/systemStatus/status', methods=['GET'])
def get_systemStatus_status():
  helper.internalLogger.debug("status required")
  rtjson=json.dumps(getStatus())
  return rtjson

'''----------------------------------------------------------'''
@api.route('/api/v1.0/systemStatus/cpu', methods=['GET'])
def get_systemStatus_cpu():
  helper.internalLogger.debug("cpu required")
  rtjson=json.dumps(getOuputCmd(GLB_configuration["plugin"]["cpu"]))
  return rtjson

'''----------------------------------------------------------'''
@api.route('/api/v1.0/systemStatus/mem', methods=['GET'])
def get_systemStatus_mem():
  helper.internalLogger.debug("mem required")
  rtjson=json.dumps(getOuputCmd(GLB_configuration["plugin"]["mem"]))
  return rtjson

'''----------------------------------------------------------'''
@api.route('/api/v1.0/systemStatus/services', methods=['GET'])
def get_systemStatus_services():
  helper.internalLogger.debug("services required")
  rtjson=json.dumps(getServices())
  return rtjson

'''----------------------------------------------------------'''
@api.route('/api/v1.0/systemStatus/disk', methods=['GET'])
def get_systemStatus_disk():
  helper.internalLogger.debug("disk required")
  rtjson=json.dumps(getOuputCmd(GLB_configuration["plugin"]["disk"]))
  return rtjson

'''----------------------------------------------------------'''
@api.route('/api/v1.0/systemStatus/network', methods=['GET'])
def get_systemStatus_network():
  helper.internalLogger.debug("network required")
  rtjson=json.dumps(getOuputCmd(GLB_configuration["plugin"]["network"]))
  return rtjson

'''----------------------------------------------------------'''
'''----------------       M A I N         -------------------'''
'''----------------------------------------------------------'''

def main(configfile):
  print('systemStatus-start -----------------------------')

  # Loading config file,
  # Default values
  cfg_log_traces="systemStatus.log"
  cfg_log_exceptions="systemStatuse.log"


  global GLB_configuration


  # Let's fetch data
  GLB_configuration={}
  with open(configfile) as json_data:
      GLB_configuration = json.load(json_data)
  #Get log names
  if "log" in GLB_configuration:
      if "logTraces" in GLB_configuration["log"]:
        cfg_log_traces = GLB_configuration["log"]["logTraces"]
      if "logExceptions" in GLB_configuration["log"]:
        cfg_log_exceptions = GLB_configuration["log"]["logExceptions"]
  helper.init(cfg_log_traces,cfg_log_exceptions)
  print('See logs traces in: {0} and exeptions in: {1}-----------'.format(cfg_log_traces,cfg_log_exceptions))  
  helper.internalLogger.critical('systemStatus-start -------------------------------')  
  helper.einternalLogger.critical('systemStatus-start -------------------------------')

  signal.signal(signal.SIGINT, signal_handler)

  try:
    apiRestTask=threading.Thread(target=apirest_task,name="restapi")
    apiRestTask.daemon = True
    apiRestTask.start()
  
  except Exception as e:
    helper.internalLogger.critical("Error processing GLB_configuration json {0} file. Exiting".format(configfile))
    helper.einternalLogger.exception(e)
    loggingEnd()
    return  

  try:    

     while True:
       #helper.internalLogger.critical("Polling, nothing to poll yet")
       time.sleep(1)
  

  except Exception as e:
    e = sys.exc_info()[0]
    helper.internalLogger.critical('Error: Exception unprocessed properly. Exiting')
    helper.einternalLogger.exception(e)  
    print('systemStatus-General exeception captured. See log:{0}',format(cfg_log_exceptions))        
    loggingEnd()

'''----------------------------------------------------------'''
'''----------------------------------------------------------'''
def signal_handler(sig, frame):
    print('SIGNAL CAPTURED')        
    loggingEnd()
    sys.exit(0)



'''----------------------------------------------------------'''
'''----------------     apirest_task      -------------------'''
def apirest_task():

  api.run(debug=True, use_reloader=False,port=GLB_configuration["port"],host=GLB_configuration["host"])


'''----------------------------------------------------------'''
'''----------------       loggingEnd      -------------------'''
def loggingEnd():      
  helper.internalLogger.critical('systemStatus-end -----------------------------')        
  print('systemStatus-end -----------------------------')


'''----------------------------------------------------------'''
'''----------------     parse_args        -------------------'''
def parse_args():
    """Parse the args."""
    parser = argparse.ArgumentParser(
        description='systemStatus service')
    parser.add_argument('--configfile', type=str, required=False,
                        default='/etc/systemStatus.conf',
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

