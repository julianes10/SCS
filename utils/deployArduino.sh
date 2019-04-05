#!/bin/bash 
source ./commonvars.sh

echo "This script will check if latest arduino firmware is the latest. To check this will compile latest deployed sources an diff with previous stored as backup hex file in TODO . No arguments required."
if [ "$1" == "-h" -o "$1" == "--help" ]; then
  echo "This script does not need parameters"
  exit 0
fi

cd $DEPLOY_FOLDER/arduino
make clean
make 
NEW_FILE="$DEPLOY_FOLDER/arduino/build-uno/arduino.hex"
OLD_FILE="/opt/arduino.hex"
diff $NEW_FILE $OLD_FILE
retval=$?
if [ $retval -ne 0 ]; then
  echo "Files differs, let's upload new firmware"
  make upload
  retval=$?
  if [ $retval -ne 0 ]; then
    echo "ERROR UPLOADING FILE"
  else
    cp $NEW_FILE $OLD_FILE
  fi
else
  echo "File already uploaded. Skip loading again"
fi

echo "Exiting."
