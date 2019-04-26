#! /bin/bash

target=localhost

if [ "$2" == "" ];  then
  echo "Operation over localhost"
else
  echo "Operation over $2"
  target=$2
fi

if [ "$1" == "--help" ];  then
  echo "API available:"
  curl -D - -H 'Content-Type: application/json' $target:8080/jsonrpc   
else
  echo "Calling jsonrpc kodi API with request: $1..."
  curl -D - -H 'Content-Type: application/json' -X POST  -d@$1 $target:8080/jsonrpc 
fi


