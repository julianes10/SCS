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
from kodijson import Kodi, PLAYER_VIDEO
import re
import random

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


#Code copy and adapted from https://github.com/adafruit/Adafruit_Python_DHT/blob/master/examples/simpletest.py


from flask import Flask, jsonify,abort,make_response,request, url_for

from helper import *

class TrackerStats:
  def __init__(self):
    self.reset()
  def reset(self):
    self.playOn=True
    self.numEvents = 0
    self.numEventsLIVE = 0
    self.numSourcesTargetEvent = 0
    self.numSourcesTargetEventAvailable = 0
    self.numFails = 0
    self.numSuccess = 0
    self.timeFailing = 0
    self.timeSucceeding = 0
    self.latestUpdate = 0
  def toDict(self):
    rt={}
    rt['numEvents'] = self.numEvents
    rt['numEventsLIVE'] = self.numEventsLIVE
    rt['numSourcesTargetEvent'] = self.numSourcesTargetEvent
    rt['numSourcesTargetEventAvailable'] = self.numSourcesTargetEventAvailable
    rt['numFails'] = self.numFails
    rt['numSuccess'] = self.numSuccess
    rt['timeFailing'] = round(self.timeFailing,2)
    rt['timeSucceeding'] = round(self.timeSucceeding,2)
    return rt

  def success(self):
    self.numSuccess = self.numSuccess+1
    self.updateTimings(True)

  def fail(self):
    self.numFails = self.numFails+1
    self.updateTimings(False)


  def updateTimings(self,on):
    if self.latestUpdate == 0:  #first time only
      self.latestUpdate=time.time()
  
    if self.playOn and on:
      self.timeSucceeding = self.timeSucceeding + (time.time() - self.latestUpdate)
    else:
      self.timeFailing = self.timeFailing + (time.time() - self.latestUpdate)
    self.playOn=on
    self.latestUpdate=time.time()
    '''else if not self.playOn and not on:
      self.timeFailing = self.timeFailing + (time.time() - self.latestUpdate)
    else if not self.playOn and on:
      self.timeFailing = self.timeFailing + (time.time() - self.latestUpdate)
    else if self.playOn and off:
      self.timeFailing = self.timeFailing + (time.time() - self.latestUpdate)
    ''' 


'''----------------------------------------------------------'''
'''----------------      API REST         -------------------'''
'''----------------------------------------------------------'''
api = Flask("api")


@api.route('/api/v1.0/kodi/status', methods=['GET'])
def get_kodi_status():
  helper.internalLogger.debug("status required")
  rt = {}
  rt['vsw']={}
  rt['vsw']['kodiAgent']=getVersion()
  try:
      if kodiAlive():
        rt['result']='OK'
        rt['vsw']['kodi']=getKodiVersion()
        rt['vsw']['sd']=getSDVersion()
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
          content="*" 
          if "content" in GLB_meAsked2play:
            if "keystrings" in GLB_meAsked2play["content"]:
              content=" ".join(GLB_meAsked2play["content"]["keystrings"])
          rt['title']=content+"-"+title+"-"+label 
              
      else:
        rt['result']='KO'

      rt['tracker-stats']=GLB_ts.toDict()       
      

      try:
        output="--"
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
      if "auto-tracker" in configuration:     
        rt['auto-tracker-what']=what2track(configuration["auto-tracker"])
      else:
        rt['auto-tracker-what']={}

      rtjson=json.dumps(rt)

  except Exception as e:
    e = sys.exc_info()[0]
    helper.internalLogger.error('Error: kodi seems not be ready to ping')
    helper.einternalLogger.exception(e)  
    rtjson=jsonify({'result': 'KO'})
    helper.internalLogger.debug("status failed")

  return rtjson


@api.route('/api/v1.0/kodi/reboot', methods=['GET'])
def get_kodi_reboot():
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


@api.route('/api/v1.0/kodi/tracker', methods=['POST'])
def post_kodi_tracker():
    rt=jsonify({'result': 'OK'})
    if not request.json: 
        abort(400)

    if "auto-tracker" in configuration:
      if "what" in configuration["auto-tracker"]:
        with open(configuration["auto-tracker"]["what"], 'w') as outfile:
          json.dump(request.json, outfile)
          return rt, 201

    abort(400)
'''----------------------------------------------------------'''
'''----------------       kodiAlive         -------------------'''
'''----------------------------------------------------------'''
def kodiAlive():


  for x in range(2):
   if x > 0: 
      tryKodi()
   try:
      aux=kodi.JSONRPC.Ping()
      #helper.internalLogger.debug("Ping: {0}".format(aux))      
      if aux['result'] == "pong":
        return True
   except Exception as e:
      e = sys.exc_info()[0]
      helper.internalLogger.error('Error: kodi seems not be ready to ping')

  return False

def getKodiVersion():
   rt={}
   try:
      aux=kodi.Application.GetProperties({ "properties":["version"] })
      if not aux['result']:
         helper.internalLogger.debug("No result kodi version")
      else:
         rt=aux
   except Exception as e:
      e = sys.exc_info()[0]
      helper.internalLogger.error('Error: kodi seems not be ok, getting version fails')
   return rt

def getSDVersion():
   rt={}
   try:
      aux=kodi.Addons.GetAddonDetails({ "addonid":"plugin.video.SportsDevil", "properties":["version"] })
      if not aux['result']:
         helper.internalLogger.debug("No result sd version")
      else:
         rt=aux
   except Exception as e:
      e = sys.exc_info()[0]
      helper.internalLogger.error('Error: kodi seems not be ok, getting version fails')
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
   #if x in target:
   #m = re.search(x,target)
   #if m:
     matchedItems=matchedItems+1

 if matchedItems>0:
     if matchedItems == items:
       helper.internalLogger.debug("Full match detected {0}".format(target))
       rt=True
     #else:
     #  helper.internalLogger.debug("Almost there but not enough matching: {0}/{1} - title  {2}, target content {3}".format(matchedItems,items,target,listOfkeys))

   
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
   helper.internalLogger.debug("Not watching it. Video Off")
  else:
   #TODO ONLY MANAGE 1 PLAYER
   pid=aux['result'][0]['playerid']
   #helper.internalLogger.debug("Player Id:{0}".format(pid))
   aux=kodi.Player.GetItem({"properties": ["title"], "playerid": pid })
   #helper.internalLogger.debug("Player INFO:{0}".format(aux))
   title=(aux['result']['item']['title'])
   label=(aux['result']['item']['label'])
   #Try to match keystrings on it title
   if "keystrings" in c:
     if fullMatch(c["keystrings"],title) or fullMatch(c["keystrings"],label):
       helper.internalLogger.debug("YES - Already playing it {0}".format(c["keystrings"]))
       rt=True

     #Last chance to match, is what i've asked to play even if no content in title?
     if "content" in GLB_meAsked2play:
        if GLB_meAsked2play["content"] == c:
          if fullMatch(GLB_meAsked2play["title"],title) or fullMatch(GLB_meAsked2play["title"],label):
            helper.internalLogger.debug("YES - Already playing it {0}, i've asked as {1}".format(c["keystrings"],GLB_meAsked2play["title"]))
            rt=True
      
     
 except Exception as e:
    e = sys.exc_info()[0]
    helper.internalLogger.error('Error: something goes bad trying to matching content keystring and now playing title')
    helper.einternalLogger.exception(e)  

 return rt


'''----------------------------------------------------------'''
'''----------------       getFileDir      -------------------'''
'''----------------------------------------------------------'''
def getFileDir(d):
  rt=[]
  try:
   params={"properties":["title"],
          "media":"video",
          "sort": { "method":"label","order":"ascending"},
          "directory": d
          }
   ## helper.internalLogger.debug('Quering : {0}'.format(params))
   aux=kodi.Files.GetDirectory(params)

   if "result" in aux:
     helper.internalLogger.debug('Dir results: {0}'.format(len(aux["result"]["files"])))
     rt=aux["result"]["files"]
   else: 
     helper.internalLogger.error('Error: get dir'.format(aux))

  except Exception as e:
   e = sys.exc_info()[0]
   helper.internalLogger.error('Error: get dir'.format(aux))
   helper.einternalLogger.exception(e) 
  
  return rt

'''----------------------------------------------------------'''
'''----------------       getEventsNow    -------------------'''
'''----------------------------------------------------------'''
def getEventsNow(trackerConfig):
  rt=[]
  try:
   helper.internalLogger.debug('Getting list of events available now... ')
   rt=getFileDir(trackerConfig["addon"]["magic-url"])
   helper.internalLogger.debug('Events available now: {0}'.format(len(rt)))
  except Exception as e:
   e = sys.exc_info()[0]
   helper.internalLogger.error('Error: gathering list of events now')
   helper.einternalLogger.exception(e)  


  GLB_ts.numEvents=len(rt)

  cont=0
  for ev in rt:
   if "LIVE" in ev["title"]:
     cont=cont+1
  GLB_ts.numEventsLIVE = cont


  return rt


'''----------------------------------------------------------'''
'''----------------       getEventSources    -------------------'''
'''----------------------------------------------------------'''
def getEventSources(item):
  rt=[]
  try:
   helper.internalLogger.debug('Getting event sources... ')
   rt=getFileDir(item["file"])
   helper.internalLogger.debug('Sources available for target event: {0}'.format(len(rt)))
  except Exception as e:
   e = sys.exc_info()[0]
   helper.internalLogger.error('Error: gathering list sources for the event')
   helper.einternalLogger.exception(e)  
  return rt



'''----------------------------------------------------------'''
def spawnedPlayFileTask(params):
  aux=kodi.Files.GetDirectory(params) 
  helper.internalLogger.debug('[{0}]File play result: {1}'.format(os.getpid(),aux))


'''----------------------------------------------------------'''
def spawningPlayFile(p):
  newpid = os.fork()
  if newpid == 0:
    spawnedPlayFileTask(p)
    exit(0)
  return newpid

'''----------------------------------------------------------'''
'''----------------       tryPlayFile     -------------------'''
'''----------------------------------------------------------'''

def tryPlayFile(c,sources):
 random.shuffle(sources)


 GLB_ts.numSourcesTargetEvent = len(sources)
 cont=0
 for source in sources:
   if "Acestream" in source["title"] or "Alieztv" in source["title"]:
     continue
   cont=cont+1
 GLB_ts.numSourcesTargetEventAvailable = cont


 for source in sources:
  try:
   if "Acestream" in source["title"] or "Alieztv" in source["title"]:
     helper.internalLogger.debug('Skipped ACEstream or Alieztv')
     continue
   params={"properties":["title"],
          "media":"video",
          "sort": { "method":"label","order":"ascending"},
          "directory": source["file"]
          }

   helper.internalLogger.debug('File to play: {0}'.format(source["title"]))

   ''' THIS NOT WORKING FINE... BLOCKS IN UI AND PROMT ERROR MOST OF TIME EVEN PLAY WELL
   WORKAROUND: LAUNCH IN BACKGROUND AND JUST CHECK PLAYER STATUS AFTER A FEW SECONDS... 
   aux=kodi.Files.GetDirectory(params) 
   helper.internalLogger.debug('File play result: {0}'.format(aux))
   if "error" in aux:
     helper.internalLogger.debug('Got error. Skipping this one')
     continue
   '''
   pid=spawningPlayFile(params)
   global GLB_meAsked2play
   GLB_meAsked2play={"content":c,"title":source["title"]}  
   # some trackers later do not back with original content but this title...

   for x in range(30):
     time.sleep(3)
     if amIwatchingIt(c):
       helper.internalLogger.debug('Killing subprocess just in case')
       os.kill(pid, signal.SIGTERM)
       GLB_ts.success()
       return
     else:
       GLB_ts.updateTimings(False)
  
   helper.internalLogger.debug('Killing subprocess just in case')
   os.kill(pid, signal.SIGKILL)
   GLB_ts.fail()

  except Exception as e:
   e = sys.exc_info()[0]
   helper.internalLogger.error('Error: play file')
   helper.einternalLogger.exception(e) 
                
'''----------------------------------------------------------'''
'''----------------       searchAndPlayContent        -------------------'''
'''----------------------------------------------------------'''
def searchAndPlayContent(c,trackerConfig):
 rt=False
 if not "keystrings" in c:
   return False

 try:
  eventsNow=getEventsNow(trackerConfig)
  for event in eventsNow:
    #Try to match keystrings on it title
    #helper.internalLogger.debug('Considering event {0}...'.format(event["title"]))
    if "keystrings" in c:
     if fullMatch(c["keystrings"],event["label"]) or fullMatch(c["keystrings"],event["title"]):
       helper.internalLogger.debug('Event to play: {0} file {1}'.format(event["title"],event["label"]))
       sources=getEventSources(event)
       tryPlayFile(c,sources)
       return True
     
 except Exception as e:
    e = sys.exc_info()[0]
    helper.internalLogger.error('Error: something goes bad trying search or play event')
    helper.einternalLogger.exception(e)  

 helper.internalLogger.debug('Not matching any event')
 return rt


'''----------------------------------------------------------'''
'''----------------       pollAutoTracker        -------------------'''
'''----------------------------------------------------------'''

def pollAutoTracker(trackerConfig):

  if not kodiAlive():
    helper.internalLogger.error("Tracker: kodi is ko, useless to try to track anything")
    return
  what= what2track(trackerConfig)
  if not "content" in what:
    helper.internalLogger.debug("Tracker: nothing to track yet")
    return
  if not what["content"]:
    helper.internalLogger.debug("Tracker: empty list to track")
    return

  helper.internalLogger.debug("Tracker: Checking status of contents...")
  for c in what["content"]:
    if "keystrings" in c:
      helper.internalLogger.debug("Tracker: Checking status of content {0}".format(c['keystrings']))
      if amIwatchingIt(c):
        GLB_ts.updateTimings(True)
      else:
        GLB_ts.updateTimings(False)
        if searchAndPlayContent(c,trackerConfig):
          return  ### NOTE it breaks so it is like a prio list...
      

'''----------------------------------------------------------'''
'''----------------       M A I N         -------------------'''
'''----------------------------------------------------------'''
def tryKodi():
  global kodi
  try:
    helper.internalLogger.debug("Trying get kodi at {0}...".format(configuration["kodi"]["url"]))
    #Login with default kodi/kodi credentials
    if "login" in configuration["kodi"]:
      kodi = Kodi(configuration["kodi"]["url"],configuration["kodi"]["login"],configuration["kodi"]["password"])
    else:
      kodi = Kodi(configuration["kodi"]["url"])
  except Exception as e:
    helper.internalLogger.critical("Error, not kodi at {0}.".format(configuration["kodi"]["url"]))
    helper.einternalLogger.exception(e)
    loggingEnd()
    return  


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
  helper.internalLogger.critical('kodiAgent-start -------------------------------')  
  helper.einternalLogger.critical('kodiAgent-start -------------------------------')

  global GLB_meAsked2play
  GLB_meAsked2play={}

  enableTracker=False
  pollingInterval=5
  if "auto-tracker" in configuration:
    if "enable" in configuration["auto-tracker"]:
      enableTracker=configuration["auto-tracker"]["enable"]
    if "polling-interval" in configuration["auto-tracker"]:
      pollingInterval=configuration["auto-tracker"]["polling-interval"]
        
  global GLB_ts
  GLB_ts=TrackerStats()

  try:

    tryKodi() 

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

## TODO
# REBOOT
# REST FOR UPDATE TRACKERLIST
# FILTER SOPCAST? 
# APP MOVIL
# try in spawned
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
