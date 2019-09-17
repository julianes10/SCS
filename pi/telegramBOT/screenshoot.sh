#!/bin/bash
file=$1
rm -f $1 > /dev/null 2>&1
# Run this script in display 0 - the monitor
export DISPLAY=:0
scrot $file

