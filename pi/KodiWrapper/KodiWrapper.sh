#!/bin/bash 
echo "Wrapper to access kodi using jsonrpc basic commands"
echo "Here we go: $@"

################################################
function usage
{ 
  echo  "$0 
           --mute    
           --unmute  
           --stop  
           --checkPlayer 
           --checkMute
           --playPause
           --help"
  echo "Notes:
          --checkplayer return 0 if something is playing, -1 nothing is playing."
}

################################################
function stop 
{
  echo "Stopping kodi player..."
  curl -i -X POST http://localhost:8080/jsonrpc  \
    -H "Content-Type: application/json" \
    --data '{ "jsonrpc": "2.0", "method": "Player.Stop", "params": {"playerid":0}, "id": 1 }'
  curl -i -X POST http://localhost:8080/jsonrpc  \
    -H "Content-Type: application/json" \
    --data '{ "jsonrpc": "2.0", "method": "Player.Stop", "params": {"playerid":1}, "id": 1 }'
} 


################################################
function checkPlayer 
{
  echo "Check player..."
  curl -i -X POST http://localhost:8080/jsonrpc  \
    -H "Content-Type: application/json" \
    --data '{ "jsonrpc": "2.0", "method": "Player.GetActivePlayers", "id": 1}'
} 
################################################
function mute 
{
  echo "Mute kodi..."
  curl -i -X POST http://localhost:8080/jsonrpc  \
    -H "Content-Type: application/json" \
    --data '{ "jsonrpc": "2.0", "method": "Application.SetMute", "params": {"mute": true}, "id": 1 }'
} 

################################################
function unmute 
{
  echo "Mute kodi..."
  curl -i -X POST http://localhost:8080/jsonrpc  \
    -H "Content-Type: application/json" \
    --data '{ "jsonrpc": "2.0", "method": "Application.SetMute", "params": {"mute": false}, "id": 1 }'
} 

################################################
function playPause 
{
  echo "PlayPause kodi..."
  curl -i -X POST http://localhost:8080/jsonrpc  \
    -H "Content-Type: application/json" \
    --data '{ "jsonrpc": "2.0", "method": "Player.PlayPause", "params": { "playerid": 0 }, "id": 1}'
} 

################################################
function checkMute 
{
  echo "Check Mute..."
  curl -i -X POST http://localhost:8080/jsonrpc  \
    -H "Content-Type: application/json" \
    --data '{ "jsonrpc": "2.0", "method": "Application.GetMute", "id": 1}'
} 

################################################
################################################
################################################
if [ "$1" == "-h" -o "$1" == "--help" ]; then
  usage
  exit 0
elif [ "$1" == "" ]; then
  echo "ERROR, args needed"
  usage
  exit -1
elif [ "$1" == "--stop" ]; then
  stop
elif [ "$1" == "--playPause" ]; then
  playPause
elif [ "$1" == "--checkPlayer" ]; then
  checkPlayer
elif [ "$1" == "--checkMute" ]; then
  checkMute
elif [ "$1" == "--mute" ]; then
  mute
elif [ "$1" == "--unmute" ]; then
  unmute
elif [ "$1" == "--help" ]; then
  usage
else
  echo "ERROR, unknown option $1"
  usage
  exit -1
fi






