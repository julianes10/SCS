#!/bin/bash
# usage: liga|champions [numero de canal opcional]
#echo "Executing $0 with arguments: $@"


if [ "$1" == "liga" ]; then
  canal="mitele.es/directo/movistar-laliga"
fi

if [ "$1" == "champions" ]; then
  canal="mitele.es/directo/movistar-liga-de-campeones"
fi

if [ "$#" -gt 1 ]; then
  canal=$canal-$2
fi
echo "Channel to tune: $canal"

curl -i -H "Content-Type: application/json" -X POST -d "{\"channel\":\"$canal\"}" http://localhost:5060/api/v1.0/webStreamingAgent/tracker

exit 0
