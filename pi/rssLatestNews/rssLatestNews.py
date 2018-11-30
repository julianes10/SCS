#!/usr/bin/env python

# Custom adaptations
from __future__ import print_function

import argparse
import os.path
import json
import time
import sys
import subprocess
import os
import platform
import helper

from helper import *

from collections import OrderedDict


'''----------------------------------------------------------'''
'''----------------    playSound            -----------------'''

def playSound(item,bg=False):
   try:
      p=subprocess.Popen(['aplay',configuration["audios"][item]])
      if not bg:
        p.wait()     
      helper.internalLogger.debug("OK processing audio file for {0} item".format(item))
   except Exception as e:
      helper.internalLogger.warning("Error processing audio file for {0} item".format(item))
      helper.einternalLogger.exception(e)     
   return None
   

'''----------------------------------------------------------'''
'''----------------    getParam             -----------------'''
def getParam(param,mainLevel,currentLevel):
  pass


'''----------------------------------------------------------'''
'''----------------       M A I N         -------------------'''
'''----------------------------------------------------------'''

def main(configfile):
  global configuration

  # Loading config file,
  # Default values
  cfg_log_traces="ipaem.log"
  cfg_log_exceptions="ipaeme.log"
  # Let's fetch data
  with open(configfile) as json_data:
      configuration = json.load(json_data, object_pairs_hook=OrderedDict)
  #Get log names
  if "log" in configuration:
      if "logTraces" in configuration["log"]:
        cfg_log_traces = configuration["log"]["logTraces"]
      if "logExceptions" in configuration["log"]:
        cfg_log_exceptions = configuration["log"]["logExceptions"]
  helper.init(cfg_log_traces,cfg_log_exceptions)
  helper.internalLogger.debug('See logs traces in: {0} and exeptions in: {1}-----------'.format(cfg_log_traces,cfg_log_exceptions))  
  helper.internalLogger.critical('rss-------------------------------')  
  helper.einternalLogger.critical('rss-------------------------------')
  try:
      cfg_Actions = configuration["LocalActions"]
      helper.internalLogger.debug("Local actions {0}...".format(cfg_Actions))
  except Exception as e:
      helper.internalLogger.critical("Error processing configuration json {0} file. No action".format(configfile))
      helper.einternalLogger.exception(e)
      loggingEnd()
      return 0

  try:
      
      print('speech :{0}'.format(configuration["LocalActions"]["Rss2speech"]["nextLevel"]))
      feedList=configuration["LocalActions"]["Rss2speech"]["nextLevel"]
      for key,item in feedList.items():
        helper.internalLogger.debug("Processing {0}...".format(key,item))
        if "input" not in item:
          continue
        for key2,item2 in item.items():
          if "arg1" not in item2:
            pass
          print("key2: {0} item2 {1}".format(key2,item2))       

  except Exception as e:
    e = sys.exc_info()[0]
    helper.internalLogger.critical('Error: Exception unprocessed properly. Exiting')
    helper.einternalLogger.exception(e)  
    helper.internalLogger.debug('IPAEM-General exeception captured. See ssms.log:{0}',format(cfg_log_exceptions))        
    loggingEnd()



'''----------------------------------------------------------'''
'''----------------       loggingEnd      -------------------'''
def loggingEnd():      
  helper.internalLogger.critical('IPAEM-end -----------------------------')        
  print('IPAEM-end -----------------------------')

   
'''----------------------------------------------------------'''
'''----------------     parse_args        -------------------'''
def parse_args():
    """Parse the args."""
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawTextHelpFormatter)
    parser = argparse.ArgumentParser(
        description='Intelligent Personal Assistant EM')
    parser.add_argument('--configfile', type=str, required=False,
                        default='/etc/ipaem/ipaem.conf',
                        help='Config file for ipaem service')
    return parser.parse_args()

'''----------------------------------------------------------'''
'''----------------    helper.internalLogger.debugPlatformInfo  -------------------'''
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
