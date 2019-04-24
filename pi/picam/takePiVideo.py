#!/usr/bin/env python3
import argparse
import picamera
import time

def main(args):
    camera=picamera.PiCamera()
    camera.rotation = args.rotation
    camera.resolution = (640, 480)
    camera.start_recording(args.outfile)
    camera.wait_recording(args.time)
    camera.stop_recording()
    camera.close()

'''----------------------------------------------------------'''
'''----------------     parse_args        -------------------'''
def parse_args():
    """Parse the args."""
    parser = argparse.ArgumentParser(
        description='Take video with picam')
    parser.add_argument('--outfile', type=str, required=False,
                        default='/tmp/picam.avi',
                        help='Jpeg file to save the picture')
    parser.add_argument('--time', type=int, required=False,
                        default=5,
                        help='Time to record')
    parser.add_argument('--rotation', type=int, required=False,
                        default=0,
                        help='Rotation degree')
    return parser.parse_args()


'''----------------------------------------------------------'''
'''----------------       '__main__'      -------------------'''
if __name__ == '__main__':
    args = parse_args()
    main(args)

