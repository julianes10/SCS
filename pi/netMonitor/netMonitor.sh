#!/bin/bash

echo "Here we go: $@"
usage(){
  echo "------------------------------------------------------------------"
	echo "Usage: $0 <configFile>"
	echo "   Where config file defines:"
  echo "      HOST2MONITOR"
  echo "      INTERVAL"
  echo "      RETRYTIMES"
  echo "      RETRYINTERVAL"
  echo "      ONFAILURECOMMAND"
  echo "Example: www.google.com 30 5 5 reboot"
  echo "------------------------------------------------------------------"
	exit 1
}
rt=55


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
echo "Parameters INTERVAL=$INTERVAL RETRYTIMES=$RETRYTIMES RETRYINTERVAL=$RETRYINTERVAL"  | tee >(logger -t $0)

while true; do
  nextSleep=$INTERVAL
  ping -c1 $HOST2MONITOR > /dev/null
  pingresult=$?
  if [ $pingresult -eq 0 ]
  then
      echo "Success pinging $HOST2MONITOR after $consecutiveFailures failures" | tee >(logger -t $0)
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

  #Update latest report
  echo "TotalSuccess=$totalSuccess">/tmp/netMonitor.status
  echo "TotalFailures=$totalFailures">>/tmp/netMonitor.status
  echo "ConsecutiveFailures=$consecutiveFailures">>/tmp/netMonitor.status
  sleep $nextSleep
done

