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
import telebot
from helper import *
from flask import Flask, render_template,redirect
from flask import Flask, jsonify,abort,make_response,request, url_for
from datetime import datetime

_FINISHTASKS=False


''' 
------------- ongoing fields

{"periodic": [
  {"action": "test", "interval": 7200, "start": "01:00:00", "nbrOfTimes": 0,  "nbrOfTimesWithSubscribers": 0, 
  "subscribers": [], "nexttime": 1566428400.0}, 
  ... 
 ]
"event": [
  {"name": "kk", "nbrOfTimes": 0, "nbrOfTimes": 0,"nbrOfTimesWithSubscribers": 0, "subscribers": []}, 
  ...
 ]
}
'''


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
'''----------------      API REST         -------------------'''
'''----------------------------------------------------------'''
api = Flask("api",template_folder="templates",static_folder='static_telegram')
api.jinja_env.filters['datetime'] = format_datetime


'''----------------------------------------------------------'''
@api.route('/api/v1.0/telegramBOT/event', methods=['POST'])
def post_telegram_event():
    if not request.json:
        helper.internalLogger.debug("It is not a json. Back with error")
        abort(400)
    return requestNewEvent(request.json)


def requestNewEvent(req):
    #TODO control error
    rt=jsonify({'result': 'OK'})
    eventTask(req)
    return rt

'''----------------------------------------------------------'''
@api.route('/',methods=["GET", "POST"])
@api.route('/telegramBOT/',methods=["GET", "POST"])
def telegramBOT_home():
    if request.method == 'POST':
      helper.internalLogger.debug("Processing new request from a form...{0}".format(request.form))
      form2 = request.form.to_dict()
      helper.internalLogger.debug("Processing new request from a form2...{0}".format(form2))   
      requestNewEvent(form2)
    
    url={}

    st=getStatus()
    rt=render_template('index.html', title="TelegramBOT Site",status=st)
    return rt

'''----------------------------------------------------------'''
@api.route('/api/v1.0/telegramBOT/status', methods=['GET'])
def get_telegramBOT_status():
    return json.dumps(getStatus())

def getStatus():
    rt=LOCK()
    UNLOCK(rt)
    return rt


'''----------------------------------------------------------'''
@api.route('/clean/<name>',methods=["GET"])
@api.route('/telegramBOT/clean/<name>',methods=["GET"])
def telegramBOT_gui_clean(name):
   helper.internalLogger.debug("GUI clean {0}...".format(name))
   #TODO cleanProject(name)
   return redirect(url_for('telegramBOT_home'))

'''----------------------------------------------------------'''
'''----------------       periodic tasks  -------------------'''
'''----------------------------------------------------------'''

def periodicTasks():

  global bot
  helper.internalLogger.debug("TeleBot periodic start")
  while not _FINISHTASKS:
    ongoing=LOCK()  
    now=time.time()
    for item in ongoing["periodic"]:
      ## Tunning firstime
      if not "nextTime" in item:
        if not "subscribers" in item:
          item["subscribers"] = []
        helper.internalLogger.debug("Tunning nextTime for action {0}...".format(item["action"]))
        if not "start" in item:
          item["nextTime"] = now
          helper.internalLogger.debug("No explicit start so, nextTime for action is now {0}...".format(item["nextTime"]))
        else:
          aux=time.localtime()
          t=(aux.tm_year,aux.tm_mon,aux.tm_mday,0,0,0,aux.tm_wday,aux.tm_yday,0)
          nowToday00=time.mktime(t)
          datetime_str="1/1/1970 " + item["start"] + " +0100"
          aux2 = datetime.strptime(datetime_str, '%m/%d/%Y %H:%M:%S %z')
          item["nextTime"] = nowToday00 + datetime.timestamp(aux2)     
          #Now check nearest slot based on interval
          helper.internalLogger.debug("Explicit start at {0}, nextTime for action is  {1}-{2}...".format(item["start"],item["nextTime"],datetime.fromtimestamp(item["nextTime"])))    
          while (now > (item["nextTime"])):
            item["nextTime"]=item["nextTime"]+item["interval"]           
          helper.internalLogger.debug("Explicit FIXED start at {0}, nextTime for action is  {1}-{2}...".format(item["start"],item["nextTime"],datetime.fromtimestamp(item["nextTime"])))    

      ## Triggering when is fair

      if ( item["nextTime"] <= now ):
        helper.internalLogger.debug("Time for periodic action {0}...".format(item["action"]))
        helper.internalLogger.debug("EVAL: now       {0} \t| {1}".format(now,datetime.fromtimestamp(now)))
        helper.internalLogger.debug("EVAL: nextTime {0} \t\t| {1}".format(item["nextTime"],datetime.fromtimestamp(item["nextTime"])))
        helper.internalLogger.debug("EVAL: interval  {0}".format(item["interval"]))
        item["nextTime"]=now+item["interval"]    
        updateNbrOfTimesCounters(item)
        runActionAndSendMessageToSubscribers(item["subscribers"],item["action"])
    #helper.internalLogger.critical('ongoing {0}'.format(ongoing))
    UNLOCK(ongoing)
    time.sleep(1)


'''----------------------------------------------------------'''
def updateNbrOfTimesCounters(item):
  if not "nbrOfTimes" in item:
          item["nbrOfTimes"]=0
          item["nbrOfTimesWithSubscribers"]=0
  item["nbrOfTimes"] = item["nbrOfTimes"] + 1
  if "subscribers" in item:
    if len(item["subscribers"])>0:
          item["nbrOfTimesWithSubscribers"] = item["nbrOfTimesWithSubscribers"] + 1

'''----------------------------------------------------------'''
'''----------------       event task      -------------------'''
'''----------------------------------------------------------'''

def eventTask(event):
  global bot
  rt=True
  helper.internalLogger.debug("New event to process: {0}".format(event))
  #Purge stupid event TODO
  ongoing=LOCK()

  try: 
   if "event" in ongoing:
    for item in ongoing["event"]:
      if ( event["name"] == item["name"] ):
        helper.internalLogger.debug("Known event, let's check subscribers... ")
        updateNbrOfTimesCounters(item)

        #Sending event indication
        sendTextMessageToSubscribers(item["subscribers"],"EVENT: " + event["name"])

        #Executing event, let's check if come with EXCLICIT items
        if "text" in event:
            sendTextMessageToSubscribers(item["subscribers"],event["text"])
        if "img" in event:
            sendImageMessageToSubscribers(item["subscribers"],event["img"])
        if "video" in event:
            sendVideoMessageToSubscribers(item["subscribers"],event["video"])
        if "filetext" in event:
            sendTextFileMessageToSubscribers(item["subscribers"],event["filetext"])

        #Later, let's check if come with dynamic action associated
        if "action" in event:
            runActionAndSendMessageToSubscribers(item["subscribers"],event["action"])

        #Later, let's check if come with predefined action associated
        if "action" in item:
            runActionAndSendMessageToSubscribers(item["subscribers"],item["action"])

  except Exception as e:
    helper.internalLogger.error('Error: processing event {0}'.format(event))
    e = sys.exc_info()[0]
    helper.einternalLogger.exception(e)
    rt=False
  #helper.internalLogger.critical('ongoing {0}'.format(ongoing))
  UNLOCK(ongoing)

  return rt
'''----------------------------------------------------------'''
def sendTextMessageToSubscribers(subscriberList, text):
  if text == "":
    return
  helper.internalLogger.debug("Text to send : {0}".format(text))
  for i in subscriberList:
    helper.internalLogger.debug("Text to : {0}".format(i))
    bot.send_message(i,text)

'''----------------------------------------------------------'''
def sendImageMessageToSubscribers(subscriberList, path):
  for i in subscriberList:
    sendImageToSubscriber(i,path)

'''----------------------------------------------------------'''
def sendVideoMessageToSubscribers(subscriberList, path):
  for i in subscriberList:
    sendVideoToSubscriber(i,path)

'''----------------------------------------------------------'''
def sendTextFileMessageToSubscribers(subscriberList, path):
  for i in subscriberList:
    sendTextFileToSubscriber(i,path)

'''----------------------------------------------------------'''
def sendImageToSubscriber(chatid, path):
  rt=True
  if os.path.isfile(path):
    helper.internalLogger.debug("File: {0}".format(path))
    f = open(path, 'rb')
    if path[-4:] == ".gif":
      bot.send_document(chatid, f)
    else:
      bot.send_photo(chatid, f)
    f.close()
  else: 
    bot.send_message(chatid,"No image available, sorry")
  return rt

'''----------------------------------------------------------'''
def sendVideoToSubscriber(chatid, path):
  rt=True
  if os.path.isfile(path):
    helper.internalLogger.debug("File: {0}".format(path))
    f = open(path, 'rb')
    bot.send_video(chatid, f)
    f.close()
  else: 
    bot.send_message(chatid,"No video available, sorry")
  return rt

'''----------------------------------------------------------'''
def sendTextFileToSubscriber(chatid, path):
  rt=True
  if os.path.isfile(path):
    helper.internalLogger.debug("File: {0}".format(path))
    f = open(path, 'rb')
    t = f.read()
    bot.send_message(chatid, f)
    f.close()
  else: 
    bot.send_message(chatid,"No text file available, sorry")
  return rt




'''----------------------------------------------------------'''
def runActionAndSendMessageToSubscribers(subscriberList, actionName):
  try: 
    actionDescriptor=GLB_configuration["actions"][actionName]
  except Exception as e:
    helper.internalLogger.error('Error: not configured action. Cannot be sent to subscribers {0}'.format(actionName))
    e = sys.exc_info()[0]
    helper.internalLogger.critical('Error: not configured action. Cannot be sent to subscribers {0}'.format(actionName))
    helper.einternalLogger.exception(e)
    return 

  if len(subscriberList)>0:
    result=runAction(actionDescriptor,"AUTO")
    for i in subscriberList:
      if result is None:
        bot.send_message(i,'Error: Exception executing {0}'.format(key))
      else:
        sendActionResult(i,actionDescriptor,result) 


'''----------------------------------------------------------'''
'''----------------    runAction            -----------------'''

def runAction(action,originalMsg):
  rt=None
  msgSplitted=originalMsg.split()
  try:
    cmd=action["cmd"]
    if "TELEGRAM_COMMAND" in action["cmd"]:
        helper.internalLogger.debug("Custom cmd with TELEGRAM_COMMAND {0}'".format(cmd)) 
        cmd=action["cmd"].replace("TELEGRAM_COMMAND",' '.join(msgSplitted[1:]))

    if "include-message-args" in action:
      if "single-args" in action:
        cmd=action["cmd"] + "'"+' '.join(msgSplitted[1:])+"'"
      else:
        cmd=action["cmd"] + ' '+' '.join(msgSplitted[1:])
  
    global bot
    bg=False
    if "background" in action:
      if action["background"]:
        bg=True


    if bg:
        helper.internalLogger.debug("Executing in bg Cmd {0}...".format(cmd))
        subprocess.Popen(['bash','-c',cmd])
        helper.internalLogger.debug("Just. Executed {0} ".format(cmd))
        return "Action Executed in background"
    
    #else blocking & checking output
    helper.internalLogger.debug("Executing bloking Cmd {0}...".format(cmd))
    result=subprocess.check_output(['bash','-c',cmd])
    helper.internalLogger.debug("Cmd {0}, result {1}".format(cmd,result))
    rt=result
  except Exception as e:
    e = sys.exc_info()[0]
    helper.internalLogger.critical('Error: Exception executing {0}'.format(action))
    helper.einternalLogger.exception(e)  
 
  helper.internalLogger.debug("Let's respond with associated info to action{0}".format(action))
  return rt


'''----------------------------------------------------------'''
'''----------------    sendActionResult     -----------------'''

def sendActionResult(chatid,action,result):
  #Coding up to 5 retrials
  retry=0
  while retry < 5:
    try:
      feedback=False
      if "video" in action: 
        helper.internalLogger.debug("Action with video")
        feedback=sendVideoToSubscriber(chatid,action["video"])
      if "image" in action:
        helper.internalLogger.debug("Action with image")
        feedback=sendImageToSubscriber(chatid,action["image"])
      if "text" in action:
        helper.internalLogger.debug("Action with text file")
        feedback=sendTextFileToSubscriber(chatid,action["text"])
      if len(result.lstrip())>0:
        bot.send_message(chatid,result)
        helper.internalLogger.debug("Action: {0} executed, send output".format(action,result))
        feedback=True

      if not feedback:
        helper.internalLogger.debug("Silent or buggy action executed: {0}".format(action))
        bot.send_message(chatid,"Action just executed")



      break  #No exceptions, no retrials

    except Exception as e:
      retry=retry+1
      e = sys.exc_info()[0]
      helper.internalLogger.critical('Error: Exception using API {0}. Attempt {1}'.format(action,retry))
      helper.einternalLogger.exception(e)  
      #bot.send_message(chatid,'Error: Exception executing {0}'.format(action))

  if retry==5:
    bot.send_message(chatid,"No feedback action after {0} retrials".format(retry))



  helper.internalLogger.debug("Action ended")

  ### TODO limpiar los ficheros??? no se, se carga multiusuario...

  return None


'''----------------------------------------------------------'''
def LOCK():
  global GLB_configuration 
  rt = {}
  if not "ongoingDB" in GLB_configuration:
    return rt

  p=GLB_configuration["ongoingDB"]+".lock"
  while os.path.exists(p):
    time.sleep(1)
  # create the lock file
  lock_file = open(p, "w")
  lock_file.close()


  try:
      with open(GLB_configuration["ongoingDB"]) as json_data:
          rt = json.load(json_data)
  except Exception as e:
      helper.internalLogger.critical("Error opening ongoingDB: {0}.".format(GLB_configuration["ongoingDB"]))
      helper.einternalLogger.exception(e)
  #helper.internalLogger.debug("LOCKLOCKLOCKLOCK {0}.".format(rt))
  return rt

'''----------------------------------------------------------'''
def UNLOCK(data):
  #helper.internalLogger.debug("UNLOCKUNLOCKUNLOCKUNLOCK {0}.".format(data))
  with open(GLB_configuration["ongoingDB"], 'w') as fp:
    json.dump(data, fp)

  p=GLB_configuration["ongoingDB"]+".lock"
  if os.path.exists(p):
    os.remove(p)



'''----------------------------------------------------------'''
def delSubscriber(id,tableName,item2subscribe=None):

  if item2subscribe==None:
     aux="ALL"
  else:
     aux=item2subscribe
     if tableName == "event":
      if not isValidItem(aux,GLB_configuration["event"],"name"):
        bot.send_message(id,"Error. No {0} in configuration".format(aux))
        return
     else:
      if not isValidItem(aux,GLB_configuration["periodic"],"action"):
        bot.send_message(id,"Error. No {0} in configuration".format(aux))
        return


  ongoing=LOCK()

  if not tableName in ongoing:
    helper.internalLogger.error("Error. No {0} in configuration".format(tableName))
    bot.send_message(id,"Error. No {0} in configuration".format(tableName))
    UNLOCK(ongoing)
    return

  bot.send_message(id,'Unsubscribing you to {0} as {1} task...'.format(aux,tableName))
  
  for i in ongoing[tableName]:
    if "name" in i:
      matchingField=i["name"]
    else :
      matchingField=i["action"]
    if item2subscribe==None or item2subscribe==matchingField:
      if not "subscribers" in i:
        i["subscribers"]=[]
      if id in i["subscribers"]:
        bot.send_message(id,'Your are now unsubscribed to {0} as {1} task.'.format(matchingField,tableName))
        i["subscribers"].remove(id)
      else:
        bot.send_message(id,'Your are not subscribed to {0} as {1} task.'.format(matchingField,tableName))


  #bk subscribers nv
  try:
   with open(GLB_configuration["ongoingDBNV"], 'w+') as fp:
    json.dump(ongoing, fp)
  except Exception as e:
      helper.internalLogger.critical("Error opening ongoingDBNV")
      helper.einternalLogger.exception(e)

  UNLOCK(ongoing)


 
'''----------------------------------------------------------'''
def addSubscriber(id,tableName,item2subscribe=None):

  if item2subscribe==None:
     aux="ALL"
  else:
     aux=item2subscribe.lower()
     if tableName == "event":
        if not isValidItem(aux,GLB_configuration["event"],"name"):
          bot.send_message(id,"Error. No {0} in configuration".format(aux))
          return
     else:
        if not isValidItem(aux,GLB_configuration["periodic"],"action"):
          bot.send_message(id,"Error. No {0} in configuration".format(aux))
          return



  ongoing=LOCK()

  if not tableName in ongoing:
    helper.internalLogger.error("Error. No {0} in configuration".format(tableName))
    bot.send_message(id,"Error. No {0} in configuration".format(tableName))
    UNLOCK(ongoing)
    return

  bot.send_message(id,'Suscribing you to {0} as {1} task...'.format(aux,tableName))

  for i in ongoing[tableName]:
    if "name" in i:
      matchingField=i["name"]
    else:
      matchingField=i["action"]

    if item2subscribe==None or item2subscribe==matchingField:
      if not "subscribers" in i:
        i["subscribers"]=[]
      if id in i["subscribers"]:
        bot.send_message(id,'Your are already subscribed to {0} as {1} task.'.format(matchingField,tableName))
      else:
        bot.send_message(id,'Your are now subscribed to {0} as {1} task.'.format(matchingField,tableName))
        i["subscribers"].append(id)

  try:
   with open(GLB_configuration["ongoingDBNV"], 'w+') as fp:
    json.dump(ongoing, fp)
  except Exception as e:
      helper.internalLogger.critical("Error opening ongoingDBNV")
      helper.einternalLogger.exception(e)

  #helper.internalLogger.critical('ongoing {0}'.format(ongoing))
  UNLOCK(ongoing)
  





'''----------------------------------------------------------'''
def recoverOngoingTasks():

  UNLOCK({}) # cleanup
  ongoing=LOCK()

  ongoing["periodic"]={}
  if ("periodic" in GLB_configuration):
    ongoing["periodic"]=GLB_configuration["periodic"]

  ongoing["event"]={}
  if ("event" in GLB_configuration):
    ongoing["event"]=GLB_configuration["event"]

  if ("periodic" in GLB_configuration) or ("event" in GLB_configuration):
    # Recover form non-volatile information if any
    tmp={}
    tmp["event"]={}
    tmp["periodic"]={}
    try:
      with open(GLB_configuration["ongoingDBNV"]) as json_data:
          tmp = json.load(json_data)
    except Exception as e:
      helper.internalLogger.critical("Error opening ongoingDBNV. Subscriptions are reset")
      helper.einternalLogger.exception(e)
      
    # Check that every action is still in new configuration
    try:
     for itemCfg in ongoing["periodic"]:
      helper.internalLogger.debug("Recovering subscribers for action {0}....".format(itemCfg["action"]))
      if "periodic" in tmp:
       for itemNV in tmp["periodic"]:
        if itemNV["action"] == itemCfg["action"]:
          #Update subscribers
          itemCfg["subscribers"] = []
          if "subscribers" in itemNV:
            itemCfg["subscribers"] = itemNV["subscribers"]
          helper.internalLogger.debug("Recovered subscribers for periodic action {0}:{1}.".format(itemCfg["action"],itemCfg["subscribers"]))
          break
    except Exception as e:
      helper.internalLogger.critical("Error crosschecking ongoingNV")
      helper.einternalLogger.exception(e)

    # Check that every action is still in new configuration
    try:
     for itemCfg in ongoing["event"]:
      helper.internalLogger.debug("Recovering subscribers for event {0}....".format(itemCfg["name"]))
      if "event" in tmp:
       for itemNV in tmp["event"]:
        if itemNV["name"] == itemCfg["name"]:
          #Update subscribers
          itemCfg["subscribers"] = []
          if "subscribers" in itemNV:
            itemCfg["subscribers"] = itemNV["subscribers"]
          helper.internalLogger.debug("Recovered subscribers for event {0}:{1}.".format(itemCfg["name"],itemCfg["subscribers"]))
          break
    except Exception as e:
      helper.internalLogger.critical("Error crosschecking ongoingNV")
      helper.einternalLogger.exception(e)


  ##helper.internalLogger.debug("GGGGGGGGGGGGGGGGGGG {0}.".format(ongoing))
  UNLOCK(ongoing)



'''----------------------------------------------------------'''
def isValidItem(msg,l,key):
  rt=False
  # Custom by configuration options
  for item in l:
    if key in item:
      if msg == item[key].lower():
        rt=True
  return rt

'''----------------------------------------------------------'''
'''----------------------------------------------------------'''
'''----------------------------------------------------------'''
'''----------------------------------------------------------'''
'''----------------------------------------------------------'''
def processPhotoMessage(message):

  now=time.time()
  try:
   helper.internalLogger.debug("message.photo:{0}".format(message.photo))
   fileID = message.photo[-1].file_id
   file = bot.get_file(fileID)
   downloaded_file = bot.download_file(file.file_path)
   pathFile=GLB_configuration["media-photo"]["basePath"]+"/"+str(now)+".jpg"
   #helper.internalLogger.debug("file info:{0} {1} {2}".format(file.file_path,downloaded_file,pathFile))
   helper.internalLogger.debug("Dumping photo in :{0}".format(pathFile))
   with open(pathFile, 'wb') as new_file:
         new_file.write(downloaded_file)
   item=GLB_configuration["actions"][GLB_configuration["media-photo"]["action"]]
   result=runAction(item,"photo "+pathFile)
   if result is None:
     bot.send_message(message.chat.id,'Error: Exception executing {0}'.format(key))
     bot.reply_to(message, "Ignoring this request.")
   else:
     sendActionResult(message.chat.id,item,result)    

  except Exception as e:
    e = sys.exc_info()[0]
    helper.internalLogger.critical('Error in processPhotoMessage')
    helper.einternalLogger.exception(e)  


'''----------------------------------------------------------'''
'''----------------------------------------------------------'''
'''----------------------------------------------------------'''
'''----------------------------------------------------------'''
'''----------------------------------------------------------'''
def processVideoMessage(message):
  now=time.time()
  try:
   helper.internalLogger.debug("message.video:{0}".format(message.video))
   fileID = message.video.file_id
   file = bot.get_file(fileID)
   downloaded_file = bot.download_file(file.file_path)
   pathFile=GLB_configuration["media-video"]["basePath"]+"/"+str(now)+".mp4"
   #helper.internalLogger.debug("file info:{0} {1} {2}".format(file.file_path,downloaded_file,pathFile))
   helper.internalLogger.debug("Dumping video in :{0}".format(pathFile))
   with open(pathFile, 'wb') as new_file:
         new_file.write(downloaded_file)
   item=GLB_configuration["actions"][GLB_configuration["media-video"]["action"]]
   result=runAction(item,"video "+pathFile)
   if result is None:
     bot.send_message(message.chat.id,'Error: Exception executing {0}'.format(key))
     bot.reply_to(message, "Ignoring this request.")
   else:
     sendActionResult(message.chat.id,item,result)    

  except Exception as e:
    e = sys.exc_info()[0]
    helper.internalLogger.critical('Error in processVideoMessage')
    helper.einternalLogger.exception(e)  


'''----------------------------------------------------------'''
'''----------------       M A I N         -------------------'''
'''----------------------------------------------------------'''

def main(configfile):
  print('telegramBOT-start -----------------------------')

  # Loading config file,
  # Default values
  cfg_log_debugs="telegramBOT.log"
  cfg_log_exceptions="telegramBOTe.log"

  global GLB_configuration
  # Let's fetch data
  GLB_configuration={}
  with open(configfile) as json_data:
      GLB_configuration = json.load(json_data)
  #Get log names
  if "log" in GLB_configuration:
      if "logTraces" in GLB_configuration["log"]:
        cfg_log_debugs = GLB_configuration["log"]["logTraces"]
      if "logExceptions" in GLB_configuration["log"]:
        cfg_log_exceptions = GLB_configuration["log"]["logExceptions"]
  helper.init(cfg_log_debugs,cfg_log_exceptions)

  print('See logs debugs in: {0} and exeptions in: {1}-----------'.format(cfg_log_debugs,cfg_log_exceptions))  
  helper.internalLogger.critical('telegramBOT-start -------------------------------')  
  helper.einternalLogger.critical('telegramBOT-start -------------------------------')


  try:
    #Create local path
    os.makedirs(GLB_configuration["media-photo"]["basePath"])
    os.makedirs(GLB_configuration["media-video"]["basePath"])
  except:
    pass


  recoverOngoingTasks()

  try:    
    logging.getLogger("requests").setLevel(logging.DEBUG)


    helper.internalLogger.debug("Calling telepot.Bot...")
    global bot
    pt=None
    bot = telebot.TeleBot(GLB_configuration["hash"])
    helper.internalLogger.debug("TeleBot returned")
    

    helper.internalLogger.debug("Starting restapi...")
    apiRestTask=threading.Thread(target=apirest_task,name="restapi")
    apiRestTask.daemon = True
    apiRestTask.start()

    helper.internalLogger.debug("Starting eventBootTask...")
    eventBootTask=threading.Thread(target=eventBoot_task,name="eventBOOT")
    eventBootTask.daemon = True
    eventBootTask.start()

    @bot.message_handler(content_types=['photo'])
    def photo(message):
      processPhotoMessage(message)

    @bot.message_handler(content_types=['video'])
    def video(message):
      processVideoMessage(message)

    @bot.message_handler(func=lambda message: True)
    def process_all(message):
      start=False
      stop=False
      msgFull=message.text.lower()
      msgList=msgFull.split()
      msg=msgList[0]
      if msg[0] == '/':
        msg=msg[1:]  #Trimming char /
          
      # Some built-ins options
      #-------------------------------------------------------------------
      #-------------------------------------------------------------------
      if "start" == msg:
        start=True
        if (len(msgList) == 1):
          bot.send_message(message.chat.id, "Adding you as a subscribers for all periodic actions and event")
          addSubscriber(message.chat.id,"periodic")
          addSubscriber(message.chat.id,"event")
        else:
          msg=msgList[1]
          if "event" == msg or "e" == msg:  #this is for event tasks
            if (len(msgList) == 2): 
              bot.send_message(message.chat.id, "Adding you as a subscribers for all events")
              addSubscriber(message.chat.id,"event")
            else: 
              addSubscriber(message.chat.id,"event",msgList[2])
          elif "periodic" == msg or "p" == msg:  #this is for periodic tasks
            if (len(msgList) == 2): 
              bot.send_message(message.chat.id, "Adding you as a subscribers for all periodic tasks")
              addSubscriber(message.chat.id,"periodic")
            else: 
              addSubscriber(message.chat.id,"periodic",msgList[2])
          else:
             bot.send_message(message.chat.id, "Error, after start you must specify periodic or event [name]")
          return

      #-------------------------------------------------------------------
      #-------------------------------------------------------------------
      if "stop" in msg:
        if (len(msgList) == 1):
          bot.send_message(message.chat.id, "Deleting you as a subscribers for all periodic actions")
          delSubscriber(message.chat.id,"periodic")
          delSubscriber(message.chat.id,"event")
        else:
          msg=msgList[1]
          if "event" == msg or "e" == msg:  #this is for event tasks
            if (len(msgList) == 2): 
              bot.send_message(message.chat.id, "Deleting you as a subscribers for all events")
              delSubscriber(message.chat.id,"event")
            else:
              delSubscriber(message.chat.id,"event",msgList[2])
          elif "periodic" == msg or "p" == msg:  #this is for periodic tasks
            if (len(msgList) == 2): 
              bot.send_message(message.chat.id, "Deleting you as a subscribers for all periodic tasks")
              delSubscriber(message.chat.id,"periodic")
            else:
              delSubscriber(message.chat.id,"periodic",msgList[2])
          else:
            bot.send_message(message.chat.id, "Error, after stop you must specify periodic or event [name]") 
          return


      if "help" in msg or "helphidden" in msg:

        options="On demand menu actions:"
        options=options+"\n-----------------------"
        for key,item in GLB_configuration["actions"].items():
          if ( (not "hidden" in item)  or  ("hidden" in item and item["hidden"] == False)) or ("helphidden" in msg):
            if key in GLB_configuration["menu"]:
              options=options+'\n  '+key

        options=options+'\n'"start/stop periodic [name] or all:"
        options=options+"\n------------------------------------"
        for item in GLB_configuration["periodic"]:
          if ( (not "hidden" in item)  or  ("hidden" in item and item["hidden"] == False)) or ("helphidden" in msg):
            options=options+'\n'"  " + item["action"]+ ". Each " + str(item["interval"]) + "(s)"
            if "start" in item:
              options=options+ ". Since " + item["start"]

        options=options+'\n'"start/stop event [name] or all:"
        options=options+"\n------------------------------------"
        for item in GLB_configuration["event"]:
          if ( (not "hidden" in item)  or  ("hidden" in item and item["hidden"] == False)) or ("helphidden" in msg):
            options=options+'\n'"  " + item["name"]
            if "action" in item:
                options=options+ "  " + item["action"]

        bot.send_message(message.chat.id,options)

      else:
        # Custom by configuration options
        for key,item in GLB_configuration["actions"].items():
          if key in GLB_configuration["menu"]:
            #helper.internalLogger.debug("Checking key '{0}' and msg {1}".format(key,msg))
            if msg == key.lower():
              helper.internalLogger.debug("Command '{0}' executing...".format(key))
              result=runAction(item,message.text)  
              if result is None:
                   bot.send_message(message.chat.id,'Error: Exception executing {0}'.format(key))
              else:
                  sendActionResult(message.chat.id,item,result)    
              return
        bot.reply_to(message, "Ignoring this request.")


    global _FINISHTASKS
    helper.internalLogger.debug("TeleBot periodic starting...")
    pt = threading.Thread(target=periodicTasks)
    pt.start()
    helper.internalLogger.debug("TeleBot periodic started")


    helper.internalLogger.debug("Polling...")
    tout=20
    if "pollingTimeout" in GLB_configuration:
      tout=GLB_configuration["pollingTimeout"] 
    bot.polling(none_stop=True,timeout=tout)
 
  except Exception as e:
    e = sys.exc_info()[0]
    helper.internalLogger.critical('Error: Exception unprocessed properly. Exiting')
    helper.einternalLogger.exception(e)  
    print('telegramBOT-General exeception captured. See log:{0}',format(cfg_log_exceptions))   
    _FINISHTASKS = True
    if not pt==None:
      pt.join()
    loggingEnd()


def eventBoot_task():
  helper.internalLogger.debug("Event boot task starting...")
  time.sleep(3)  #let's wait a bit to let startup ok
  if "eventBOOT" in GLB_configuration:
    helper.internalLogger.debug("Triggering event ...")
    for i in GLB_configuration["eventBOOT"]:
      eventTask(i)

  helper.internalLogger.debug("Boot task DONE")

'''----------------------------------------------------------'''
'''----------------     apirest_task      -------------------'''
def apirest_task():

  api.run(debug=True, use_reloader=False,port=GLB_configuration["port"],host=GLB_configuration["host"])


'''----------------------------------------------------------'''
'''----------------       loggingEnd      -------------------'''
def loggingEnd():      
  helper.internalLogger.critical('telegramBOT-end -----------------------------')        
  print('telegramBOT-end -----------------------------')


'''----------------------------------------------------------'''
'''----------------     parse_args        -------------------'''
def parse_args():
    """Parse the args."""
    parser = argparse.ArgumentParser(
        description='Simple dht tracker')
    parser.add_argument('--configfile', type=str, required=False,
                        default='/etc/telegramBOT.conf',
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

