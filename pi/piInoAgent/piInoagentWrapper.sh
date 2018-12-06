#!/bin/bash 
echo "Wrapper to access piInoAgent"
echo "Here we go: $@"

################################################
function usage
{ 
  echo  "$0 
           --color <COLOR>
           --on
           --mode <fullColor|rolling|rainbow|noise|knightRider>
           --off   
           --pause <quicker|slower>
           --help"
  echo "Notes:
           --color will change main color theme on led strip
           <COLOR> should be a color known by python colour module or #RRGGBB html notation  
"
}

################################################
function setMode
{
  echo "Setting up specific mode in led strip: \"$1\"..."
  m='A'
  c='red'
  t='9999'
  p='500'
  case "$1" in
        fullColor)
            m='A'
            ;;         
        rolling)
            m='C'
            ;;           
        rainbow)
            m='W'
            ;;         
        noise)
            m='N'
            ;;         
        knightRider)
            m='K'
            ;;                  
        *)
            echo $"Bad usage"
            exit 1
       esac

  curl -i -H "Content-Type: application/json" -X POST -d '{"mode":"'$m'","color":"'$c'","pause":'$p',"timeout":'$t'}' http://localhost:5001/api/v1.0/ls/misc
  echo $t >/tmp/pinoAgent.t
  echo $p >/tmp/pinoAgent.p

} 
################################################
function setPause
{
  p=$1
  p0=`cat /tmp/pinoAgent.p`
  step=100 
  if (( p0 < 100 )); then
    step=10   
  fi
  
  case "$1" in
        quicker)

            p=$(( p0 - step ))
            ;;         
        slower)
            p=$(( p0 + step ))
            ;;           
        *)
            p=$1
            echo $"Try with a number"
       esac
  echo $p >/tmp/pinoAgent.p

  echo $"Setting up pause from \"$p0\" to: \"$p\"..."
  curl -i -H "Content-Type: application/json" -X POST -d '{"pause":'$p'}' http://localhost:5001/api/v1.0/ls/pause
} 

################################################
function setColor 
{
  echo "Setting up main color in led strip: \"$1\"..."
  curl -i -H "Content-Type: application/json" -X POST -d '{"color":"'$1'"}' http://localhost:5001/api/v1.0/ls/color
} 

################################################
function turnOn 
{
  turnOff
  setColor "white"
} 
################################################
function turnOff 
{
  echo "Turning off led strip..."
  curl -i -H "Content-Type: application/json" -X POST -d '{"reset":true}' http://localhost:5001/api/v1.0/ls/reset
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
elif [ "$1" == "--color" ]; then
  setColor $2
  exit 0
elif [ "$1" == "--on" ]; then
  turnOn
  exit 0
elif [ "$1" == "--off" ]; then
  turnOff
  exit 0
elif [ "$1" == "--mode" ]; then
  setMode $2
  exit 0
elif [ "$1" == "--pause" ]; then
  setPause $2
  exit 0
else
  echo "ERROR, unknown option $1"
  usage
  exit -1
fi






