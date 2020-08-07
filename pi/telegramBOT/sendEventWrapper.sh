#!/bin/bash 
#        if "text" in event:            sendTextMessageToSubscribers(item["subscribers"],event["text"])
#        if "img" in event:            sendImageMessageToSubscribers(item["subscribers"],event["img"])
#        if "video" in event:            sendVideoMessageToSubscribers(item["subscribers"],event["video"])
#        if "filetext" in event:            sendTextFileMessageToSubscribers(item["subscribers"],event["filetext"])

#FOR TARGET:
HOST="localhost"
HAPROXYCONFIGFILE="/etc/haproxy/haproxy.cfg"
#TODO THIS IS NOT GOOD ENOUGH, MULTIPLE TELEGRAMS CAN BE THERE

#FOR DEBUG:
#HOST="192.168.1.44"
#HAPROXYCONFIGFILE="../../../pi/etc/haproxy/haproxy.cfg "


PORT=$(cat $HAPROXYCONFIGFILE | grep telegram | grep server | cut -d: -f2)
BASE_URL="http://$HOST:$PORT/api/v1.0/telegramBOT"



usage(){
  echo "------------------------------------------------------------------"
	echo "Usage: $0 -e <eventName> [OPTS]"
  echo "    Where OPTS can be one or more of the following flags and arguments"
  echo "      -t --text 'additional text to show'"
  echo "      -v --video    <file>"
  echo "      -i --image    <file>"  
  echo "      -d --doc      <file>"
  echo "      -f --textfile <file>"
  echo ""      
  echo "------------------------------------------------------------------"
	exit 1
}
if [ "$#" -lt 2 ]; then
  usage
  exit 1
fi

eventAdditionalText="NONE"
eventAdditionalImg="NONE"
eventAdditionalVideo="NONE"
eventAdditionalTextFile="NONE"
eventName="NONE"


# Args while-loop
while [ $# -gt 0 ];
do
   case "$1" in
   -e  | --event ) shift
                   eventName=$1                   
                   ;;
   -t  | --text )  shift
                   eventAdditionalText=$1                   
                	 ;;
   -v  | --video ) shift
                   eventAdditionalVideo=$1
			             ;;
   -i  | --image ) shift
                   eventAdditionalImg=$1
			             ;;
   -f  | --textfile ) shift
                   eventAdditionalTextFile=$1
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
if [  "$eventAdditionalText" != "NONE" ]; then
  auxStr1=", \"text\": \"$eventAdditionalText\" "
fi

auxStr2=""
if [  "$eventAdditionalVideo" != "NONE" ]; then
  ofile=$(basename $eventAdditionalVideo)
  MP4Box -add $eventAdditionalVideo /tmp/$ofile.mp4 > /dev/null 2>&1
  auxStr2=", \"video\": \"/tmp/$ofile.mp4\" "
fi

auxStr3=""
if [  "$eventAdditionalImg" != "NONE" ]; then
  auxStr3=", \"image\": \"$eventAdditionalImg\" "
fi

auxStr4=""
if [  "$eventAdditionalTextFile" != "NONE" ]; then
  auxStr4=", \"filetext\": \"$eventAdditionalTextFile\" "
fi


cat <<EOF
{ "name":"$eventName" $auxStr1 $auxStr2 $auxStr3 $auxStr4} 
EOF
}

function sendEvent()
{
curl -i \
-H "Accept: application/json" \
-H "Content-Type:application/json" \
-X POST --data "$(generate_post_data)" $BASE_URL/event > /dev/null 2>&1
}

echo "DEBUG: sending $(generate_post_data) to $BASE_URL/event"
sendEvent

