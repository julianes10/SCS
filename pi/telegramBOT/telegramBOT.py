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

_FINISHTASKS=False

'''----------------------------------------------------------'''
'''----------------       periodic tasks  -------------------'''
'''----------------------------------------------------------'''

def periodicTasks():
  #TODO custom periodict task and make sleep period smaller, interval by idlist
  global bot
  global chatidList
  helper.internalLogger.debug("TeleBot periodic start")
  while not _FINISHTASKS:
    helper.internalLogger.debug("TeleBot periodic")
    if len(chatidList)>0:
      for i in chatidList:
        runAction(i,GLB_configuration["actions"][GLB_configuration["periodic-static-actions"]["default"]["action"]])
    time.sleep(GLB_configuration["periodic-static-actions"]["default"]["interval"])



'''----------------------------------------------------------'''
'''----------------    runAction            -----------------'''

def runAction(chatid,action):
  try:
    cmd=action["cmd"]
    global bot
    result=subprocess.check_output(['bash','-c',cmd])
    helper.internalLogger.debug("Cmd {0}, result {1}".format(cmd,result))
  except Exception as e:
    e = sys.exc_info()[0]
    helper.internalLogger.critical('Error: Exception executing {0}'.format(action))
    helper.einternalLogger.exception(e)  
    bot.send_message(chatid,'Error: Exception executing {0}'.format(action))
    return

  helper.internalLogger.debug("Let's respond with associated info to action{0}".format(action))


  if "video" in action: 
    if os.path.isfile(action["video"]):
      f = open(action["video"], 'rb')
      bot.send_video(chatid,f)    
      f.close()  
  if "image" in action:
    helper.internalLogger.debug("Action with image")
    if os.path.isfile(action["image"]):
      helper.internalLogger.debug("File: {0}".format(action["image"]))
      f = open(action["image"], 'rb')
      bot.send_photo(chatid, f)
      f.close()
  if "text" in action:
    if os.path.isfile(action["text"]):
      f = open(action["text"], 'r')
      t = f.read()
      bot.send_message(chatid,t)
      f.close()        

  if len(result)>0:
    bot.send_message(chatid,result)
    helper.internalLogger.debug("Action: {0}".format(action))


  helper.internalLogger.debug("Action ended")

  ### TODO limpiar los ficheros??? no se, se carga multiusuario...

  return None
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
    logging.getLogger("requests").setLevel(logging.DEBUG)
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
      msg=message.text.lower()
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
      else:
        for key,item in GLB_configuration["actions"].items():
          if key in GLB_configuration["menu"]:
            if key in msg:
              helper.internalLogger.debug("Command '{0}' executed".format(key))
              runAction(message.chat.id,item)    
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

