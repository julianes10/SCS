#!/bin/bash 

# Capture 30 seconds of raw video at 640x480 and 150kB/s bit rate into a pivideo.h264 file:
raspivid -t 30000 -w 640 -h 480 -fps 25 -b 1200000 -p 0,0,640,480 -hf -o $1.h264 
# Wrap the raw video with an MP4 container: 
MP4Box -add $1.264 $1
# Remove the source raw file, leaving the remaining pivideo.mp4 file to play
rm -f $1.264

