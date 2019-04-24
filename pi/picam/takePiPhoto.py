#!/usr/bin/env python3
import argparse
import picamera

def main(args):
  camera=picamera.PiCamera()
  camera.rotation = args.rotation
  camera.resolution = (1280, 720)
  camera.capture(args.outfile)
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
    parser.add_argument('--rotation', type=int, required=False,
                        default=0,
                        help='Rotation degree')

    return parser.parse_args()

'''----------------------------------------------------------'''
'''----------------       '__main__'      -------------------'''
if __name__ == '__main__':
    args = parse_args()
    main(args)

