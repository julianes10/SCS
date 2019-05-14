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
from flask import Flask, render_template,redirect


''' 
------------- ongoing fields
# input
    name - string  *** key
    interval - number
    maxTime  - seconds
    maxNbrOfPictures - number

# generated by code
    nbrOfPictures - number
    firstPictureTime - timestamp
    lastPictureTime - timestamp
    status  - string: ONGOING | DONE
    video - string


------------- projects fields

List of ongoing struct items.

'''



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
def getProjects():
  rt=[]
  try:
    if "projectDB" in GLB_configuration:
      with open(GLB_configuration["projectDB"]) as json_data:
        rt = json.load(json_data)
    else:
      helper.internalLogger.debug("No projects DB found...")
      rt=[]

  except Exception as e:
    helper.internalLogger.critical("Error processing GLB_configuration projectDB json {0} file. Trunking file".format(GLB_configuration["projectDB"]))
    helper.einternalLogger.exception(e)
    rt=[]
  
  return rt

def setProjects(projects):
  with open(GLB_configuration["projectDB"], 'w') as fp:
    json.dump(projects, fp)


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
'''----------------------------------------------------------'''

def format_videoURL(value):
    aux="unknown"
    try:
      aux=value[1:]
    except Exception as e:
      helper.internalLogger.critical("Error reading value date: {0}.".format(value))
      helper.einternalLogger.exception(e)
    return aux
'''----------------------------------------------------------'''
'''----------------      API REST         -------------------'''
'''----------------------------------------------------------'''
api = Flask("api",template_folder="templates",static_folder='static')
api.jinja_env.filters['datetime'] = format_datetime
api.jinja_env.filters['videoURL'] = format_videoURL

'''----------------------------------------------------------'''
@api.route('/api/v1.0/timelapse/status', methods=['GET'])
def get_timelapse_status():
    return json.dumps(getStatus())

def getStatus():
    ongoing=LOCK()
    rt={}
    rt['projects']=getProjects()      
    rt['ongoing']=ongoing       

    rt['disk']={'totalFree': 0,'projects':0,'ongoing':0}
    rt['disk']['projects']=getDirSize(GLB_configuration["mediaPath"])
    rt['disk']['totalFree']=getFreeDiskSize(GLB_configuration["mediaPath"])
 
    if "name" in ongoing:
      rt['disk']['ongoing']=getDirSize(GLB_configuration["mediaPath"]+"/"+ongoing["name"])    


    global GLB_latestManualShooted
    if  os.path.isfile(GLB_latestManualShooted):
      rt["latestPhoto"]=GLB_latestManualShooted
      rt["lastPictureTime"]=os.path.getmtime(GLB_latestManualShooted)


    UNLOCK(ongoing)
    return rt
'''----------------------------------------------------------'''
@api.route('/api/v1.0/timelapse/ongoing/new', methods=['POST'])
def post_timelapse_ongoing():
    if not request.json:
        helper.internalLogger.debug("It is not a json. Back with error")
        abort(400)
    return requestNewOngoing(request.json)


def requestNewOngoing(req):
    rt=jsonify({'result': 'OK'})
    ongoing=LOCK() 
    if not "name" in req:
        rt=jsonify({'result': 'KO'})
    else:
      #Just in case put numbers in numbers

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
@api.route('/api/v1.0/timelapse/ongoing/stop', methods=['GET'])
def stop_timelapse_ongoing():
    return stopOngoing()

def stopOngoing():
    rt=jsonify({'result': 'OK'})
    ongoing=LOCK() 
    if "name" in ongoing:
      helper.internalLogger.debug("REST Generating video and cleaning...")
      generateVideo(ongoing,True,True)
    UNLOCK(ongoing)
    return rt
'''----------------------------------------------------------'''
@api.route('/api/v1.0/timelapse/ongoing/cancel', methods=['GET'])
def cancel_timelapse_ongoing():
    return cancelOngoing()

def cancelOngoing():
    rt=jsonify({'result': 'OK'})
    ongoing=LOCK() 
    if "name" in ongoing:
      helper.internalLogger.debug("REST Cancelling video...")
      cleanUpOngoing(ongoing["name"],True,True)
      ongoing.clear()
    UNLOCK(ongoing)
    return rt
'''----------------------------------------------------------'''
@api.route('/api/v1.0/timelapse/ongoing/peek', methods=['GET'])
def peek_timelapse_ongoing():
    peekOngoing()

def peekOngoing():
    rt=jsonify({'result': 'OK'})    
    ongoing=LOCK() 
    if "name" in ongoing:
      helper.internalLogger.debug("REST generating video sample so far...")
      generateVideo(ongoing,False,False)
    UNLOCK(ongoing)
    return rt
'''----------------------------------------------------------'''
@api.route('/api/v1.0/timelapse/wipe', methods=['GET'])
def wipe_timelapse():
    rt=jsonify({'result': 'OK'})    
    ongoing=LOCK() 
    #TODO cancel ongoing clean all projects    UNLOCK(ongoing)
    return rt
'''----------------------------------------------------------'''
@api.route('/api/v1.0/timelapse/project/clean/<name>', methods=['GET'])
def clean_timelapse_project(name):
    return cleanProject(name)

def cleanProject(name):
    rt=jsonify({'result': 'KO'})    
    try:
        cleanUpOngoing(name,True,True)
        helper.internalLogger.debug("Cleaning {0}".format(name))
        purgeProject(name) 
        rt=jsonify({'result': 'OK'})    
    except Exception as e:
        helper.internalLogger.critical("Error cleaning: {0}.".format(name))
        helper.einternalLogger.exception(e)
    return rt
'''----------------------------------------------------------'''
@api.route('/',methods=["GET", "POST"])
@api.route('/timelapse/',methods=["GET", "POST"])
def timelapse_home():
    if request.method == 'POST':
      helper.internalLogger.debug("Processing new request from a form...{0}".format(request.form))
      form2 = request.form.to_dict()
      helper.internalLogger.debug("Processing new request from a form2...{0}".format(form2))   
      requestNewOngoing(form2)
    
    url={}

    st=getStatus()
    rt=render_template('index.html', title="TimeLapse Site",status=st)
    return rt
'''----------------------------------------------------------'''
@api.route('/cancel',methods=["GET"])
@api.route('/timelapse/cancel',methods=["GET"])
def timelapse_gui_cancel():
   helper.internalLogger.debug("GUI Cancelling video...")
   cancelOngoing()
   return redirect(url_for('timelapse_home'))
'''----------------------------------------------------------'''
@api.route('/stop',methods=["GET"])
@api.route('/timelapse/stop',methods=["GET"])
def timelapse_gui_stop():
   helper.internalLogger.debug("GUI Stopping video...")
   stopOngoing()
   return redirect(url_for('timelapse_home'))
'''----------------------------------------------------------'''
@api.route('/peek',methods=["GET"])
@api.route('/timelapse/peek',methods=["GET"])
def timelapse_gui_peek():
   helper.internalLogger.debug("GUI Peeking video...")
   peekOngoing()
   return redirect(url_for('timelapse_home'))
'''----------------------------------------------------------'''
@api.route('/clean/<name>',methods=["GET"])
@api.route('/timelapse/clean/<name>',methods=["GET"])
def timelapse_gui_clean(name):
   helper.internalLogger.debug("GUI clean {0}...".format(name))
   cleanProject(name)
   return redirect(url_for('timelapse_home'))

@api.route('/shoot',methods=["GET"])
@api.route('/timelapse/shoot',methods=["GET"])
def timelapse_triggerPhoto():
  ongoing=LOCK() #Regardless is manual trigerred, better mutex with ongoing just in case 

  global GLB_latestManualShooted
  global GLB_latestManualShootedDateTime 
  #delete if any latest
  try:
    remove(GLB_latestManualShooted)
  except Exception as e:
    helper.internalLogger.critical("Error cleaning: {0}.".format(GLB_latestManualShooted))
    helper.einternalLogger.exception(e)
  #select a new name to avoid cache issues
  GLB_latestManualShooted= GLB_configuration["mediaPath"]+"/latest.jpg."+str(time.time())
  #take photo
  takePhoto(GLB_latestManualShooted)
  UNLOCK(ongoing)  
  return redirect(url_for('timelapse_home'))
'''----------------------------------------------------------'''
'''--------    purgeProject                -----------------'''
'''----------------------------------------------------------'''
def purgeProject(name):

  projects=getProjects() 
  

  #clean up other ongoing temps.
  for c in projects:
    if "name" in c:
      helper.internalLogger.debug("Checking status of project {0}:{1}".format(c['name'],c['status']))
      if c["name"] == name:
        helper.internalLogger.debug("Removing project {0}:{1}".format(c['name'],c['status']))
        projects.remove(c)

  setProjects(projects)



'''----------------------------------------------------------'''
'''--------    updateProjectsWithOngoing    -----------------'''
'''----------------------------------------------------------'''
def updateProjectsWithOngoing(ongoing):
  projects=getProjects() 
   

  #clean up other ongoing temps.
  for c in projects:
    if "status" in c and "name" in c:
      helper.internalLogger.debug("Checking status of project {0}:{1}".format(c['name'],c['status']))
      if c["status"] == "ONGOING":
        helper.internalLogger.debug("Removing project {0}:{1}".format(c['name'],c['status']))
        projects.remove(c)

  helper.internalLogger.debug("Adding project {0}:{1}".format(ongoing['name'],ongoing['status']))
  projects.append(ongoing)
  setProjects(projects)


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
    pathFileVideo=pathFileVideo+".part.avi"

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

  ongoing["video"]=pathFileVideo
  if closeOngoing:
    ongoing["status"]="DONE"
    updateProjectsWithOngoing(ongoing)
    ongoing.clear()
  else:
    updateProjectsWithOngoing(ongoing)


'''----------------------------------------------------------'''
'''----------------       takefPhoto      -------------------'''
'''----------------------------------------------------------'''
def takePhoto(outfile):
  helper.internalLogger.debug("Taking photo:{0}".format(outfile))
  cmd=GLB_configuration["takePhotoCmd"].replace("PARAMETER_OUTFILE",outfile)
  subprocess.call(['bash','-c',cmd])
  # TODO return error if happen


'''----------------------------------------------------------'''
'''----------------       updateOngoing   -------------------'''
'''----------------------------------------------------------'''
def updateOngoing(ongoing):

  helper.internalLogger.debug("updateOngoing: {0}".format(ongoing))
  if not "interval" in ongoing:
    return False
  ongoing["status"]="ONGOING"
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


  takePhoto(pathfile)
  
  #TODO CONTROL ERRORS
  ongoing["latestPhoto"]=pathfile



  # It may terminate by date or number of pictures
  if "maxNbrOfPictures" in ongoing:
    if ongoing["nbrOfPictures"] >= ongoing["maxNbrOfPictures"]:
      helper.internalLogger.debug("Generating video, max nbr of picture reached {0}:".format(ongoing["maxNbrOfPictures"]))
      generateVideo(ongoing,True,True)
      return

  if "maxTime" in ongoing:
    if ongoing["firstPictureTime"] + ongoing["maxTime"] < now:
      helper.internalLogger.debug("Generating video, max time timelapsing reached {0}:".format(ongoing["maxTime"]))
      generateVideo(ongoing,True,True)
      return




'''----------------------------------------------------------'''
def  mountBindMediaPath(mount=True):
  ### Mount in loop mediapath 
  localpath=os.path.dirname(os.path.abspath(__file__))+"/static/tmp/"+os.path.basename(GLB_configuration["mediaPath"])

  try:
        #Create local path
        os.makedirs(localpath)
  except FileExistsError:
        # directory already exists
        pass
  

  try:
    cmd="sudo umount " + localpath
    if mount:
      cmd="sudo mount --bind "+GLB_configuration["mediaPath"]+ " " +localpath

    helper.internalLogger.debug("Mounting in loop mediapath for static flask access:{0}".format(cmd))
    subprocess.call(['bash','-c',cmd]) 
  except Exception as e:
    e = sys.exc_info()[0]
    helper.internalLogger.debug('Error: executing {0}. Exception unprocessed properly. Exiting'.format(cmd))
    helper.einternalLogger.exception(e)  

'''----------------------------------------------------------'''
def rebuildProjectsFromFileSystem():
    projects=[]

    extension = "avi"
    for dirpath, dirnames, files in os.walk(GLB_configuration["mediaPath"]):
        for name in files:
            if extension and name.lower().endswith(extension):
                helper.internalLogger.debug("File IN {0}".format(os.path.join(dirpath, name)))
                item={}
                
                item["name"]=os.path.basename(os.path.dirname(dirpath))
                item["video"]=os.path.join(dirpath, name)
                item["lastPictureTime"]=os.path.getmtime(os.path.join(dirpath, name))
                item["status"]="DONE"
                projects.append(item)
            elif not extension:
                helper.internalLogger.debug("File OUT {0}".format(os.path.join(dirpath, name)))

    setProjects(projects)

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

  global GLB_latestManualShooted

  GLB_latestManualShooted="none"


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
  
  mountBindMediaPath(False)
  mountBindMediaPath(True)
 
  rebuildProjectsFromFileSystem()

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
    mountBindMediaPath(False)
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

