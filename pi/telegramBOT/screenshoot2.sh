#!/bin/bash
# check https://github.com/AndrewFromMelbourne/raspi2png
file=$1
rm -f $file > /dev/null 2>&1
raspi2png -w 320 -h 240  -p $file

