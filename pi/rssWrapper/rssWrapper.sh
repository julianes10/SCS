#!/bin/bash 
echo "This script is as a wrapper to tts rss news"
#args: $1(stationId | STOP) 
echo "Here we go $@"

function usage
{
  echo  "$0 
           --url  <URLFSS>  [--items <NUM ITEMS TO READ>]   
           --stop 
           --help"
  echo "Notes:
          --stop only killall tts tool
          --items default 3"
}

################################################
function stop 
{
#Stop whatever it is playing
echo "Stopping rss speech..."
killall pico2wave
}

################################################
function dilo 
{
  LAN="es-ES"
  #LAN="en-GB"
  pico2wave -l $LAN -w /tmp/lookdave.wav "$1" && aplay /tmp/lookdave.wav
}

################################################
function sayIt 
{
  LANF=""
  #LANF="--language spanish"
  echo "$1" | festival --tts  $LANF 
}

################################################
function readRSSURL 
{
echo "Checkout rss news from: $1, items $2, and title: $3..."

curl $1 --output /tmp/news.raw
feed -o /tmp/news.raw | head -n$2 >/tmp/news

grep "<language>es" /tmp/news.raw
spanish="$?"
if [ "$spanish" != "0" ]; then
  # Try again
  grep "xml:lang=\"es" /tmp/news.raw
  spanish="$?"
fi

LAN="en-GB"
LANF=""
if [ "$spanish" == "0" ]; then
  LAN="es-ES"
  LANF="--language spanish"
fi
echo "Language: $LAN ( $spanish )..."

if [ "$3" != "" ]; then
  if [ "$spanish" == "0" ]; then
    dilo "$3"
  else
    sayIt "$3"
  fi
fi


input=/tmp/news
while IFS= read -r var
do
  if [ "$spanish" == "0" ]; then
    dilo "$var"
  else
    sayIt "$var"
  fi
  sleep 1
done < "$input"
} 
################################################
################################################
################################################

if [ "$1" == "-h" -o "$1" == "--help" ]; then
  usage
elif [ "$1" == "--stop" ]; then
   stop
elif [ "$1" == "--url" ]; then
  #If args is not just stop, then let's put the rss to sing
  items=3
  if [ "$3" == "--items" ]; then
    items=$4
  fi

  title=""
  if [ "$3" == "--title" ]; then
    title=$4
  fi
  if [ "$5" == "--title" ]; then
    title=$6
  fi


  readRSSURL $2 $items $title
else
  echo "ERROR, unknown option $1"
  usage
  exit -1
fi
exit 0

