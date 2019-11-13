#!/bin/bash

echo "Here we go: $@"
usage() {
  echo "------------------------------------------------------------------"
	echo "Usage: $0 <configFile>"
	echo "   Where config file defines:"
  echo "      HOST2MONITOR"
  echo "      INTERVAL"
  echo "      RETRYTIMES"
  echo "      RETRYINTERVAL"
  echo "      ONFAILURECOMMAND"
  echo "      FAVORITESSID (OPTIONAL USELESS). Path file to wpa_supplican.conf For simplicity  with networks in priority order"
  echo "      IFACE (OPTIONAL)."
  echo "Example: "
  echo "      HOST2MONITOR=www.google.com"
  echo "      INTERVAL=30"
  echo "      RETRYTIMES=5"
  echo "      RETRYINTERVAL=5"
  echo "      ONFAILURECOMMAND=reboot"
  echo "      FAVORITESSID=/etc/wpa_supplicant/wpa_supplicant.conf"
  echo "      IFACE=wlan0"
  echo "NOTE: favorite ssid is in TODO, as finally it works fine with priority in wpa_supplican and disable wicd as network manager, otherwise wifi interface gets dummy in autoreconnect"
  echo "------------------------------------------------------------------"
	exit 1
}
rt=55

checkFavoriteSSID() {
	echo ${FUNCNAME[ 0 ]} "... checking $1 on the $2 interface..." 
}

checkFavoriteSSID() {
	echo ${FUNCNAME[ 0 ]} "... checking $1 on the $2 interface..." 

  currentAttached=`iwconfig $2 | grep -i SSID  | cut -d ":" -f2 | sed 's/"//g' | awk '{$1=$1};1'`
	echo "SSIDs current attached is: $currentAttached"    


  # For simplicity, lets parse supplicant file, it is suppose essid are in priority order
 	echo "Gathering favorites SSIDs..." 
  favorites=`cat $1 | grep ssid | cut -d "=" -f2 | sed 's/"//g'`
  counter=0
  for i in $favorites
  do
    counter=$((counter+1))
    if [ "$counter" == "1" ]
    then 
      favorites1=`echo $i | awk '{$1=$1};1'`
    	echo "  SSID  1st favorite is: $favorites1" 
    else 
    	echo "  SSID next favorite is: $i"    
    fi
  done

  if [ "$currentAttached" == "$favorites1" ]
  then
   	echo "BINGO, connected to the fist favorite. Exiting this function."    
    return
  else
   	echo "Not connected to the fist favorite $favorites1, but $currentAttached. Let's explore if now is available..."    
  fi

  echo "Checking avaliable SSIDs..."
  currentAvailable=`iwlist $2 scanning | grep -i SSID | cut -d ":" -f2 | sed 's/"//g'`
  for i in $currentAvailable
  do
	  echo "  SSID: $i"
  done

  for i in $favorites
  do
    echo "Checking if favorite SSID $i is available on interface $2..."
    if [[ "$currentAvailable"  =~ "$1" ]]
    then 
      echo "YES, favorite SSID $i is available. TODO lets try connect..."
      
    else
      echo "NO, favorite SSID $i is not available..."
    fi     
  done

}


if [ "$#" -ne 1 ]
then
    echo "Illegal number of parameters"
    usage
    return rt
fi
source $1

consecutiveFailures=0
totalFailures=0
totalSuccess=0



echo "Starting $0, pinging $HOST2MONITOR, onfailure hook: $ONFAILURECOMMAND"  | tee >(logger -t $0)
echo "Parameters INTERVAL=$INTERVAL RETRYTIMES=$RETRYTIMES RETRYINTERVAL=$RETRYINTERVAL FAVORITESSID=$FAVORITESSID"  | tee >(logger -t $0)

while true; do
  nextSleep=$INTERVAL
  ping -c1 $HOST2MONITOR > /dev/null
  pingresult=$?
  if [ $pingresult -eq 0 ]
  then
      #echo "Success pinging $HOST2MONITOR after $consecutiveFailures failures" | tee >(logger -t $0)
      consecutiveFailures=0
      totalSuccess=$((totalSuccess+1))
  else
      totalFailures=$((totalFailures+1))
      consecutiveFailures=$((consecutiveFailures+1))
      echo "Failure pinging $HOST2MONITOR, $consecutiveFailures failures in row"  | tee >(logger -t $0)
      if [ "$consecutiveFailures" == "$RETRYTIMES" ]
      then
          echo "Maximun consecutive failures pinging $HOST2MONITOR, $consecutiveFailures executing $ONFAILURECOMMAND"  | tee >(logger -t $0)
     
          $ONFAILURECOMMAND
          consecutiveFailures=0
      else
          nextSleep=$RETRYINTERVAL
      fi
  fi

  if [ "$FAVORITESSID" != "" ]
  then
      checkFavoriteSSID "$FAVORITESSID" "$IFACE"
  fi

  #Update latest report
  echo "TotalSuccess=$totalSuccess">$LOGSTATUS
  echo "TotalFailures=$totalFailures">>$LOGSTATUS
  echo "ConsecutiveFailures=$consecutiveFailures">>$LOGSTATUS
  sleep $nextSleep
done

