#!/usr/bin/env python
import argparse
import time
import sys
import json
import subprocess
import os
import platform
import threading
import helper
#Code copy and adapted from https://github.com/adafruit/Adafruit_Python_DHT/blob/master/examples/simpletest.py


from helper import *


configuration={}



'''----------------------------------------------------------'''
'''----------------       M A I N         -------------------'''
'''----------------------------------------------------------'''

def main(configfile):
  print('SIMPLEDHTTRACKER-start -----------------------------')

  
  # Loading config file,
  # Default values
  cfg_log_traces="SIMPLEDHTTRACKER.log"
  cfg_log_exceptions="SIMPLEDHTTRACKERe.log"
  cfg_SensorsDirectory={}
  # Let's fetch data
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
  helper.internalLogger.critical('SIMPLEDHTTRACKER-start -------------------------------')  
  helper.einternalLogger.critical('SIMPLEDHTTRACKER-start -------------------------------')


  try:
    #Get log names
    dhtList=configuration["DHT"];

  except Exception as e:
    helper.internalLogger.critical("Error processing configuration json {0} file. Exiting".format(configfile))
    helper.einternalLogger.exception(e)
    loggingEnd()
    return  

  try:    

    if amIaPi():
      import Adafruit_DHT
    else:
      from random import randint
      helper.internalLogger.warning('Not in pi environment, simulating reading values from dht')
      
    while True:
      for x in dhtList:
        helper.internalLogger.debug('Reading DHT "{0}" on pin "{1}"...'.format(x["name"],x["pin"]))
        if amIaPi():
          sensor = Adafruit_DHT.DHT22
          pin = x["pin"]
          humidity, temperature = Adafruit_DHT.read_retry(sensor, pin)
        else:
          humidity=randint(0, 200)/2.0
          temperature=randint(-10, 100)/2.0

        if humidity is not None and temperature is not None:
          print('Temp={0:0.1f} Celsius  Humidity={1:0.1f}%'.format(temperature, humidity))
        else:
          print('Failed to get reading. Try again!')
      time.sleep(10) 

  except Exception as e:
    e = sys.exc_info()[0]
    helper.internalLogger.critical('Error: Exception unprocessed properly. Exiting')
    helper.einternalLogger.exception(e)  
    print('SIMPLEDHTTRACKER-General exeception captured. See log:{0}',format(cfg_log_exceptions))        
    loggingEnd()


'''----------------------------------------------------------'''
'''----------------       loggingEnd      -------------------'''
def loggingEnd():      
  helper.internalLogger.critical('SIMPLEDHTTRACKER-end -----------------------------')        
  print('SIMPLEDHTTRACKER-end -----------------------------')


'''----------------------------------------------------------'''
'''----------------     parse_args        -------------------'''
def parse_args():
    """Parse the args."""
    parser = argparse.ArgumentParser(
        description='Simple dht tracker')
    parser.add_argument('--configfile', type=str, required=False,
                        default='/etc/simpleDhtTracker.conf',
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


