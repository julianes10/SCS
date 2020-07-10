#!/bin/bash 
# intall depndencies sudo apt install -y gpac

relaunch=0
sudo systemctl status mjpg-streamer.service > /dev/null 2>&1
if [ $? -eq 0 ]
then
  # echo "Stopping live streaming..."
  sudo systemctl stop mjpg-streamer.service > /dev/null 2>&1
  relaunch=1
fi

#echo "Running raspivid with options $@...."

raspivid $@
aux=$?
if [ ! $aux -eq 0 ]
then
   echo "#### ERROR taking video ####"
fi


if [ $relaunch -eq 1 ]
then
    # echo "Restoring live streaming..."
    sudo systemctl start mjpg-streamer.service > /dev/null 2>&1
fi


exit $aux



  

