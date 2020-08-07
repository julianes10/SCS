#!/bin/bash 
#FOR TARGET:
HOST="localhost"
HAPROXYCONFIGFILE="/etc/haproxy/haproxy.cfg"
#TODO THIS IS NOT GOOD ENOUGH, MULTIPLE TELEGRAMS CAN BE THERE

#FOR DEBUG:
#HOST="192.168.1.44"
#HAPROXYCONFIGFILE="../../../pi/etc/haproxy/haproxy.cfg "


PORT=$(cat $HAPROXYCONFIGFILE | grep picam | grep server | cut -d: -f2)
BASE_URL="http://$HOST:$PORT/api/v1.0/picam"



usage(){
  echo "------------------------------------------------------------------"
	echo "Usage: $0 [OPTS]"
  echo "    Where OPTS can be one or more of the following flags and arguments"
  echo "      -o --outputFileName 'Output file'"
  echo "      -p --position <panValue> <tiltValue>"
  echo "      -b --backPosition"
  echo "      -f --flags <option to add to cmd in picam instead of default ones>"
  echo "      -c --cmd  <alternative to cmd configured in picam>"
  echo ""      
  echo "------------------------------------------------------------------"
	exit 1
}
if [ "$#" -lt 2 ]; then
  usage
  exit 1
fi


positionTilt="NONE"
positionPan="NONE"
positionBack="NONE"
outputFileName="NONE"
flags="NONE"
cmd="NONE"


# Args while-loop
while [ $# -gt 0 ];
do
   case "$1" in
   -o  | --outputFileName ) 
                   shift
                   outputFileName=$1                   
                   ;;
   -p  | --position )  
                   shift
                   positionPan=$1
                   shift
                   positionTilt=$1                                      
                	 ;;
   -c  | --cmd )  
                   shift
                   cmd=$1
                   ;;
   -f  | --flags )  
                   shift
                   flags=$1
                   ;;
   -b  | --backPosition ) 
                   positionBack="true"
			             ;;
   -h   | --help )        usage
                          exit
                          ;;
   *)                     shift
                          echo "$script: illegal option $1"
                          usage
                          ;;
    esac
    shift
done


generate_post_data()
{
auxStr1=""
if [  "$outputFileName" != "NONE" ]; then
  auxStr1="\"customOutputFile\": \"$outputFileName\""
else
  auxStr1="\"fake\":\"k\""
fi

if [  "$positionBack" != "NONE" ] || [  "$positionPan" != "NONE" ]; then
  auxStr2=""
  if [  "$positionBack" != "NONE" ]; then
    auxStr2="\"backPosition\": true"
  else
    auxStr2="\"backPosition\": false"
  fi

  auxStr3=""
  if [  "$positionPan" != "NONE" ]; then
    auxStr3="\"pan\": { \"abs\":\"$positionPan\"}, \"tilt\": { \"abs\":\"$positionTilt\"}"
    positionStr=", \"position\": { $auxStr2 , $auxStr3 }"
  else
    positionStr=", \"position\": { $auxStr2 , $auxStr3 }"
  fi
fi

auxStrCmd=""
if [  "$cmd" != "NONE" ]; then
  auxStrCmd=",\"cmd\": \"$cmd\""
fi
auxStrFlags=""
if [  "$flags" != "NONE" ]; then
  auxStrFlags=",\"customFlags\": \"$flags\""
fi

cat <<EOF
{ $auxStr1 $positionStr $auxStrCmd $auxStrFlags } 
EOF
}

function sendRequest()
{
curl -i \
-H "Accept: application/json" \
-H "Content-Type:application/json" \
-X POST --data "$(generate_post_data)" $BASE_URL/photo > /dev/null 2>&1
}

#echo "DEBUG: sending $(generate_post_data) to $BASE_URL/photo"
sendRequest

