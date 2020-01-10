#!/bin/bash 
echo "This script will tss $@ in english"

################################################
function stop 
{
#Stop whatever it is playing
echo "Stopping tss speech..."
killall pico2wave
}

################################################
function sayIt 
{
  LANF=""
  #LANF="--language spanish"
  echo "$1" | festival --tts  $LANF 
}

stop
sayIt "$@"
exit 0

