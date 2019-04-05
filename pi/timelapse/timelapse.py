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

  global GLB_configuration 
  p=GLB_configuration["ongoingDB"]+".lock"
  if os.path.exists(p):
    os.remove(p)

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
    ongoing=LOCK()
    rt={}
    rt['projects']=GLB_projects      
    rt['ongoing']=ongoing       

    rt['disk']={'totalFree': 0,'projects':0,'ongoing':0}
    rt['disk']['projects']=getDirSize(GLB_configuration["mediaPath"])
    rt['disk']['totalFree']=getFreeDiskSize(GLB_configuration["mediaPath"])
 
    if "name" in ongoing:
      rt['disk']['ongoing']=getDirSize(GLB_configuration["mediaPath"]+"/"+ongoing["name"])    


    rtjson=json.dumps(rt)
    UNLOCK(ongoing)
    return rtjson

@api.route('/api/v1.0/timelapse/ongoing/new', methods=['POST'])
def post_timelapse_ongoing():
    rt=jsonify({'result': 'OK'})
    if not request.json:
        abort(400)
        return
    ongoing=LOCK() 
    if not "name" in request.json:
        rt=jsonify({'result': 'KO'})
    else:

      helper.internalLogger.debug("NEW timelapse is requested. Autocanceling current one if any")
      if "name" in ongoing:
        cleanUpOngoing(ongoing["name"],True,True)
        helper.internalLogger.debug("DELETING existing ones with same name if any")
        purgeProject(ongoing["name"])
      ongoing=request.json
      cleanUpOngoing(ongoing["name"],True,True)

    UNLOCK(ongoing)
    return rt


@api.route('/api/v1.0/timelapse/ongoing/stop', methods=['GET'])
def stop_timelapse_ongoing():
    rt=jsonify({'result': 'OK'})
    ongoing=LOCK() 
    if "name" in ongoing:
      helper.internalLogger.debug("REST Generating video and cleaning...")
      generateVideo(ongoing,True,True)
    UNLOCK(ongoing)
    return rt

@api.route('/api/v1.0/timelapse/ongoing/cancel', methods=['GET'])
def cancel_timelapse_ongoing():
    rt=jsonify({'result': 'OK'})
    ongoing=LOCK() 
    if "name" in ongoing:
      helper.internalLogger.debug("REST Cancelling video...")
      cleanUpOngoing(ongoing["name"],True,True)
      ongoing.clear()
    UNLOCK(ongoing)
    return rt

@api.route('/api/v1.0/timelapse/ongoing/peek', methods=['GET'])
def peek_timelapse_ongoing():
    rt=jsonify({'result': 'OK'})    
    ongoing=LOCK() 
    if "name" in ongoing:
      helper.internalLogger.debug("REST generating video sample so far...")
      generateVideo(ongoing,False,False)
    UNLOCK(ongoing)
    return rt




'''----------------------------------------------------------'''
'''--------    purgeProject                -----------------'''
'''----------------------------------------------------------'''
def purgeProject(name):
  global GLB_projects 

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
    if "name" in c:
      helper.internalLogger.debug("Checking status of project {0}:{1}".format(c['name'],c['status']))
      if c["name"] == name:
        helper.internalLogger.debug("Removing project {0}:{1}".format(c['name'],c['status']))
        GLB_projects.remove(c)

  with open(GLB_configuration["projectDB"], 'w') as fp:
    json.dump(GLB_projects, fp)



'''----------------------------------------------------------'''
'''--------    updateProjectsWithOngoing    -----------------'''
'''----------------------------------------------------------'''
def updateProjectsWithOngoing(ongoing):
  global GLB_projects 


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

  helper.internalLogger.debug("Adding project {0}:{1}".format(ongoing['name'],ongoing['status']))
  GLB_projects.append(ongoing)

  with open(GLB_configuration["projectDB"], 'w') as fp:
    json.dump(GLB_projects, fp)


'''----------------------------------------------------------'''
'''----------------       cleanUp         -------------------'''
'''----------------------------------------------------------'''
def cleanUpOngoing(name,pictures,video):

  helper.internalLogger.debug("CLEAN UP ONGOING {0} - pictures: {1}, video: {2}".format(name,pictures,video))

  if pictures and video:
    pathOngoing=GLB_configuration["mediaPath"]+"/"+name
    if os.path.isdir(pathOngoing):
      shutil.rmtree(pathOngoing)
    return
    
  if pictures:
    pathPictures=GLB_configuration["mediaPath"]+"/"+name+"/pictures"
    if os.path.isdir(pathPictures):
      shutil.rmtree(pathPictures)

  if video:
    pathVideo=GLB_configuration["mediaPath"]+"/"+name+"/video"
    if os.path.isdir(pathVideo):
      shutil.rmtree(pathVideo)

'''----------------------------------------------------------'''
'''----------------       generateVideo    -------------------'''
'''----------------------------------------------------------'''
def generateVideo(ongoing,cleanUp,closeOngoing):

  pathPictures =GLB_configuration["mediaPath"]+"/"+ongoing["name"]+"/pictures"
  pathVideo=GLB_configuration["mediaPath"]+"/"+ongoing["name"]+"/video"
  pathFileVideo=pathVideo + "/"+ongoing["name"]+".avi"

  if not closeOngoing:
    pathFileVideo=pathFileVideo+".part"

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


  if cleanUp:
    if "name" in ongoing:
      cleanUpOngoing(ongoing["name"],True,False)

  if closeOngoing:
    ongoing["status"]="DONE"
    ongoing["video"]=pathFileVideo
    updateProjectsWithOngoing(ongoing)
    ongoing.clear()
  else:
    updateProjectsWithOngoing(ongoing)




'''----------------------------------------------------------'''
'''----------------       updateOngoing   -------------------'''
'''----------------------------------------------------------'''
def updateOngoing(ongoing):

  helper.internalLogger.debug("updateOngoing: {0}".format(ongoing))
  if not "interval" in ongoing:
    return False
  
  now=time.time()

  if not  "firstPictureTime" in ongoing:
    ongoing["firstPictureTime"] = now
    ongoing["lastPictureTime"]  = 0
    ongoing["nbrOfPictures"] = 0


  if  (ongoing["firstPictureTime"] == now
      or ongoing["lastPictureTime"] + ongoing["interval"] > now):  
     return False

  #if still here, it's time to take a picture
  ongoing["lastPictureTime"]=now
  ongoing["nbrOfPictures"]=ongoing["nbrOfPictures"]+1
  path=GLB_configuration["mediaPath"]+"/"+ongoing["name"]+"/pictures"
  pathfile=path+"/"+ongoing["name"]+"."+str(now)+".jpg"
  try:
        os.makedirs(path)
  except FileExistsError:
        # directory already exists
        pass

  helper.internalLogger.debug("Ongoing {0}, taking photo:{1}".format(ongoing["name"],pathfile))
  cmd=GLB_configuration["takePhotoCmd"].replace("PARAMETER_OUTFILE",pathfile)
  subprocess.call(['bash','-c',cmd])


  # It may terminate by date or number of pictures
  if "maxNbrOfPictures" in ongoing:
    if ongoing["nbrOfPictures"] >= ongoing["maxNbrOfPictures"]:
      helper.internalLogger.debug("Generating video, max nbr of picture reached {0}:".format(ongoing["maxNbrOfPictures"]))
      generateVideo(ongoing,True,True)
      return

  if "maxTime" in ongoing:
    if ongoing["firstPictureTime"] + ongoing["maxTime"] >= now:
      helper.internalLogger.debug("Generating video, max time timelapsing reached {0}:".format(ongoing["maxTime"]))
      generateVideo(ongoing,True,True)
      return



'''----------------------------------------------------------'''
'''----------------       M A I N         -------------------'''
'''----------------------------------------------------------'''

def main(configfile):
  print('timelapse-start -----------------------------')

  # Loading config file,
  # Default values
  cfg_log_traces="timelapse.log"
  cfg_log_exceptions="timelapsee.log"


  global GLB_configuration

  global GLB_projects


  GLB_projects=[]


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
  UNLOCK({}) # cleanup
  try:
        os.makedirs(GLB_configuration["mediaPath"])
  except FileExistsError:
        # directory already exists
        pass


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
       #helper.internalLogger.critical("Polling")
       d=LOCK()
       updateOngoing(d)
       UNLOCK(d)
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

