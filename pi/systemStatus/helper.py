import logging
import sys
import os
import subprocess

def init(tracePath="/var/log/em.log",exceptionsPath="/var/log/em.log",il="il",eil="eil"):
  global internalLogger
  internalLogger = logging.getLogger(il)
  hdlr_1 = logging.FileHandler(tracePath)
  formatter_1 = logging.Formatter('%(asctime)s %(processName)s %(levelname)-8s %(threadName)-10s %(funcName)12s() %(message)s')
  hdlr_1.setFormatter(formatter_1)
  internalLogger.addHandler(hdlr_1)
  internalLogger.setLevel(logging.DEBUG)

  # Logging with exceptions 
  global einternalLogger
  einternalLogger  = logging.getLogger(eil)
  hdlr_1 = logging.FileHandler(exceptionsPath)
  formatter_1 = logging.Formatter('%(asctime)s %(processName)s %(levelname)-8s %(threadName)-10s %(funcName)12s() %(message)s')
  hdlr_1.setFormatter(formatter_1)
  einternalLogger.addHandler(hdlr_1)
  einternalLogger.setLevel(logging.DEBUG)

def amIaPi():
  rt=False
  if "arm" in os.uname()[4]:
    rt=True
  return rt

def getResultCommand(cmd):
    rt=False
    #internalLogger.debug("Executing shell cmd:{0}...".format(cmd))
    try:
      result=subprocess.check_output(cmd, shell=True)
      rt=True
    except subprocess.CalledProcessError as execution:
      internalLogger.debug("Return code: {0}. Output {1}".format(execution.returncode, execution.output))
    return rt

def getOutputCommand(cmd,default):
    rt=default
    #internalLogger.debug("Executing shell cmd:{0}...".format(cmd))
    try:
      result=subprocess.check_output(cmd, shell=True)
      rt=result.decode().rstrip()
    except subprocess.CalledProcessError as execution:
      internalLogger.debug("Return code: {0}. Output {1}".format(execution.returncode, execution.output))
    return rt
