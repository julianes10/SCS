#!/usr/bin/env python
import argparse
import time
import datetime
import sys
import json
import subprocess
import os
import platform
import threading
import helper
from random import randint

#Code copy and adapted from https://github.com/adafruit/Adafruit_Python_DHT/blob/master/examples/simpletest.py


from flask import Flask, jsonify,abort,make_response,request, url_for

from helper import *


configuration={}

'''----------------------------------------------------------'''
'''----------------      API REST         -------------------'''
'''----------------------------------------------------------'''
api = Flask("api")


@api.route('/api/v1.0/dht/status', methods=['GET'])
def get_dht_status():
    if True:
      helper.internalLogger.debug("status required")
      rt=jsonify({'result': 'OK'})
    else:
      helper.internalLogger.debug("ce test ignored")
    return rt

@api.route('/api/v1.0/dht/sensors/now', methods=['GET'])
def get_dht_sensors_now():
    helper.internalLogger.debug("now sensors data required")
    info=[]

    for x in dhtList:
        helper.internalLogger.debug('Reading DHT "{0}" on pin "{1}"...'.format(x["name"],x["pin"]))
        h, t = getSensorData(x["pin"], x["model"] ) 
        if h is not None and t is not None:
          info.append({'name': x["name"],'temperature':t,'humidity':h})
        else:
          helper.internalLogger.debug('Error reading DHT "{0}" on pin "{1}"...'.format(x["name"],x["pin"]))

    return json.dumps(info)

@api.route('/api/v1.0/dht/sensors/latest', methods=['GET'])
def get_dht_sensors_latest():
    helper.internalLogger.debug("latest cached sensors data required")
    return json.dumps(latestCached)


'''----------------------------------------------------------'''
'''----------------       getSensorData   -------------------'''
def getSensorData(pin,model=22):

   if amIaPi():
      import Adafruit_DHT
      if model == 11:  
        sensor = Adafruit_DHT.DHT11
      else:
        sensor = Adafruit_DHT.DHT22
      humidity, temperature = Adafruit_DHT.read_retry(sensor, pin)
   else:
      humidity=randint(0, 200)/2.0
      temperature=randint(-10, 100)/2.0
   return (humidity,temperature)

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

    if  args.scan:
     for x in range(1, 41):
      print('Scanning DHT 22 PIN {0}...'.format(x))
      h,t = getSensorData(x) 
      if h is not None and t is not None:
        print('  PIN {0} Temp={1:0.1f} Celsius  Humidity={2:0.1f}%'.format(x,t,h))
      else:
        print('  Failed to get DHT data')
      print('Scanning DHT 11 PIN {0}...'.format(x))

      h,t = getSensorData(x,11) 
      if h is not None and t is not None:
        print('  PIN {0} Temp={1:0.1f} Celsius  Humidity={2:0.1f}%'.format(x,t,h))
      else:
        print('  Failed to get DHT data')

     loggingEnd()
     return

    #Get log names
    global dhtList
    dhtList=configuration["DHT"];


    
    apiRestTask=threading.Thread(target=apirest_task,name="restapi")
    apiRestTask.daemon = True
    apiRestTask.start()


    global latestCached
    latestCached=[]

  except Exception as e:
    helper.internalLogger.critical("Error processing configuration json {0} file. Exiting".format(configfile))
    helper.einternalLogger.exception(e)
    loggingEnd()
    return  

  try:    
     import time
     ts = time.time()
     st = datetime.datetime.fromtimestamp(ts).strftime('%d-%m-%Y %H:%M:%S')
     for x in dhtList:
        helper.internalLogger.debug('Truncating file {0}... '.format(x["output"]))
        with open(x["output"]+".t", "w") as myfile:
          myfile.write("Temperature " + x["name"] + " From " + st + " " + str(ts) + "\n")      
          myfile.close()
        with open(x["output"]+".h", "w") as myfile:
          myfile.write("Humidity " + x["name"] + " From " + st + " " + str(ts) + "\n")      
          myfile.close()
     while True:
      for x in dhtList:
        helper.internalLogger.debug('Reading DHT "{0}" on pin "{1}"...'.format(x["name"],x["pin"]))
        h, t = getSensorData(x["pin"],x["model"]) 
        if h is not None and t is not None:

         with open(x["output"]+".t", "a") as myfile:
          myfile.write(str(round(t,1))+" ")      
          myfile.close()
         with open(x["output"]+".h", "a") as myfile:
          myfile.write(str(round(h,1))+" ")      
          myfile.close()
        latestCached.append({'name': x["name"],'temperature':t,'humidity':h})
        time.sleep(configuration["interval"]) 


  except Exception as e:
    e = sys.exc_info()[0]
    helper.internalLogger.critical('Error: Exception unprocessed properly. Exiting')
    helper.einternalLogger.exception(e)  
    print('SIMPLEDHTTRACKER-General exeception captured. See log:{0}',format(cfg_log_exceptions))        
    loggingEnd()

'''----------------------------------------------------------'''
'''----------------     apirest_task      -------------------'''
def apirest_task():
  api.run(debug=True, use_reloader=False,port=5056,host='0.0.0.0')


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
    parser.add_argument('--scan', action='store_true',
                        help='Scan GPIOs trying discover DHTs')
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


