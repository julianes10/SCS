#!/bin/bash 

SOURCEPATH="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

$SOURCEPATH/takePhotoMjpgStreamer.sh $@
if [ $? -eq 0 ]
then
   exit 0
fi

$SOURCEPATH/takePiPhoto.py --outfile $3 --rotation $4
aux=$?
if [ ! $aux -eq 0 ]
then
   echo "#### ERROR taking photo ####"
fi
exit $aux



  

