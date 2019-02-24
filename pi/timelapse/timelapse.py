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
def getDirSize(start_path = '.'):
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(start_path):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            total_size += os.path.getsize(fp)
    return total_size

def getFreeDiskSize(path = '.'):
    rt = 0
    statvfs = os.statvfs(path)
    #statvfs.f_frsize * statvfs.f_blocks     # Size of filesystem in bytes
    #rt=statvfs.f_frsize * statvfs.f_bfree      # Actual number of free bytes
    rt=statvfs.f_frsize * statvfs.f_bavail     # Number of free bytes that ordinary users
    return rt

'''----------------------------------------------------------'''
'''----------------      API REST         -------------------'''
'''----------------------------------------------------------'''
api = Flask("api")


@api.route('/api/v1.0/timelapse/status', methods=['GET'])
def get_timelapse_status():
    rt={}
    rt['projects']=GLB_projects      
    rt['ongoing']=GLB_ongoing       

    rt['disk']={'totalFree': 0,'projects':0,'ongoing':0}
    rt['disk']['projects']=getDirSize(GLB_configuration["mediaPath"])
    rt['disk']['totalFree']=getFreeDiskSize(GLB_configuration["mediaPath"])
 
    if "name" in GLB_ongoing:
      rt['disk']['ongoing']=getDirSize(GLB_configuration["mediaPath"]+"/"+GLB_ongoing["name"])
      


    rtjson=json.dumps(rt)
    return rtjson

@api.route('/api/v1.0/timelapse/project', methods=['POST'])
def post_timelapse_tracker():
    rt=jsonify({'result': 'OK'})
    if not request.json: 
        abort(400)
    abort(400)
'''
    if "auto-tracker" in GLB_configuration:
      if "what" in GLB_configuration["auto-tracker"]:
        with open(GLB_configuration["auto-tracker"]["what"], 'w') as outfile:
          json.dump(request.json, outfile)
          return rt, 201
'''


'''----------------------------------------------------------'''
'''--------    updateProjectsWithOngoing    -----------------'''
'''----------------------------------------------------------'''
def updateProjectsWithOngoing():
  global GLB_projects 
  global GLB_ongoing 

  try:
    if "projectDB" in GLB_configuration:
      with open(GLB_configuration["projectDB"]) as json_data:
        GLB_projects = json.load(json_data)
    else:
      helper.internalLogger.debug("No GLB_projects DB found...")
      GLB_projects=[]

  except Exception as e:
    helper.internalLogger.critical("Error processing GLB_configuration json {0} file. Trunking file".format(GLB_configuration["projectDB"]))
    helper.einternalLogger.exception(e)
    GLB_projects=[]
    

  #clean up other ongoing temps.
  for c in GLB_projects:
    if "status" in c and "name" in c:
      helper.internalLogger.debug("Checking status of project {0}:{1}".format(c['name'],c['status']))
      if c["status"] == "ONGOING":
        helper.internalLogger.debug("Removing project {0}:{1}".format(c['name'],c['status']))
        GLB_projects.remove(c)

  helper.internalLogger.debug("Adding project {0}:{1}".format(GLB_ongoing['name'],GLB_ongoing['status']))
  GLB_projects.append(GLB_ongoing)

  with open(GLB_configuration["projectDB"], 'w') as fp:
    json.dump(GLB_projects, fp)


'''----------------------------------------------------------'''
'''----------------       generateVideo    -------------------'''
'''----------------------------------------------------------'''
def generateVideo(cleanUp,closeOngoing):
  global GLB_ongoing
  pathPictures =GLB_configuration["mediaPath"]+"/"+GLB_ongoing["name"]+"/pictures"
  pathVideo=GLB_configuration["mediaPath"]+"/"+GLB_ongoing["name"]+"/video"
  pathFileVideo=pathVideo + "/"+GLB_ongoing["name"]+".avi"

  try:
      os.makedirs(pathVideo)
  except FileExistsError:
      # directory already exists
      pass

  helper.internalLogger.debug("Project {0}, generating video:".format(pathFileVideo))
  cmd=GLB_configuration["createVideoCmd"].replace("PARAMETER_INPUTFOLDER",pathPictures)
  cmd=cmd.replace("PARAMETER_OUTFILE",pathFileVideo)
  helper.internalLogger.debug("Project {0}, generating video CMD:".format(cmd))
  subprocess.call(['bash','-c',cmd]) 

  if closeOngoing:
    GLB_ongoing["status"]="DONE"
    GLB_ongoing["video"]=pathFileVideo
    updateProjectsWithOngoing()
    GLB_ongoing={}
  else:
    # keep ongoing
    GLB_ongoing["video"]="PART."+pathFileVideo  
    updateProjectsWithOngoing()

  if cleanUp:
    shutil.rmtree(pathPictures) 


'''----------------------------------------------------------'''
'''----------------       updateOngoing   -------------------'''
'''----------------------------------------------------------'''
def updateOngoing():

  global GLB_ongoing
  #helper.internalLogger.critical("updateOngoing: {0}",format(GLB_ongoing.dumps()))
  if not "interval" in GLB_ongoing:
    return False

  now=time.time()

  if not  "firstPictureTime" in GLB_ongoing:
    GLB_ongoing["firstPictureTime"] = now
    GLB_ongoing["lastPictureTime"]  = 0
    GLB_ongoing["nbrOfPictures"] = 0


  if  (GLB_ongoing["firstPictureTime"] == now
      or GLB_ongoing["lastPictureTime"] + GLB_ongoing["interval"] > now):
    return False

  #if still here, it's time to take a picture
  GLB_ongoing["lastPictureTime"]=now
  GLB_ongoing["nbrOfPictures"]=GLB_ongoing["nbrOfPictures"]+1
  path=GLB_configuration["mediaPath"]+"/"+GLB_ongoing["name"]+"/pictures"
  pathfile=path+"/"+GLB_ongoing["name"]+"."+str(now)+".jpg"
  try:
        os.makedirs(path)
  except FileExistsError:
        # directory already exists
        pass

  helper.internalLogger.debug("Ongoing {0}, taking photo:{1}".format(GLB_ongoing["name"],pathfile))
  cmd=GLB_configuration["takePhotoCmd"].replace("PARAMETER_OUTFILE",pathfile)
  subprocess.call(['bash','-c',cmd])


  # It may terminate by date or number of pictures
  if "maxNbrOfPictures" in GLB_ongoing:
    if GLB_ongoing["nbrOfPictures"] >= GLB_ongoing["maxNbrOfPictures"]:
      helper.internalLogger.debug("Generating video, max nbr of picture reached {0}:".format(GLB_ongoing["maxNbrOfPictures"]))
      generateVideo(True,True)
      return

  if "maxTime" in GLB_ongoing:
    if GLB_ongoing["firstPictureTime"] + GLB_ongoing["maxTime"] >= now:
      helper.internalLogger.debug("Generating video, max time timelapsing reached {0}:".format(GLB_ongoing["maxTime"]))
      generateVideo(True,True)
      return

'''----------------------------------------------------------'''
'''----------------       updateProjects   -------------------'''
'''----------------------------------------------------------'''


'''----------------------------------------------------------'''
'''----------------      pollOngoing      -------------------'''
'''----------------------------------------------------------'''

def pollOngoing():

  global GLB_projects 
  global GLB_ongoing 

  global firstPolling

  if not any(GLB_ongoing) and firstPolling:
    firstPolling=False
    try:
      #NOTE: BELOW IS ONLY A HACK FOR TESTING WITHOUT REST POST
      if "ongoingDB" in GLB_configuration:
        with open(GLB_configuration["ongoingDB"]) as json_data:
          GLB_ongoing  = json.load(json_data)
      else:
        helper.internalLogger.debug("No ongoingDB found...")
        return

    except Exception as e:
      helper.internalLogger.critical("Error processing GLB_configuration json {0} file. Exiting".format(GLB_configuration["ongoingDB"]))
      helper.einternalLogger.exception(e)
      return 

  updateOngoing()


'''----------------------------------------------------------'''
'''----------------       M A I N         -------------------'''
'''----------------------------------------------------------'''

def main(configfile):
  print('timelapse-start -----------------------------')

  # Loading config file,
  # Default values
  cfg_log_traces="timelapse.log"
  cfg_log_exceptions="timelapsee.log"
  cfg_SensorsDirectory={}


  global GLB_configuration
  global GLB_ongoing
  global GLB_projects
  global firstPolling
 
  firstPolling=True

  GLB_projects=[]
  GLB_ongoing={}

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
  helper.internalLogger.critical('timelapse-start -------------------------------')  
  helper.einternalLogger.critical('timelapse-start -------------------------------')





  if "polling-interval" in GLB_configuration:
      pollingInterval=GLB_configuration["polling-interval"]


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
       helper.internalLogger.critical("Polling")
       pollOngoing()
       time.sleep(pollingInterval)


  except Exception as e:
    e = sys.exc_info()[0]
    helper.internalLogger.critical('Error: Exception unprocessed properly. Exiting')
    helper.einternalLogger.exception(e)  
    print('timelapse-General exeception captured. See log:{0}',format(cfg_log_exceptions))        
    loggingEnd()

'''----------------------------------------------------------'''
'''----------------     apirest_task      -------------------'''
def apirest_task():
  api.run(debug=True, use_reloader=False,port=GLB_configuration["port"],host=GLB_configuration["host"])


'''----------------------------------------------------------'''
'''----------------       loggingEnd      -------------------'''
def loggingEnd():      
  helper.internalLogger.critical('timelapse-end -----------------------------')        
  print('timelapse-end -----------------------------')


'''----------------------------------------------------------'''
'''----------------     parse_args        -------------------'''
def parse_args():
    """Parse the args."""
    parser = argparse.ArgumentParser(
        description='Simple dht tracker')
    parser.add_argument('--configfile', type=str, required=False,
                        default='/etc/timelapse.conf',
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

