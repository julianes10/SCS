#!/bin/bash
# usage: liga|champions [numero de canal opcional]
#echo "Executing $0 with arguments: $@"


if [ "$1" == "liga" ]; then
  canal="https://orangetv.orange.es/LiveChannel?extChId=11013&type=live"
fi

if [ "$1" == "champions" ]; then
  canal="https://orangetv.orange.es/LiveChannel?extChId=1023&type=live"
fi

if [ "$1" == "gol" ]; then
  canal="https://orangetv.orange.es/LiveChannel?extChId=11031&type=live"
fi



if [ "$#" -gt 1 ]; then  #TODO
  canal=$canal-$2
fi
echo "Channel to tune: $canal"

curl -i -H "Content-Type: application/json" -X POST -d "{\"channel\":\"$canal\"}" http://localhost:5060/api/v1.0/webStreamingAgent/tracker

exit 0
