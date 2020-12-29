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


GLB_latestChannelOn=""

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


#Code copy and adapted from https://github.com/adafruit/Adafruit_Python_DHT/blob/master/examples/simpletest.py


from flask import Flask, render_template,redirect
from flask import Flask, jsonify,abort,make_response,request, url_for

from helper import *

class TrackerStats:
  def __init__(self):
    self.reset()
  def reset(self):
    self.playOn=True
    self.numFails = 0
    self.numSuccess = 0
    self.timeFailing = 0
    self.timeSucceeding = 0
    self.latestUpdate = 0
    self.latestCPU = 0
    self.latestBW = 0
    self.consecutiveFails=0
    self.lastRxBytes=0
    self.lastRxBytesTS=0
    self.OnMeanBW=0
    self.OnMedianBW=0
    self.OnStdDev=0
    self.dataBW=[]
  def toDict(self):
    rt={}
    try:
      rt['numFails'] = self.numFails
      rt['numSuccess'] = self.numSuccess
      rt['timeFailing'] = round(self.timeFailing,2)
      rt['timeSucceeding'] = round(self.timeSucceeding,2)
      rt['consecutiveFails'] = self.consecutiveFails
      rt['latestCPU'] = round(self.latestCPU,2)
      rt['latestBW'] = round(self.latestBW,2)
      rt['OnMeanBW'] = round(self.OnMeanBW,2)
      rt['OnMedianBW'] = round(self.OnMedianBW,2)
      rt['OnStdDev'] = round(self.OnStdDev,2)
    except Exception as e:
        e = sys.exc_info()[0]
        helper.internalLogger.error('Some exception returning traker stats')
        helper.einternalLogger.exception(e)  

    return rt

  def updateBW(self):
    self.numSuccess = self.numSuccess+1
    self.updateTimings(True)

  def success(self):
    self.numSuccess = self.numSuccess+1
    self.updateTimings(True)

  def fail(self):
    self.numFails = self.numFails+1
    self.updateTimings(False)

  def updateKPIs(self):
    self.latestCPU=getKPI(GLB_configuration["kpi"]["cpu"]["cmd"])
    lastRxBytesNew=getKPI(GLB_configuration["kpi"]["bwKbps"]["cmd"])
    now=time.time()
    if self.lastRxBytes==0:
      self.latestBW = 0
    elif lastRxBytesNew<self.lastRxBytes:
      self.latestBW = 0
    else:
      self.latestBW = round((lastRxBytesNew-self.lastRxBytes)*8/((now-self.lastRxBytesTS))/1000)
    helper.internalLogger.debug('bytes {0}, bytesnew {1}, interval {2}. BW= {3}kbps'.format(self.lastRxBytes,lastRxBytesNew,now-self.lastRxBytesTS,self.latestBW))
    self.lastRxBytes=lastRxBytesNew
    self.lastRxBytesTS=now

    

  def updateTimings(self,on):
   try:
    if self.latestUpdate == 0:  #first time only
      self.latestUpdate=time.time()

    if on:
      self.consecutiveFails=0
    else:
      self.consecutiveFails=self.consecutiveFails+1;
  
    if self.playOn and on:
      self.timeSucceeding = self.timeSucceeding + (time.time() - self.latestUpdate)
    else:
      self.timeFailing = self.timeFailing + (time.time() - self.latestUpdate)
    self.playOn=on
    self.latestUpdate=time.time()

    if on:
      import statistics
      self.dataBW.append(self.latestBW)
      self.OnMeanBW=statistics.mean(self.dataBW)
      self.OnMedianBW=statistics.median(self.dataBW)
      self.OnStdDev=statistics.stdev(self.dataBW)

   except Exception as e:
        e = sys.exc_info()[0]
        helper.internalLogger.error('Some exception calculating kpi')
        helper.einternalLogger.exception(e)  



def listFiles2Array(basedir,extension):
  import os
  ext = "." + extension 
  target_files = []
  # Select only files with the ext extension
  target_files = [i for i in os.listdir(basedir) if os.path.splitext(i)[1] == ext]
  return target_files

def generatePhotoThumbnails(bdir,fileList,oDir):
  from PIL import Image
  try:
    for x in fileList:     
      helper.internalLogger.debug("Generating photo thumbnails of {0}".format(x))
      ofile=oDir+"/"+os.path.basename(x)
      if not os.path.isfile(ofile):    
        im=Image.open(bdir+"/"+x)
        im.thumbnail((120,120))
        im.save(ofile)
         
  except Exception as e:
    e = sys.exc_info()[0]
    helper.internalLogger.error('exception generating thumbnail photo')
    helper.einternalLogger.exception(e)  

def generateVideoThumbnails(bdir,fileList,oDir):

  try:
    for x in fileList:     
      helper.internalLogger.debug("Generating video thumbnails of {0}".format(x))
      ofile=oDir+"/"+os.path.basename(x)
      if not os.path.isfile(ofile):    
        cmd="ffmpegthumbnailer -i " +bdir+"/"+x +" -o " + ofile
        subprocess.run(['bash','-c',cmd])
         
  except Exception as e:
    e = sys.exc_info()[0]
    helper.internalLogger.error('exception generating thumbnail video')
    helper.einternalLogger.exception(e)    

def getStatusDisplayMedia():
  helper.internalLogger.debug("status getStatusDisplayMedia")
  rt = {}
  rt['photo']={}
  rt['video']={}
  rt['status']={}
  try:
    rt['photo']=listFiles2Array(GLB_configuration["media-photo"],"jpg")
    rt['video']=listFiles2Array(GLB_configuration["media-video"],"mp4")
    rt['photo'].sort() 
    rt['video'].sort() 

    generatePhotoThumbnails(GLB_configuration["media-photo"],rt['photo'],"static_webStreamingAgent")
    generateVideoThumbnails(GLB_configuration["media-video"],rt['video'],"static_webStreamingAgent")
    
    file = open(GLB_configuration["displayStatus"])
    rt['status']=file.read()
    file.close()

  except Exception as e:
        e = sys.exc_info()[0]
        helper.internalLogger.error('Some exception getting displaymedia files')
        helper.einternalLogger.exception(e)  

  return rt
'''----------------------------------------------------------'''
'''----------------      API REST         -------------------'''
'''----------------------------------------------------------'''

api = Flask("api",template_folder="templates",static_folder='static_webStreamingAgent')
api.jinja_env.filters['tojson_pretty'] = to_pretty_json

'''----------------------------------------------------------'''
@api.route('/',methods=["GET", "POST"])
@api.route('/webStreamingAgent/',methods=["GET", "POST"])
def webStreamingAgent_home():
    if request.method == 'POST':
      helper.internalLogger.debug("Processing new request from a form...{0}".format(request.form))
      form2 = request.form.to_dict()
      helper.internalLogger.debug("TODO Processing new request from a form2...{0}".format(form2))   
    
    st=getStatus()
    rt=render_template('index.html', title="web streaming agent Site",status=st)
    return rt


'''----------------------------------------------------------'''
@api.route('/api/v1.0/webStreamingAgent/status', methods=['GET'])
def get_webStreaming_status():
    return json.dumps(getStatus())

def getStatus():
  global GLB_latestChannelOn

  helper.internalLogger.debug("status required")
  rt = {}
  rt['vsw']={}
  rt['vsw']['webStreamingAgent']=getVersion()
  try:
      #TODO
      rt['result']='OK'       
      rt['stats']=GLB_ts.toDict()          

      output="--"
      try:
        output=subprocess.check_output(['tvservice', '-s'])
      except Exception as e:
        e = sys.exc_info()[0]
        helper.internalLogger.error('tvservice not seems to work')
        helper.einternalLogger.exception(e)  


      if "HDMI" in str(output):
          rt['hdmi']=True
      else:
          rt['hdmi']=False
      #state 0x12000a [HDMI CEA (16) RGB lim 16:9], 1920x1080 @ 60.00Hz, progressive
      #state 0x40001 [NTSC 4:3], 720x480 @ 60.00Hz, interlaced

      #Now tracker information
      if "trackFile" in GLB_configuration:     
        rt['tracking']=what2track()
      else:
        rt['tracking']={}

      rt['playing']=GLB_latestChannelOn


      rt['displayMedia']=getStatusDisplayMedia()

      helper.internalLogger.debug("status {0}".format(rt))

      return rt

  except Exception as e:
    e = sys.exc_info()[0]
    helper.internalLogger.error('Error: gathering status')
    helper.einternalLogger.exception(e)  
    rt={'result': 'KO'}
    helper.internalLogger.debug("status failed")

  return rt


@api.route('/api/v1.0/webStreamingAgent/reboot', methods=['GET'])
def get_webStreaming_reboot():
  helper.internalLogger.debug("reboot required")
  rt = {}
  try:
        import os
        os.system('sudo shutdown -r now &')
        rt['result']='OK'
  except Exception as e:
        helper.internalLogger.error('reboot not seems to work')
        helper.einternalLogger.exception(e)  
        rt['result']='KO'
  rtjson=json.dumps(rt)
  return rtjson


@api.route('/api/v1.0/webStreamingAgent/tracker', methods=['POST'])
def post_webStreaming_tracker():
    rt=jsonify({'result': 'OK'})
    if not request.json: 
        abort(400)

    if "trackFile" in GLB_configuration:
        with open(GLB_configuration["trackFile"], 'w') as outfile:
          json.dump(request.json, outfile)
          return rt, 201

    abort(400)


'''----------------------------------------------------------'''

def cleanFile(path):
  helper.internalLogger.debug("Cleaning item: {0}".format(path))
  if os.path.isfile(path):
      os.remove(path)


@api.route('/clean/photo/<name>',methods=["GET"])
@api.route('/webStreamingAgent/clean/photo/<name>',methods=["GET"])
def webStreamingAgent_gui_photo_clean(name):
   helper.internalLogger.debug("GUI clean {0}...".format(name))
   path=GLB_configuration["media-photo"]+"/"+name
   cleanFile(path)
   return redirect(url_for('webStreamingAgent_home'))

@api.route('/clean/video/<name>',methods=["GET"])
@api.route('/webStreamingAgent/clean/video/<name>',methods=["GET"])
def webStreamingAgent_gui_video_clean(name):
   helper.internalLogger.debug("GUI clean {0}...".format(name))
   path=GLB_configuration["media-video"]+"/"+name
   cleanFile(path)
   return redirect(url_for('webStreamingAgent_home'))


'''----------------------------------------------------------'''
'''----------------       what2track        -------------------'''
'''----------------------------------------------------------'''

def what2track():
  rt={}

  if "trackFile" in GLB_configuration:
   try:
     with open(GLB_configuration["trackFile"]) as json_data:
       rt = json.load(json_data)

   except Exception as e:
     helper.internalLogger.error("Error processing what to track in config".format(GLB_configuration))
     helper.einternalLogger.exception(e)

  return rt

'''----------------------------------------------------------'''
'''----------------       targetChannel   -------------------'''
'''----------------------------------------------------------'''

def targetChannel():
  data=what2track()
  rt = ""
  if "channel" in data:
    rt= data["channel"]
  return rt


def getKPI(cmd):
  rt=0
  try:
    r=subprocess.run(cmd, shell=True,universal_newlines=True, stdout=subprocess.PIPE,   stderr=subprocess.PIPE)
    if r!="":
      rt=int(r.stdout)
  except Exception as e:
    helper.internalLogger.error("Error in getCpuUsage {0}".format(r))
    helper.einternalLogger.exception(e)
  return rt

'''----------------------------------------------------------'''
'''----------------       amIReceivingStreaming         -------------------'''
'''----------------------------------------------------------'''
def amIReceivingStreaming():
 global GLB_latestCPU
 global GLB_latestBW
 rt=False
 try:

    GLB_ts.updateKPIs()

    if ((not GLB_ts.latestCPU is  None) and  (not GLB_ts.latestCPU is -1) and (GLB_ts.latestCPU >= GLB_configuration["kpi"]["cpu"]["minValue"])) and \
       ((not GLB_ts.latestBW  is  None) and (GLB_ts.latestBW  >= GLB_configuration["kpi"]["bwKbps"]["minValue"])):
       rt=True
     
 except Exception as e:
    e = sys.exc_info()[0]
    helper.internalLogger.error('Error: something goes bad trying to monitor some kpi')
    helper.einternalLogger.exception(e)  

 return rt



'''----------------------------------------------------------'''
def stopPlayer():
    aux=GLB_configuration["browserLauncher"] + " STOP" 
    helper.internalLogger.debug('browserLauncher: Calling {0}...'.format(aux))
    #r=subprocess.run(aux, shell=True,universal_newlines=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    r=subprocess.run(aux, shell=True,universal_newlines=True)

    helper.internalLogger.debug('browserLauncher: Result: {0}'.format(r))


'''----------------------------------------------------------'''
def startPlayer(p):
    aux=GLB_configuration["browserLauncher"] + " " \
      + '"'+ p +'"'+ " " \
      + str(GLB_configuration["playButton"]["x"]) + " " \
      + str(GLB_configuration["playButton"]["y"]) + " " \
      + str(GLB_configuration["loadTime"])
    helper.internalLogger.debug('browserLauncher: Calling {0}...'.format(aux))
    r=subprocess.run(aux, shell=True,universal_newlines=True)
    helper.internalLogger.debug('browserLauncher: Result: {0}'.format(r))
    return True


'''----------------------------------------------------------'''
'''----------------       tryPlay     -------------------'''
'''----------------------------------------------------------'''

def tryPlay(channel):
  try:

   startPlayer(channel)

   maxTout=60
   if "browserLauncherTimeout" in GLB_configuration:
     maxTout=GLB_configuration["browserLauncherTimeout"]
   for x in range(10):
     helper.internalLogger.debug('Streaming just launched, checking if ok ... {0}/10'.format(x))
     time.sleep(maxTout/10)
     if amIReceivingStreaming():
       helper.internalLogger.debug('Streaming started to work ok')
       GLB_ts.success()
       return True
     else:
       GLB_ts.updateTimings(False)
  
   GLB_ts.fail()


  except Exception as e:
   e = sys.exc_info()[0]
   helper.internalLogger.error('Error: play file')
   helper.einternalLogger.exception(e) 

  return False      

'''----------------------------------------------------------'''
'''----------------       pollAutoTracker        -------------------'''
'''----------------------------------------------------------'''

def polling():

  global GLB_latestChannelOn

  newChannel=targetChannel()
  rt=False
 

  if ((GLB_latestChannelOn == newChannel) and (newChannel == "")) or\
     ((GLB_latestChannelOn == "KO") and (newChannel == "")):
    helper.internalLogger.debug("Tracker: nothing to track, nothing play.")
    try:
      GLB_ts.updateKPIs() 
    except Exception as e:
      e = sys.exc_info()[0]
      helper.internalLogger.error('Error updating kpi when nothing is played')
      helper.einternalLogger.exception(e) 
    rt=True
  elif GLB_latestChannelOn != newChannel and newChannel == "":
    helper.internalLogger.debug("Tracker: Stopping player...")
    stopPlayer()
    GLB_ts.updateTimings(False)
    rt=True
  elif GLB_latestChannelOn == newChannel:
    helper.internalLogger.debug("Tracker: Checking streaming {0} is still  running...".format(newChannel))
    if amIReceivingStreaming():
      helper.internalLogger.debug("Tracker: Streaming {0} seems to be ok".format(newChannel))
      GLB_ts.updateTimings(True)
      rt=True
    else:
      GLB_ts.updateTimings(False)
      helper.internalLogger.debug("Tracker: streaming {0} seems to be stopped (attempt {0}/5).".format(GLB_ts.consecutiveFails))
      if GLB_ts.consecutiveFails<5:
        helper.internalLogger.debug("Tracker: streaming {0} has stopped, let's try to check again later...".format(newChannel))
        rt=True
      else:       
        rt=tryPlay(newChannel)
  else:
    helper.internalLogger.debug("Tracker: Change of streaming is required, playing: {0}, target: {1} let's try...".format(GLB_latestChannelOn,newChannel))
    rt=tryPlay(newChannel)

  if rt:
    GLB_latestChannelOn=newChannel
  else: 
    GLB_latestChannelOn="KO"



 

'''----------------------------------------------------------'''
'''----------------       M A I N         -------------------'''
'''----------------------------------------------------------'''

def main(configfile):
  print('webStreamingAgent-start -----------------------------')
  
  # Loading config file,
  # Default values
  cfg_log_traces="webStreamingAgent.log"
  cfg_log_exceptions="webStreamingAgente.log"

  # Let's fetch data
  global GLB_configuration
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
  helper.internalLogger.critical('webStreamingAgent-start -------------------------------')  
  helper.einternalLogger.critical('webStreamingAgent-start -------------------------------')

  pollingInterval=5

  GLB_latestChannelOn=""

  global GLB_ts
  GLB_ts=TrackerStats()

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
       polling()
       time.sleep(pollingInterval)


  except Exception as e:
    e = sys.exc_info()[0]
    helper.internalLogger.critical('Error: Exception unprocessed properly. Exiting')
    helper.einternalLogger.exception(e)  
    print('webStreamingAgent-General exeception captured. See log:{0}',format(cfg_log_exceptions))        
    loggingEnd()

'''----------------------------------------------------------'''
'''----------------     apirest_task      -------------------'''
def apirest_task():
  api.run(debug=True, use_reloader=False,port=GLB_configuration["port"],host=GLB_configuration["host"])


'''----------------------------------------------------------'''
'''----------------       loggingEnd      -------------------'''
def loggingEnd():      
  helper.internalLogger.critical('webStreamingAgent-end -----------------------------')        
  print('webStreamingAgent-end -----------------------------')


'''----------------------------------------------------------'''
'''----------------     parse_args        -------------------'''
def parse_args():
    """Parse the args."""
    parser = argparse.ArgumentParser(
        description='webStramingAgent monitor that you are receiving well your favorite web streaming')
    parser.add_argument('--configfile', type=str, required=False,
                        default='/etc/webStreamingAgent.conf',
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


