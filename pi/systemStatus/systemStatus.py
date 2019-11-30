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



''' -------------------------------------------------'''
class NetworkMonitor:
  def __init__(self):
    self.status=0  
    self.connected=False
    self.lastTimeConnected=0
    self.ipWlan="unknown"
    self.ipv6Wlan="unknown"
    self.ipWan="unknown"
    self.ipv6Wan="unknown"
    self.defaultInterfaceRoute="unknown"
    self.wlans=[]
    self.totalConnectedSuccess=0
    self.totalConnectedFails=0
    self.consecutiveFailures=0
    self.nextTime=time.time()
    cmd="cat /etc/wpa_supplicant/wpa_supplicant.conf  | grep -C3 ssid | grep 'ssid\|prio'"
    self.preferredESSIDs=getOutputCommand(cmd,"unknown")
    self.wlanOn=False
    self.wanOn=False


  #--------------------------------------------
  def update(self):
    if not "netMonitor" in GLB_configuration:
      return
    now=time.time()
    if self.nextTime > now:
      return
    self.nextTime=now+GLB_configuration["netMonitor"]["interval"]
    self.getConnectivity()
    self.getAvailableWlans()
    self.getActiveInterfacesIp()
    self.updateDefaultRoute()

    if self.connected==True:
      self.totalConnectedSuccess=self.totalConnectedSuccess+1
      self.consecutiveFailures=0
    else:
      self.totalConnectedFails=self.totalConnectedFails+1
      self.consecutiveFailures=self.consecutiveFailures+1
      helper.internalLogger.warning("No connectiviy, consecutive fail: {0}".format(self.consecutiveFailures))
    
    try:

      if self.consecutiveFailures >=  GLB_configuration["netMonitor"]["retryTimes"]:
        helper.internalLogger.warning("No connectiviy, to much. Executing failureCmd...")
        getResultCommand(GLB_configuration["netMonitor"]["failureCmd"])
        self.consecutiveFailures=0
    except Exception as e:
      e = sys.exc_info()[0]
      helper.internalLogger.error('Error executing failureCmd when no connection')
      helper.einternalLogger.exception(e) 


  #--------------------------------------------
  def getConnectivity(self):
    # Check regular connectivity
    host2monitor="www.google.com"
    if "host2Monitor" in GLB_configuration:
      host2monitor=GLB_configuration["netMonitor"]["host2Monitor"]

    cmd="ping -c1 " + host2monitor + " > /dev/null"
    self.connected=getResultCommand(cmd)

    # Check wlan connected SSID
    if not "wlanInterface" in GLB_configuration["netMonitor"]:
      self.connectedWlan="unknown"
      return
    cmd="iwconfig " + GLB_configuration["netMonitor"]["wlanInterface"] + " | grep -i SSID  | cut -d \":\" -f2 | sed 's/\"//g' | awk '{$1=$1};1'"
    self.connectedWlan=getOutputCommand(cmd,"unknown")

  #--------------------------------------------
  def getAvailableWlans(self):
    helper.internalLogger.debug("Getting available wlan..")
    self.wlans=[]
    if not "wlanInterface" in GLB_configuration["netMonitor"]:
      return
    cmd="iwlist " + GLB_configuration["netMonitor"]["wlanInterface"] + " scanning | grep -i SSID | cut -d ':' -f2 | sed 's/\"//g'"
    aux=getOutputCommand(cmd," ")
    self.wlans=aux.split()

  #--------------------------------------------
  def getDefaultRoute(self):
    cmd="ip r | grep default | sed -n -e 's/^.*dev //p' | cut -d ' ' -f1"
    helper.internalLogger.debug("Getting default route...")
    self.defaultInterfaceRoute=getOutputCommand(cmd,"unknown")

  #--------------------------------------------
  def getActiveInterfacesIp(self):
    if "wanInterface" in GLB_configuration["netMonitor"]:
      self.ipWan   =self.getIp("inet ",GLB_configuration["netMonitor"]["wanInterface"])
      self.ipv6Wan =self.getIp("inet6 ",GLB_configuration["netMonitor"]["wanInterface"]) 
    if "wlanInterface" in GLB_configuration["netMonitor"]:
      self.ipWlan     =self.getIp("inet ",GLB_configuration["netMonitor"]["wlanInterface"])
      self.ipv6Wlan   =self.getIp("inet6 ",GLB_configuration["netMonitor"]["wlanInterface"])
    self.wlanOn = (self.ipWlan != None and self.ipWlan != "unknown" and self.ipWlan!= "") or (self.ipv6Wlan != None and self.ipv6Wlan != "unknown" and self.ipv6Wlan!= "")
    self.wanOn = (self.ipWan != None and self.ipWan != "unknown" and self.ipWan!= "") or (self.ipv6Wan != None and self.ipv6Wan != "unknown" and self.ipv6Wan!= "")
 



  #--------------------------------------------
  def getIp(self,ipv,iface):
    cmd="ifconfig "+iface+" | grep '"+ipv+"' | awk '{print$2}'"
    return getOutputCommand(cmd,"unknown")

  #--------------------------------------------
  def updateDefaultRoute(self):
    self.getDefaultRoute()
    if not "favoriteDefaultRoute" in GLB_configuration["netMonitor"]:
      return
    if GLB_configuration["netMonitor"]["favoriteDefaultRoute"] == self.defaultInterfaceRoute:
      return
      
    iface2useInRoute=""
    if GLB_configuration["netMonitor"]["favoriteDefaultRoute"] == GLB_configuration["netMonitor"]["wlanInterface"]: 
      if self.wlanOn:
          iface2useInRoute=GLB_configuration["netMonitor"]["wlanInterface"]
          helper.internalLogger.debug("Route prefered wlan and it is on")
      else:
        if self.wanOn:
          iface2useInRoute=GLB_configuration["netMonitor"]["wanInterface"]
          helper.internalLogger.debug("Route prefered wlan but it is not on and wan yes")
        else:
          return

    if GLB_configuration["netMonitor"]["favoriteDefaultRoute"] == GLB_configuration["netMonitor"]["wanInterface"]: 
      if self.wanOn:
          iface2useInRoute=GLB_configuration["netMonitor"]["wanInterface"]
          helper.internalLogger.debug("Route prefered wan and it is on")
      else:
        if self.wlanOn:
          iface2useInRoute=GLB_configuration["netMonitor"]["wlanInterface"]
          helper.internalLogger.debug("Route prefered wan but it is not on and wlan yes")
        else:
          return    
    if (iface2useInRoute ==""):
      return
    if iface2useInRoute == self.defaultInterfaceRoute:
      helper.internalLogger.debug("Route prefered is already the default one.")
      return

    helper.internalLogger.debug("Lets try to add NEW default route...")
    # delete current default route
    cmd="ip r del default"
    getResultCommand(cmd)

    # add new default route
    cmd="ip r add default dev " + iface2useInRoute
    if getResultCommand(cmd):
      self.defaultInterfaceRoute=iface2useInRoute

  def toDict(self):
    rt={}
    rt['totalConnectedSuccess'] = self.totalConnectedSuccess
    rt['totalConnectedFails'] = self.totalConnectedFails
    rt['consecutiveFailures'] = self.consecutiveFailures
    rt['connected'] = self.connected
    rt['ipWlan'] = self.ipWlan
    rt['ipWan'] = self.ipWan
    rt['ipv6Wlan'] = self.ipv6Wlan
    rt['ipv6Wan'] = self.ipv6Wan

    rt['defaultInterfaceRoute'] = self.defaultInterfaceRoute
    rt['wlans'] = self.wlans
    rt['connectedWlan']=self.connectedWlan
    rt['preferredESSIDs']=self.preferredESSIDs

    if "netMonitor" in GLB_configuration:
      rt['configuration']=GLB_configuration["netMonitor"]

    rt['wlanOn']=self.wlanOn
    rt['wanOn']=self.wanOn

    return rt

'''----------------------------------------------------------'''
'''----------------      API REST         -------------------'''
'''----------------------------------------------------------'''
api = Flask("api",template_folder="templates",static_folder='static_systemStatus')

'''----------------------------------------------------------'''
@api.route('/',methods=["GET"])
def home():
    return render_home_tab('services')

'''----------------------------------------------------------'''
@api.route('/netMonitor',methods=["GET"])
def gui_home_netMonitor():
    return render_home_tab('netMonitor')

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
  rt["netMonitor"]=GLB_netMonitor.toDict()

  return rt

'''----------------------------------------------------------'''
def getOuputCmd(cmd):     
  rt={}
  rt["dump"]=getOutputCommand(cmd,"ERROR executing "+cmd)
  return rt


'''----------------------------------------------------------'''
def getServiceStatus(flag,service):     
  rt=False
  helper.internalLogger.debug("Get service status {0}...".format(service))
  cmd="systemctl " + flag + " " + service
  rt=getResultCommand(cmd)
  helper.internalLogger.debug("Service {0} status {1} is : {2}".format(service,flag,rt))
  return rt

'''----------------------------------------------------------'''
def getServiceShow(flag,service):     
  helper.internalLogger.debug("Get service show {0}...".format(service))
  cmd="systemctl show " + service + " -p" + flag + " | cut -d '=' -f2"
  rt=getOutputCommand(cmd,"unknown")
  if rt == "": 
    rt="unknown"
  helper.internalLogger.debug("Service {0}  show  {1} is : {2}".format(service,flag,rt))
  return rt

'''----------------------------------------------------------'''
def getServiceRestarts(service):     
  rt="unknown"
  helper.internalLogger.debug("Get restarts {0}...".format(service))
  cmd="journalctl -u "+ service + " | grep systemd | grep -i started | wc -l"
  ## WEAK WOW
  ## ALTERNATIVE -p NRestart not working
  rt=getOutputCommand(cmd,"unknown")
  helper.internalLogger.debug("Service {0} restarts {1}".format(service,rt))
  return rt


'''----------------------------------------------------------'''
def getServiceRestartsToday(service):     
  rt="unknown"
  helper.internalLogger.debug("Get restarts {0}...".format(service))
  cmd="journalctl -u "+ service + " | grep systemd | grep -i started | grep \"$(date +\" %d \")\" | wc -l"
  ## WEAK WOW
  ## ALTERNATIVE -p NRestart not working
  rt=getOutputCommand(cmd,"unknown")
  helper.internalLogger.debug("Service {0} restarts {1}".format(service,rt))
  helper.internalLogger.debug("Service {0} restarts {1}".format(service,rt))
  return rt

'''----------------------------------------------------------'''
def getServices():     
  rt={}

  for i in GLB_configuration["services"]:
    rt[i]={}
    rt[i]["active"]=getServiceStatus("is-active",i)
    rt[i]["enabled"]=getServiceStatus("is-enabled",i)
    # rt[i]["failed"]=getServiceStatus("is-failed",i)
    rt[i]["startTime"]=getServiceShow("ExecMainStartTimestamp",i)
    rt[i]["restarts"]=getServiceRestarts(i)
    rt[i]["restartsToday"]=getServiceRestartsToday(i)

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
@api.route('/api/v1.0/systemStatus/netMonitor', methods=['GET'])
def get_systemStatus_netMonitor():
  helper.internalLogger.debug("network monitor required")
  rtjson=json.dumps(GLB_netMonitor.toDict())
  return rtjson




'''----------------------------------------------------------'''
'''----------------       polling         -------------------'''
'''----------------------------------------------------------'''

def polling(): 
  GLB_netMonitor.update()



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
     pollingInterval=5
     if "polling-interval" in GLB_configuration:
       pollingInterval=GLB_configuration["polling-interval"]

     global GLB_netMonitor
     GLB_netMonitor=NetworkMonitor()

     while True:
       polling()
       time.sleep(pollingInterval)
  

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

