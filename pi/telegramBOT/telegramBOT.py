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

_FINISHTASKS=False


'''----------------------------------------------------------'''
'''----------------      API REST         -------------------'''
'''----------------------------------------------------------'''
api = Flask("api",template_folder="templates",static_folder='static')


'''----------------------------------------------------------'''
@api.route('/api/v1.0/telegramBOT/action', methods=['POST'])
def post_telegram_action():
    if not request.json:
        helper.internalLogger.debug("It is not a json. Back with error")
        abort(400)
    return requestNewAction(request.json)


def requestNewAction(req):
    rt=jsonify({'result': 'OK'})

    if not "action" in req:
        rt=jsonify({'result': 'KO'})
    else:
      helper.internalLogger.debug("NEW timelapse is requested. Autocanceling current one if any")
      if "name" in ongoing:
        cleanUpOngoing(ongoing["name"],True,True)
        helper.internalLogger.debug("DELETING existing ones with same name if any")
        purgeProject(ongoing["name"])
      ongoing.clear()
      ongoing["name"]=req["name"]
      ongoing["interval"]=int(req["interval"])
      if "maxTime" in req:
       if req["maxTime"] != "": 
        ongoing["maxTime"]=int(req["maxTime"])
      if "maxNbrOfPictures" in req:
       if req["maxNbrOfPictures"] != "":
        ongoing["maxNbrOfPictures"]=int(req["maxNbrOfPictures"])
      ongoing["status"]="ONGOING"
      cleanUpOngoing(ongoing["name"],True,True)
    UNLOCK(ongoing) 
    return rt

'''----------------------------------------------------------'''
@api.route('/',methods=["GET", "POST"])
@api.route('/telegramBOT/',methods=["GET", "POST"])
def telegramBOT_home():
    if request.method == 'POST':
      helper.internalLogger.debug("Processing new request from a form...{0}".format(request.form))
      form2 = request.form.to_dict()
      helper.internalLogger.debug("Processing new request from a form2...{0}".format(form2))   
      requestNewAction(form2)
    
    url={}

    st={} # getStatus()
    rt=render_template('index.html', title="TelegramBOT Site",status=st)
    return rt

'''----------------------------------------------------------'''
@api.route('/api/v1.0/telegramBOT/status', methods=['GET'])
def get_telegramBOT_status():
    return json.dumps(getStatus())

def getStatus():
    ongoing=LOCK()
    UNLOCK(ongoing)
    return rt

'''----------------------------------------------------------'''
'''----------------       periodic tasks  -------------------'''
'''----------------------------------------------------------'''

def periodicTasks():

  global bot
  global chatidList
  helper.internalLogger.debug("TeleBot periodic start")
  while not _FINISHTASKS:
    for key,item in GLB_configuration["periodic-static-actions"].items():
        time.sleep(1)
        ''' 
        # TODO check if it is time to execute this action item.interval 
        # TODO runAction     result=runAction(item,message.text)  
        TODO send to subscribers or force broadcast

        # iterate tasks, run commands if applied and send to peers subscribed.
        helper.internalLogger.debug("TeleBot periodic")
        if len(chatidList)>0:
          for i in chatidList:
            runAction(i,GLB_configuration["actions"][GLB_configuration["periodic-static-actions"]   ["default"]["action"]])
          time.sleep(GLB_configuration["periodic-static-actions"]["default"]["interval"])
  
              if result is None:
                   bot.send_message(message.chat.id,'Error: Exception executing {0}'.format(key))
              else:
                  sendActionResult(message.chat.id,item,result)    
              return     
          bot.reply_to(message, "Ignoring this request.")
        '''


  


'''----------------------------------------------------------'''
'''----------------    runAction            -----------------'''

def runAction(action,originalMsg):
  rt=None
  try:

    cmd=action["cmd"]
    if "TELEGRAM_COMMAND" in action["cmd"]:
        helper.internalLogger.debug("Custom cmd with TELEGRAM_COMMAND {0}'".format(cmd)) 
        msgSplitted=originalMsg.split()     
        cmd=action["cmd"].replace("TELEGRAM_COMMAND",' '.join(msgSplitted[1:]))
  
    global bot
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
        if os.path.isfile(action["video"]):
          f = open(action["video"], 'rb')
          bot.send_video(chatid,f)    
          f.close()  
          feedback=True
        else: 
          bot.send_message(chatid,"No video available, sorry")
      if "image" in action:
        helper.internalLogger.debug("Action with image")
        if os.path.isfile(action["image"]):
          helper.internalLogger.debug("File: {0}".format(action["image"]))
          f = open(action["image"], 'rb')
          bot.send_photo(chatid, f)
          f.close()
          feedback=True
        else: 
          bot.send_message(chatid,"No image available, sorry")
      if "text" in action:
        if os.path.isfile(action["text"]):
          f = open(action["text"], 'r')
          t = f.read()
          bot.send_message(chatid,t)
          f.close()        
          feedback=True
        else:
          bot.send_message(chatid,"No text available, sorry")
      if len(result)>0:
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
  
  return rt

'''----------------------------------------------------------'''
def UNLOCK(data):
  with open(GLB_configuration["ongoingDB"], 'w') as fp:
    json.dump(data, fp)

  p=GLB_configuration["ongoingDB"]+".lock"
  if os.path.exists(p):
    os.remove(p)

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
  UNLOCK({}) # cleanup


  try:    
    logging.getLogger("requests").setLevel(logging.DEBUG)

    helper.internalLogger.debug("Starting restapi...")
 
    apiRestTask=threading.Thread(target=apirest_task,name="restapi")
    apiRestTask.daemon = True
    apiRestTask.start()



    helper.internalLogger.debug("Calling telepot.Bot...")
    global bot
    global chatidList
    pt=None
    chatidList=[]
    bot = telebot.TeleBot(GLB_configuration["hash"])
    helper.internalLogger.debug("TeleBot returned")

    
    @bot.message_handler(func=lambda message: True)
    def process_all(message):
      global chatidList
      msgFull=message.text.lower()
      msgList=msgFull.split()
      msg=msgList[0]
      # Some built-ins options
      if "start" in msg:
        if message.chat.id in chatidList:
          bot.send_message(message.chat.id, "Hello my friend, BOT was already started for you")
        else:
          chatidList.append(message.chat.id)
          bot.send_message(message.chat.id, "Hello my friend, BOT is starting for you")
      elif "stop" in msg:
        if message.chat.id in chatidList:
          chatidList.remove(message.chat.id)
        bot.send_message(message.chat.id, "That's all folk, see you later")
      elif "help" in msg:
        options="Menu options:"
        for key,item in GLB_configuration["actions"].items():
          if (not "hidden" in item)  or  ("hidden" in item and item["hidden"] == False):
            if key in GLB_configuration["menu"]:
              options=options+'\n'+key
        bot.send_message(message.chat.id, options)
      else:
        # Custom by configuration options
        for key,item in GLB_configuration["actions"].items():
          if key in GLB_configuration["menu"]:
            helper.internalLogger.debug("Checking key '{0}' and msg {1}".format(key,msg))
            if msg == key.lower():
              helper.internalLogger.debug("Command '{0}' executed".format(key))
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

