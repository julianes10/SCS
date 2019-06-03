#!/bin/bash 
relaunch=0
sudo systemctl status mjpg-streamer.service
if [ $? -eq 0 ]
then
  echo "Stopping live streaming..."
  sudo systemctl stop mjpg-streamer.service
  relaunch=1
fi

echo "Running raspistill with options $@...."

raspistill $@

aux=$?
if [ ! $aux -eq 0 ]
then
   echo "#### ERROR taking photo ####"
fi


if [ $relaunch -eq 1 ]
then
    echo "Restoring live streaming..."
    sudo systemctl start mjpg-streamer.service
fi


exit $aux



  

