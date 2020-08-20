#!/usr/bin/env python
import argparse

'''----------------------------------------------------------'''
'''----------------       M A I N         -------------------'''
'''----------------------------------------------------------'''

def main(arg):
  import RPi.GPIO as GPIO

  GPIO.setwarnings(False)
  GPIO.setmode(GPIO.BCM) # GPIO Numbers instead of board numbers

  GPIO.setup(arg.pin, GPIO.OUT) # GPIO Assign mode
  if arg.value==-1:
    aux=GPIO.input(arg.pin)
    print('Pin {0} is {1}'.format(arg.pin,aux))
  else:
    if arg.value==0:
      GPIO.output(arg.pin, GPIO.LOW) # out
    else:
      GPIO.output(arg.pin, GPIO.HIGH) # out


'''----------------------------------------------------------'''
'''----------------     parse_args        -------------------'''
def parse_args():
    """Parse the args."""
    parser = argparse.ArgumentParser(
        description='GPIO wrapper')
    parser.add_argument('--pin', type=int, required=True,
                        help='GPIO number')
    parser.add_argument('--value', type=int, required=False,default=-1,
                        help='1 or 0')
    return parser.parse_args()

'''----------------------------------------------------------'''
'''----------------       '__main__'      -------------------'''
if __name__ == '__main__':
    args = parse_args()
    main(args)


    


