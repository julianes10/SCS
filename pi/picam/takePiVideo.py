#!/usr/bin/env python3
import argparse
import picamera
import time

def main(outfile,t):
    camera=picamera.PiCamera()
 
    camera.start_preview()
    camera.start_recording(outfile)
    time.sleep(t)
    camera.stop_recording()
    camera.stop_preview()
    camera.close()

'''----------------------------------------------------------'''
'''----------------     parse_args        -------------------'''
def parse_args():
    """Parse the args."""
    parser = argparse.ArgumentParser(
        description='Take photo with picam')
    parser.add_argument('--outfile', type=str, required=False,
                        default='/tmp/picam.jpg',
                        help='Jpeg file to save the picture')
    parser.add_argument('--time', type=int, required=False,
                        default=5,
                        help='Jpeg file to save the picture')
    return parser.parse_args()


'''----------------------------------------------------------'''
'''----------------       '__main__'      -------------------'''
if __name__ == '__main__':
    args = parse_args()
    main(configfile=args.outfile)

