#!/usr/bin/env python
import sys
import signal
import subprocess
import sched, time
from threading import Timer
import RPi.GPIO as GPIO


interrupted = False

def hotword_handler(arg1):
    values=[]
    values.append(GPIO.input(11))
    for num in range(1,30):
      time.sleep(0.01)    
      values.append(GPIO.input(11)) 
      #if (aux == True):
      #   return
    
    #if we are still here, falling is consistent
    print('- gpio values: {0}'.format(values))   
    for index, item in enumerate(values):
      if item==0:
        print('- VALID FALLING GPIO')   
        p=subprocess.Popen(['bash','-c',"curl -i -H \"Content-Type: application/json\" -X POST -d  '{\"debug\":\"shock sensor\"}' http://localhost:5000/ipaem/api/v1.0/hotword"])
        p.wait()
        return  


def signal_handler(signal, frame):
    global interrupted
    interrupted = True
    print('-end -----------------------------')   
    exit(-1)


def interrupt_callback():
    global interrupted
    return interrupted

# capture SIGINT signal, e.g., Ctrl+C
signal.signal(signal.SIGINT, signal_handler)


'''----------------------------------------------------------'''
'''----------------       M A I N         -------------------'''
'''----------------------------------------------------------'''

def main():
  print('-start -----------------------------')   
  GPIO.setwarnings(False)
  GPIO.setmode(GPIO.BOARD)
  GPIO.setup(11, GPIO.IN)         #Read output from shock sensor
  GPIO.add_event_detect(11, GPIO.FALLING)

  cb = lambda arg1=1: hotword_handler(arg1)
  GPIO.add_event_callback(11, cb)


  while True:
    time.sleep(0.1)

'''----------------------------------------------------------'''
'''----------------       '__main__'      -------------------'''
if __name__ == '__main__':
    main()
