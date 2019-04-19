#!/usr/bin/env python3
import argparse
import picamera

def main(outfile):
  camera=picamera.PiCamera()
  camera.capture(outfile)
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
    return parser.parse_args()

'''----------------------------------------------------------'''
'''----------------       '__main__'      -------------------'''
if __name__ == '__main__':
    args = parse_args()
    main(configfile=args.outfile)

