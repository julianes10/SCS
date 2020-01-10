#!/bin/bash 
echo "This script will tss $@ in spanish"

################################################
function stop 
{
#Stop whatever it is playing
echo "Stopping tss speech..."
killall pico2wave
}

################################################
function dilo 
{
  LAN="es-ES"
  #LAN="en-GB"
  pico2wave -l $LAN -w /tmp/lookdave.wav "$1" && aplay /tmp/lookdave.wav
}

stop
dilo "$@"
exit 0

