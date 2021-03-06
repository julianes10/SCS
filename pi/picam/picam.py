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
def getLiveStatus():
  rt={}

  rt["enable"]=False
  rt["active"]=False

  if not "live" in GLB_configuration: 
    return rt
  if not "enable" in GLB_configuration["live"]:
    return rt

  if not GLB_configuration["live"]["enable"]:
    return rt

  rt["enable"]=True

  helper.internalLogger.debug("Get live status...")
  try:
    result=subprocess.check_output(GLB_configuration["live"]["isActiveCmd"], shell=True)
    rt["active"]=True
  except subprocess.CalledProcessError as execution:
    helper.internalLogger.debug("Return code: {0}. Output {1}".format(execution.returncode, execution.output))
  helper.internalLogger.debug("Live is {0}".format(rt))
  return rt




'''----------------------------------------------------------'''
def setLiveStatusAtBoot():

  if not "live" in GLB_configuration: 
    return
  if not "enable" in GLB_configuration["live"]:
    return
  if GLB_configuration["live"]["enable"]:
    enableAtBoot=GLB_configuration["live"]["enable"]
    if "enableBoot" in GLB_configuration["live"]:
      enableAtBoot=GLB_configuration["live"]["enableBoot"]

  #By default deployment system will setup as enabled
  if enableAtBoot:  #Start and enable for the next
    helper.internalLogger.debug("Enabling live at boot...")
    try:
      subprocess.check_output(GLB_configuration["live"]["enableCmd"], shell=True)
    except subprocess.CalledProcessError as execution:
      helper.internalLogger.debug("Return code: {0}. Output {1}".format(execution.returncode, execution.output))

    try:
      subprocess.check_output(GLB_configuration["live"]["startCmd"], shell=True)
    except subprocess.CalledProcessError as execution:
      helper.internalLogger.debug("Return code: {0}. Output {1}".format(execution.returncode, execution.output))

  else: #Stop and disable for next boot
    helper.internalLogger.debug("Disabling live at boot...")
    try:
      subprocess.check_output(GLB_configuration["live"]["stopCmd"], shell=True)
    except subprocess.CalledProcessError as execution:
      helper.internalLogger.debug("Return code: {0}. Output {1}".format(execution.returncode, execution.output))

    try:
      subprocess.check_output(GLB_configuration["live"]["disableCmd"], shell=True)
    except subprocess.CalledProcessError as execution:
      helper.internalLogger.debug("Return code: {0}. Output {1}".format(execution.returncode, execution.output))




'''----------------------------------------------------------'''
'''----------------------------------------------------------'''

def format_datetime(value):
    aux="unknown"
    try:
      aux=time.ctime(value)
    except Exception as e:
      helper.internalLogger.critical("Error reading value date: {0}.".format(value))
      helper.einternalLogger.exception(e)
    return aux 

'''----------------------------------------------------------'''
'''----------------------------------------------------------'''
'''----------------------------------------------------------'''
class ServoTrackDirection:
  def __init__(self):
    self.reset()
        
  def reset(self):
    self.iniCurrent=0
    self.ini=0
    self.end=0
    self.speed=0
    self.duration=0

  def start(self,i,e,t):
    self.ini=i
    self.end=e
    self.iniCurrent=self.ini
    self.duration=t
    self.speed=(self.end-self.ini)/self.duration

  def startReverse(self):
    self.iniCurrent=self.end
    self.speed=(self.ini-self.end)/self.duration

  def restart(self):
    self.iniCurrent=self.ini
    self.speed=(self.end-self.ini)/self.duration

    
  def refresh(self,travelTime):
    return round(self.iniCurrent + (self.speed * travelTime))

  def toDict(self):
    rt={}
    rt['ini'] = self.ini
    rt['end'] = self.end
    rt['speed'] = self.speed
    rt['duration'] = self.duration
    rt['iniCurrent'] = self.iniCurrent
    return rt


'''----------------------------------------------------------'''
class ServoTrack:
  def __init__(self,cfg):
    self.initcfg=cfg
    self.pan=ServoTrackDirection()
    self.tilt=ServoTrackDirection()
    self.reset()

  def reset(self):
    self.trackDuration=0
    self.trackStartTime=0
    self.trackFinishedTime=0
    self.repeatTimes=0
    self.repeatCounter=0
    self.active=False
    self.reverse=False
    self.reverseDone=False
    self.pan.reset()
    self.tilt.reset()
    self.trackQueue=[] 



  def start(self,data):
    self.reset()
    for i in data:
      self.enqueue(i)
    if (len(data)): 
      self.active=True

  def enqueue(self,data):
    self.trackQueue.append(data)

  def startItem(self,data):
    helper.internalLogger.debug("starting an item to track: {0}".format(data))
    self.trackStartTime=time.time()
    self.pan.start(data["pan"]["ini"],data["pan"]["end"],data["duration"])
    self.tilt.start(data["tilt"]["ini"],data["tilt"]["end"],data["duration"])
    self.reverse=data["reverse"]
    self.reverseDone=False
    self.repeatTimes=data["ntimes"]
    self.repeatCounter=0
    self.trackDuration=data["duration"]
    self.trackFinishedTime=self.trackStartTime+self.trackDuration
    self.active=True


  def dequeue(self):
    rt=None
    if len(self.trackQueue):
      rt=self.trackQueue.pop(0)
      helper.internalLogger.debug("Poping out an item to track. Pending {0}".format(len(self.trackQueue)))
    return rt


  def isActive(self):
    return self.active

  def refresh(self):
    a=False
    p=0
    t=0
    now=time.time()
    if now <= self.trackFinishedTime and now >= self.trackStartTime:
       d=now - self.trackStartTime
       p=self.pan.refresh(d)
       t=self.tilt.refresh(d)
       a=True

    if self.active==True and a==False:
      helper.internalLogger.debug("Round done")
      # Check reverse and times:
      if (self.reverse and not self.reverseDone):
        helper.internalLogger.debug("Starting reverse...")
        self.reverseDone=True
        self.pan.startReverse()
        self.tilt.startReverse() 
     
        self.trackStartTime=time.time()
        self.trackFinishedTime=self.trackStartTime+self.trackDuration
        p=self.pan.refresh(0)
        t=self.tilt.refresh(0)

        a=True
      else:
        self.repeatCounter=self.repeatCounter+1 
        helper.internalLogger.debug("Round complete done {0}/{1}".format(self.repeatCounter,self.repeatTimes))
        if self.repeatCounter < self.repeatTimes:
          helper.internalLogger.debug("Starting new round...")
          self.reverseDone=False
          self.pan.restart()
          self.tilt.restart()
          self.trackStartTime=time.time()
          self.trackFinishedTime=self.trackStartTime+self.trackDuration
          p=self.pan.refresh(0)
          t=self.tilt.refresh(0)
          a=True
        else:
          helper.internalLogger.debug("Check if item enqueued to track...")
          item=self.dequeue()
          if item != None:
            self.startItem(item)
            p=self.pan.refresh(0)
            t=self.tilt.refresh(0)
            a=True
          else:
            helper.internalLogger.debug("Nothing to track.")

    self.active=a
    return a,p,t


  def toDict(self):
    rt={}
    rt['active']=self.active
    if self.active:
      rt['pan'] = self.pan.toDict()
      rt['tilt'] = self.tilt.toDict()
      rt['trackDuration'] = self.trackDuration
      rt['trackStartTime'] = self.trackStartTime
      rt['trackFinishedTime'] = self.trackFinishedTime
      rt['repeatTimes'] = self.repeatTimes
      rt['repeatCounter'] = self.repeatCounter
      rt['reverse'] = self.reverse
      rt['reverseDone'] = self.reverseDone
      rt['trackQueue'] = self.trackQueue

    return rt

'''----------------------------------------------------------'''
class ServoHandler:
  def __init__(self,cfg):
   try:
    self.pwm=None

    if amIaPi():
      self.setPan(0)
      self.setTilt(0)
    else:
      helper.internalLogger.debug("Not running in pi. Not init servo")
    self.autoTrack = ServoTrack(cfg)
    self.reset()
    if "enable" in cfg:
      if "initPan" in cfg:
        self.setPan(cfg["initPan"])
      if "initTilt" in cfg:
        self.setTilt(cfg["initTilt"])
      if "powerSavingTimeout" in cfg:
        self.powerSavingTimeout=cfg["powerSavingTimeout"]
   except Exception as e:
      helper.internalLogger.warning("Motor CAM is not in good shape...")
      helper.einternalLogger.exception(e)


  def end(self):
   try:
    self.stopDriver()
   except Exception as e:
      helper.internalLogger.warning("Motor CAM is not in good shape...")
      helper.einternalLogger.exception(e)



  def restartDriver(self):
   try:
    if amIaPi():
      import RPi.GPIO as GPIO
      from PCA9685 import PCA9685
      self.pwm = PCA9685()
      self.pwm.setPWMFreq(50)
    else:
      helper.internalLogger.debug("Not running in pi. Not init servo")
   except Exception as e:
      helper.internalLogger.warning("Motor CAM is not in good shape...")
      helper.einternalLogger.exception(e)


  def stopDriver(self):
   try:
    if amIaPi():
      helper.internalLogger.debug("Asking for Servo to end...")   
      if not self.pwm == None:
        self.pwm.exit_PCA9685()
      helper.internalLogger.debug("Servo is resting")   
    self.pwm=None
   except Exception as e:
      helper.internalLogger.warning("Motor CAM is not in good shape...")
      helper.einternalLogger.exception(e)
  
  def setDeltaPan(self,delta):
    helper.internalLogger.debug("setDeltaPan...{0}".format(delta))   
    aux=int(self.pan+int(delta))
    if (aux) > 180:
      aux=180
    if (aux) < 0:
      aux=0
    self.setPan(aux)

  def setDeltaTilt(self,delta):
    helper.internalLogger.debug("setDeltaTilt...{0}".format(delta))   
    aux=int(self.tilt+int(delta))
    if (aux) > 90:
      aux=90
    if (aux) < 0:
      aux=0
    self.setTilt(aux)


  def setPan(self,value):
   try:
    helper.internalLogger.debug("setPan...{0}".format(value))   
    self.pan = int(value)
    if amIaPi():
      if self.pwm is None:
        self.restartDriver()
      self.pwm.setRotationAngle(1,int(value))
      self.latestUsageTS=time.time()

   except Exception as e:
      helper.internalLogger.warning("Motor CAM is not in good shape...")
      helper.einternalLogger.exception(e)



  def setTilt(self,value):
   try:
    helper.internalLogger.debug("setTilt...{0}".format(value))   
    self.tilt = int(value)
    if amIaPi():
      if self.pwm is None:
        self.restartDriver()
      self.pwm.setRotationAngle(0,int(value))
      self.latestUsageTS=time.time()
   except Exception as e:
      helper.internalLogger.warning("Motor CAM is not in good shape...")
      helper.einternalLogger.exception(e)


  def startTrack(self,data):
    self.panBK=self.pan
    self.tiltBK=self.tilt
    self.backAfterAutoTrack=False
    if "backPosition" in data:
      self.backAfterAutoTrack=data["backPosition"]
    self.autoTrack.start(data["data"])

  def refreshTrack(self):
    if self.autoTrack.isActive():
      a,p,t = self.autoTrack.refresh()
      if (a):
        self.setPan(p)
        self.setTilt(t)
      else:
        if self.backAfterAutoTrack:
          self.setPan(self.panBK)
          self.setTilt(self.tiltBK)


  def reset(self):
    self.pan = 0
    self.tilt = 0
    self.panBK = 0
    self.tiltBK = 0
    self.autoTrack.reset()
    self.backAfterAutoTrack=False
    self.powerSavingTimeout = 0
    self.latestUsageTS = 0


  def refreshPowerSaving(self):
    if self.powerSavingTimeout == 0:
      return
    if self.latestUsageTS == 0:
      return
    now=time.time()
    #helper.internalLogger.debug("JODER {0} +  {1} = {2}, comparing with {3}".format(self.latestUsageTS, self.powerSavingTimeout,self.latestUsageTS + self.powerSavingTimeout,now))
    if (self.latestUsageTS + self.powerSavingTimeout) < now:
      helper.internalLogger.debug("Power savings timeout has expired")
      self.latestUsageTS=0
      self.stopDriver()
  


  def toDict(self):
    rt={}
    rt['pan'] = self.pan
    rt['tilt'] = self.tilt
    rt['panBK'] = self.panBK
    rt['tiltBK'] = self.tiltBK
    rt['autoTrack'] = self.autoTrack.toDict()
    rt['backAfterAutoTrack'] = self.backAfterAutoTrack
    rt['powerSavingTimeout'] = self.powerSavingTimeout
    rt['latestUsageTS'] = self.latestUsageTS


    return rt







'''----------------------------------------------------------'''
'''----------------------------------------------------------'''

def format_videoURL(value):
    aux="unknown"
    try:
      aux=value[1:]
    except Exception as e:
      helper.internalLogger.critical("Error reading value date: {0}.".format(value))
      helper.einternalLogger.exception(e)
    return aux
'''----------------------------------------------------------'''
'''----------------      API REST         -------------------'''
'''----------------------------------------------------------'''
api = Flask("api",template_folder="templates",static_folder='static_picam')
api.jinja_env.filters['datetime'] = format_datetime
api.jinja_env.filters['videoURL'] = format_videoURL
api.jinja_env.filters['tojson_pretty'] = to_pretty_json


'''----------------------------------------------------------'''
@api.route('/',methods=["GET"])
def home():
    return render_home_tab('Live')

'''----------------------------------------------------------'''
def render_home_tab(tab):
  display={}
  display["tab"]=tab
  st=getStatus()
  return render_template('index.html', title="Live picam",st=st,display=display)

'''----------------------------------------------------------'''
@api.route('/api/v1.0/picam/photo',methods=["POST","GET"])
def post_picam_photo():
  rt={}
  rt['result']='KO'  

  try:
    if request.json: 
      helper.internalLogger.debug("new photo required")
      helper.internalLogger.debug("Processing new request:...{0}".format(request.json))
      data = request.get_json()
    else:
      rt['result']='OK'  
      data={}   
  
    rt,f=requestPhoto(data)
 
    ''' TODO if f==None:
      rtjson=json.dumps(rt)
      return rtjson
    else:
      pass
      #TODO return imagen
    '''


  except Exception as e:
    e = sys.exc_info()[0]
    helper.internalLogger.error('Error: position json')
    helper.einternalLogger.exception(e)  
    rtjson=jsonify({'result': 'KO'})
    helper.internalLogger.debug("status failed")

  return json.dumps(rt)


'''----------------------------------------------------------'''
@api.route('/api/v1.0/picam/position',methods=["POST","GET"])
def post_picam_position():
  rt = {}

  try:
    if request.json: 
      helper.internalLogger.debug("new positon required")
      helper.internalLogger.debug("Processing new request:...{0}".format(request.json))
      data = request.get_json()
    else:
      rt['result']='OK'  
      data={}   
  
    rt['data']=requestNewPosition(data)
 
    rtjson=json.dumps(rt)

  except Exception as e:
    e = sys.exc_info()[0]
    helper.internalLogger.error('Error: position json')
    helper.einternalLogger.exception(e)  
    rtjson=jsonify({'result': 'KO'})
    helper.internalLogger.debug("status failed")
  return rtjson


'''----------------------------------------------------------'''
@api.route('/api/v1.0/picam/track',methods=["POST"])
def post_picam_track():
  rt = {}
  try:

      helper.internalLogger.debug("new track required")
      helper.internalLogger.debug("Processing new track request:...{0}".format(request.json))
      data = request.get_json()
      rt['result']='OK'     
  
      rt['data']=requestNewTrack(data)
 
      rtjson=json.dumps(rt)

  except Exception as e:
    e = sys.exc_info()[0]
    helper.internalLogger.error('Error: track json')
    helper.einternalLogger.exception(e)  
    rtjson=jsonify({'result': 'KO'})
    helper.internalLogger.debug("status failed")
  return rtjson


'''----------------------------------------------------------'''
def requestNewTrack(data):
      global GLB_servo
     
      GLB_servo.startTrack(data)

      return GLB_servo.toDict()


'''----------------------------------------------------------'''
def requestNewPosition(data):
      global GLB_servo
      if "pan" in data:
        if "delta" in data["pan"]:
          GLB_servo.setDeltaPan(data["pan"]["delta"])
        if "abs" in data["pan"]:
          GLB_servo.setPan(data["pan"]["abs"])

      if "tilt" in data:
        if "delta" in data["tilt"]:
          GLB_servo.setDeltaTilt(data["tilt"]["delta"])
        if "abs" in data["tilt"]:
          GLB_servo.setTilt(data["tilt"]["abs"])

      return GLB_servo.toDict()

'''----------------------------------------------------------'''
def requestPhoto(data):
  global GLB_servo
  rt={}
  rt["result"]="KO"
  rt2=""
  # Set position if required and pantilt is enabled
  backPosition=False
  panBK=0
  tiltBK=0
  if "servo" in GLB_configuration:
    if "enable" in GLB_configuration["servo"]:
      if GLB_configuration["servo"]["enable"]:     
        if "position" in data:
          if "backPosition" in data["position"]:  
            if data["position"]["backPosition"]:  
              panBK=GLB_servo.pan
              tiltBK=GLB_servo.tilt   
              backPosition=True    
              rt["backPositionData"]={"pan":panBK,"tilt":tiltBK}
            rt["backPosition"]=backPosition
        if "position" in data:
          rttpos=requestNewPosition(data["position"])  
        rt["positionData"]={"pan":GLB_servo.pan,"tilt":GLB_servo.tilt}         

  # Get custom camara setup if required, else use defaults
  cmd="UNKNOWN"
  additionalFlags=""
  outputFile="/tmp/photo"
  if "photo" in GLB_configuration:
    if "defaultCmd" in GLB_configuration["photo"]:
      cmd=GLB_configuration["photo"]["defaultCmd"]
    if "cmd" in data:
      cmd=data["cmd"]
    else:
      if "defaultFlags" in GLB_configuration["photo"]:
        flags=GLB_configuration["photo"]["defaultFlags"]
      if "defaultFileOutput" in GLB_configuration["photo"]:
        outputFile=GLB_configuration["photo"]["defaultFileOutput"]
      if "customFlags" in data:
        flags=data["customFlags"]
      if "customOutputFile" in data:
        outputFile=data["customOutputFile"]
      cmd=cmd.replace("PARAMETER_FLAGS",flags)
      cmd=cmd.replace("PARAMETER_FILEOUTPUT",outputFile)
      rt2=outputFile
      rt["cmd"]=cmd
      rt["outputFile"]=outputFile
     
  # shoot!
  try:
    helper.internalLogger.debug("Shooting: {0}".format(cmd))
    subprocess.check_output(cmd, shell=True)
    rt["result"]="OK"
  except subprocess.CalledProcessError as execution:
    helper.internalLogger.debug("Return code: {0}. Output {1}".format(execution.returncode, execution.output))


  # Back to position if required
  if backPosition:
    GLB_servo.setTilt(tiltBK)
    GLB_servo.setPan(panBK)

  # Return when image is ready with json ok or with image itself if not filenema is requested
  return rt,rt2 

'''----------------------------------------------------------'''
def requestRelease(data):
      global GLB_servo

      if "release" in data:  #saving power
        if data["release"]:
          GLB_servo.end()
        else:
          GLB_servo.setDeltaTilt(0)
          GLB_servo.setDeltaTilt(0)    

      return GLB_servo.toDict()

'''----------------------------------------------------------'''
@api.route('/api/v1.0/picam/release',methods=["POST"])
def post_picam_release():
  rt = {}
  try:

      helper.internalLogger.debug("Release setting request")
      helper.internalLogger.debug("Processing new request:{0}...".format(request.json))
      rt['result']='OK'     
      data = request.get_json()
      rt['data']=requestRelease(data)

      rtjson=json.dumps(rt)

  except Exception as e:
    e = sys.exc_info()[0]
    helper.internalLogger.error('Error: in release json')
    helper.einternalLogger.exception(e)  
    rtjson=jsonify({'result': 'KO'})
    helper.internalLogger.debug("status failed")
  return rtjson
'''----------------------------------------------------------'''
@api.route('/api/v1.0/picam/live',methods=["POST"])
def post_picam_live():
  rt = {}
  try:

      helper.internalLogger.debug("Live setting request")
      helper.internalLogger.debug("Processing new request:{0}...".format(request.json))
      rt['result']='OK'     
      data = request.get_json()
      rt['data']=requestLive(data)

      rtjson=json.dumps(rt)

  except Exception as e:
    e = sys.exc_info()[0]
    helper.internalLogger.error('Error: in live json')
    helper.einternalLogger.exception(e)  
    rtjson=jsonify({'result': 'KO'})
    helper.internalLogger.debug("status failed")
  return rtjson


'''----------------------------------------------------------'''
def requestLive(data):     
      rt={}
      rt["live"]=False
      helper.internalLogger.debug("requestLive...")
      if "live" in data:
        helper.internalLogger.debug("requestLive live in data...")
        if data["live"]:
          helper.internalLogger.debug("Starting live video streamer...")
          result=subprocess.check_output(['bash','-c',GLB_configuration["live"]["startCmd"]])
          rt["live"]=True
        else:
          helper.internalLogger.debug("Stopping live video streamer...")
          result=subprocess.check_output(['bash','-c',GLB_configuration["live"]["stopCmd"]])
          rt["live"]=False

      return rt

'''----------------------------------------------------------'''
@api.route('/api/v1.0/picam/status', methods=['GET'])
def get_picam_status():
  helper.internalLogger.debug("status required")
  rtjson=json.dumps(getStatus())
  return rtjson


def getStatus():
  global GLB_servo

  helper.internalLogger.debug("status required")
  rt = {}
  rt['vsw']={}
  rt['vsw']['picam']=getVersion()
  try:
      rt['result']='OK'       
      rt['status']={}
      rt['status']['live']=getLiveStatus()
      rt['status']['servo']=GLB_servo.toDict()
      helper.internalLogger.debug("status {0}".format(rt))

  except Exception as e:
    e = sys.exc_info()[0]
    helper.internalLogger.error('Error: gathering status')
    helper.einternalLogger.exception(e)  
    rt['result']='KO'
    helper.internalLogger.debug("status failed")

  return rt

'''----------------------------------------------------------'''
'''----------------       M A I N         -------------------'''
'''----------------------------------------------------------'''

def main(configfile):
  print('picam-start -----------------------------')

  # Loading config file,
  # Default values
  cfg_log_traces="picam.log"
  cfg_log_exceptions="picame.log"


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
  helper.internalLogger.critical('picam-start -------------------------------')  
  helper.einternalLogger.critical('picam-start -------------------------------')

  signal.signal(signal.SIGINT, signal_handler)
  signal.signal(signal.SIGTERM, signal_handler)

  try:
    apiRestTask=threading.Thread(target=apirest_task,name="restapi")
    apiRestTask.daemon = True
    apiRestTask.start()
  
    global GLB_servo
    if not "servo" in GLB_configuration:    
      GLB_servo=ServoHandler({})
    else:
      GLB_servo=ServoHandler(GLB_configuration["servo"])

    setLiveStatusAtBoot()

  except Exception as e:
    helper.internalLogger.critical("Error processing GLB_configuration json {0} file. Exiting".format(configfile))
    helper.einternalLogger.exception(e)
    if not GLB_servo is None:
        GLB_servo.end()
    loggingEnd()
    return  

  try:    

     while True:
       #helper.internalLogger.critical("Polling, nothing to poll yet")
       time.sleep(0.05)
       GLB_servo.refreshTrack()
       GLB_servo.refreshPowerSaving()
  
     if not GLB_servo is None:
       GLB_servo.end()

  except Exception as e:
    e = sys.exc_info()[0]
    helper.internalLogger.critical('Error: Exception unprocessed properly. Exiting')
    helper.einternalLogger.exception(e)  
    print('picam-General exeception captured. See log:{0}',format(cfg_log_exceptions))        
    if not GLB_servo is None:
        GLB_servo.end()
    loggingEnd()

'''----------------------------------------------------------'''
'''----------------------------------------------------------'''
def signal_handler(sig, frame):
    print('SIGNAL CAPTURED')        
    if not GLB_servo is None:
        GLB_servo.end()
    loggingEnd()
    sys.exit(0)



'''----------------------------------------------------------'''
'''----------------     apirest_task      -------------------'''
def apirest_task():

  api.run(debug=True, use_reloader=False,port=GLB_configuration["port"],host=GLB_configuration["host"])


'''----------------------------------------------------------'''
'''----------------       loggingEnd      -------------------'''
def loggingEnd():      
  helper.internalLogger.critical('picam-end -----------------------------')        
  print('picam-end -----------------------------')


'''----------------------------------------------------------'''
'''----------------     parse_args        -------------------'''
def parse_args():
    """Parse the args."""
    parser = argparse.ArgumentParser(
        description='picam service')
    parser.add_argument('--configfile', type=str, required=False,
                        default='/etc/picam.conf',
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

