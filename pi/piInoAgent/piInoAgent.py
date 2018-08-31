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

from helper import *
from serialWrapper import *

from flask import Flask, jsonify,abort,make_response,request, url_for

configuration={}


'''----------------------------------------------------------'''
'''----------------      API REST         -------------------'''
'''----------------------------------------------------------'''
api = Flask("api")


'''--------- LS LS LS LS LS LS ------------------------------ '''
@api.route('/api/v1.0/ls/status', methods=['GET'])
def get_status():
    arduinoSerial.sendStatus()
    arduinoSerial.flush()
    if True:
      helper.internalLogger.debug("lstest is requested")
      rt=jsonify({'result': 'OK'})
    else:
      helper.internalLogger.debug("lstest ignored")
    return rt


@api.route('/api/v1.0/ls/color', methods=['POST'])
def post_color():
    rt=jsonify({'result': 'OK'})
    if not request.json or not 'color' in request.json:
        abort(400)
    arduinoSerial.sendLSColor(request.json['color']) 
    arduinoSerial.flush()
    return rt, 201

@api.route('/api/v1.0/ls/mode', methods=['POST'])
def post_mode():
    rt=jsonify({'result': 'OK'})
    if not request.json or not 'mode' in request.json:
        abort(400)
    arduinoSerial.sendMode(request.json['mode']) 
    arduinoSerial.flush()
    return rt, 201

@api.route('/api/v1.0/ls/timeout', methods=['POST'])
def post_timemout():
    rt=jsonify({'result': 'OK'})
    if not request.json or not 'timeout' in request.json:
        abort(400)
    arduinoSerial.sendLSTimeout(request.json['timeout']) 
    arduinoSerial.flush()
    return rt, 201

@api.route('/api/v1.0/ls/pause', methods=['POST'])
def post_pause():
    rt=jsonify({'result': 'OK'})
    if not request.json or not 'pause' in request.json:
        abort(400)
    arduinoSerial.sendLSPause(request.json['pause']) 
    arduinoSerial.flush()
    return rt, 201

@api.route('/api/v1.0/ls/debug', methods=['POST'])
def post_debug():
    rt=jsonify({'result': 'OK'})
    if not request.json or not 'debug' in request.json:
        abort(400)
    arduinoSerial.sendDebug(request.json['debug']) 
    arduinoSerial.flush()
    return rt, 201

@api.route('/api/v1.0/ls/reset', methods=['POST'])
def post_reset():
    rt=jsonify({'result': 'OK'})
    if not request.json or not 'reset' in request.json:
        abort(400)
    arduinoSerial.sendReset() 
    arduinoSerial.flush()
    return rt, 201


@api.route('/api/v1.0/ls/misc', methods=['POST'])
def post_misc():
    rt=jsonify({'result': 'OK'})
    if not request.json:
        abort(400)
    if 'mode' in request.json:
      arduinoSerial.sendMode(request.json['mode']) 
    if 'color' in request.json:
      arduinoSerial.sendLSColor(request.json['color']) 
    if 'pause' in request.json:
      arduinoSerial.sendLSPause(request.json['pause']) 
    if 'timeout' in request.json:
      arduinoSerial.sendLSTimeout(request.json['timeout']) 
    if 'debug' in request.json:
      arduinoSerial.sendDebug(request.json['debug']) 
    if 'reset' in request.json:
      arduinoSerial.sendReset() 
    arduinoSerial.flush()
    return rt, 201

'''--------- CE CE CE CE CE CE ------------------------------ '''

@api.route('/api/v1.0/ce/mode', methods=['POST'])
def post_ce_mode():
    helper.internalLogger.debug("mode requested")

    rt=jsonify({'result': 'OK'})
    if not request.json or not 'mode' in request.json:
        helper.internalLogger.debug("DDDD: {0} ".format(request.json))   
        abort(400)
    arduinoSerial.sendMode(request.json['mode'],"E") 
    arduinoSerial.flush()
    return rt, 201

@api.route('/api/v1.0/ce/speed', methods=['POST'])
def post_ce_speed():
    rt=jsonify({'result': 'OK'})
    if not request.json:
        abort(400)
    if 'raw' in request.json:
      arduinoSerial.sendCE(request.json['raw']) 
    if 'value' in request.json:
      arduinoSerial.sendCESpeed(request.json['value']) 
    arduinoSerial.flush()
    return rt, 201

@api.route('/api/v1.0/ce/steeringWheel', methods=['POST'])
def post_ce_steeringWheel():
    rt=jsonify({'result': 'OK'})
    if not request.json:
        abort(400)
    if 'raw' in request.json:
      arduinoSerial.sendCE(request.json['raw']) 
    arduinoSerial.flush()
    return rt, 201

@api.route('/api/v1.0/ce/debug', methods=['POST'])
def post_ce_debug():
    rt=jsonify({'result': 'OK'})
    if not request.json or not 'debug' in request.json:
        abort(400)
    arduinoSerial.sendDebug(request.json['debug'],"E") 
    arduinoSerial.flush()
    return rt, 201

@api.route('/api/v1.0/ce/reset', methods=['POST'])
def post_ce_reset():
    rt=jsonify({'result': 'OK'})
    if not request.json or not 'reset' in request.json:
        abort(400)
    arduinoSerial.sendReset("E") 
    arduinoSerial.flush()
    return rt, 201

@api.route('/api/v1.0/ce/status', methods=['GET'])
def get_ce_status():
    arduinoSerial.sendStatus("E")
    arduinoSerial.flush()
    if True:
      helper.internalLogger.debug("ce test is requested")
      rt=jsonify({'result': 'OK'})
    else:
      helper.internalLogger.debug("ce test ignored")
    return rt


'''----------------------------------------------------------'''
'''----------------       M A I N         -------------------'''
'''----------------------------------------------------------'''

def main(configfile):
  print('PIINOAGENT-start -----------------------------')
  
  # Loading config file,
  # Default values
  cfg_log_traces="piinoagent.log"
  cfg_log_exceptions="piinoagente.log"
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
  helper.internalLogger.critical('PIINOAGENT-start -------------------------------')  
  helper.einternalLogger.critical('PIINOAGENT-start -------------------------------')
  try:
    pass
  except Exception as e:
    helper.internalLogger.critical("Error processing configuration json {0} file. Exiting".format(configfile))
    helper.einternalLogger.exception(e)
    loggingEnd()
    return  

  try:    

    apiRestTask=threading.Thread(target=apirest_task,name="restapi")
    apiRestTask.daemon = True
    apiRestTask.start()
   
    global arduinoSerial
    arduinoSerial=serialWrapper( configuration["arduino"]["port"],
                      configuration["arduino"]["speed"],
                      configuration["arduino"]["timeout"]);
   
    while True:
        cmd=arduinoSerial.readCommand()
        time.sleep(10) 

  except Exception as e:
    e = sys.exc_info()[0]
    helper.internalLogger.critical('Error: Exception unprocessed properly. Exiting')
    helper.einternalLogger.exception(e)  
    print('PIINOAGENT-General exeception captured. See ssms.log:{0}',format(cfg_log_exceptions))        
    loggingEnd()


'''----------------------------------------------------------'''
'''----------------       loggingEnd      -------------------'''
def loggingEnd():      
  helper.internalLogger.critical('PIINOAGENT-end -----------------------------')        
  print('PIINOAGENT-end -----------------------------')


'''----------------------------------------------------------'''
'''----------------     apirest_task      -------------------'''
def apirest_task():
  api.run(debug=True, use_reloader=False,port=5001,host='0.0.0.0')

'''----------------------------------------------------------'''
'''----------------     parse_args        -------------------'''
def parse_args():
    """Parse the args."""
    parser = argparse.ArgumentParser(
        description='Arduino SCS handler agent')
    parser.add_argument('--configfile', type=str, required=False,
                        default='/etc/piinoagent.conf',
                        help='Config file for piinoagent service')
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
