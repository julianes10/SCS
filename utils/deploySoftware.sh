#!/bin/bash 
# Deploy and setup release into pi system

echo "Here we go: $@"
usage(){
  echo "------------------------------------------------------------------"
	echo "Usage: $0 <fileSettings> (remote) (local) [arduino][config])"
  echo "NOTE: ONLY remote local arduino config is supported."
  echo "FileSettings must be define the following environment variables:"
  echo "  SERVICES_LIST service1 service2 ...."
  echo "  DEPLOY_FOLDER e.g /opt/project/...."
  echo "  PI_USER pi"
  echo "  PI_IPNAME pi32"
  echo "  PI_PORT 22"
  echo "------------------------------------------------------------------"
	exit 1
}
rt=55

#---------------------------------------------------------------------------
arg_dest="$2"
arg_ori="$3"

deployConfig=0
deployArduino=0
for i in "$@"
do
case $i in
    config)
      deployConfig=1
    ;;
    arduino)
      deployArduino=1
    ;;
esac
done

TMP_DEPLOY="/home/pi/deploy.tmp"

#---------------------------------------------------------------------------
echo "This script will deploy SERVICES_LIST in your system"
if [ "$1" == "-h" -o "$1" == "--help" ]; then
  usage
  exit 0
fi

if [ "$1" == "" ]; then
  echo "ERROR: you must not deploy with a file with the settings"
  usage
  exit
fi

source $1
echo "  Loaded variables:"
echo "   SERVICES_LIST: $SERVICES_LIST"
echo "   DEPLOY_FOLDER: $DEPLOY_FOLDER"
echo "   PI_USER:       $PI_USER"
echo "   PI_IPNAME:     $PI_IPNAME"
echo "   PI_PORT:       $PI_PORT"

#---------------------------------------------------------------------------

for item in $SERVICES_LIST; do
    echo "Service to install: $item"
done

if [ "$arg_dest" == "remote" ]; then
  if [ "$arg_ori" == "local" ]; then

    # Cleaning
    find -L . -type f -name '*.o' -exec rm {} +
    find -L . -type f -name '*~' -exec rm {} +
    find -L . -type f -name '*.a' -exec rm {} +
    find -L . -type f -name '*.pyc' -exec rm {} +

    echo "Stopping services..."
    ssh -p $PI_PORT pi@$PI_IPNAME "sudo systemctl stop $SERVICES_LIST"

    echo "Copying local files from . to $TMP_DEPLOY..."
    ssh -p $PI_PORT pi@$PI_IPNAME "sudo rm -rf $TMP_DEPLOY; mkdir -p $TMP_DEPLOY"
    export GLOBIGNORE=".git:./arduino/build-uno:./arduino/build-nano";
    scp -r -P $PI_PORT ./pi/* $PI_USER@$PI_IPNAME:$TMP_DEPLOY

    DEPLOY_CONFIG=""
    if [ $deployConfig -eq 1 ]; then
       DEPLOY_CONFIG="sudo cp -rf $DEPLOY_FOLDER/etc/* /etc/;"
    fi
    DEPLOY_ARDUINO=""
    if [ $deployArduino -eq 1 ]; then
       ## Compile localy
       pushd ./arduino
       make
       retval=$?
       popd
       if [ $retval -ne 0 ]; then
         echo "ERROR COMPILING ARDUINO FILE"
         exit 1
       fi 
       ## Get basic info
       A_BOARD=`awk '/BOARD_TAG/ {print $3}' ./arduino/Makefile`
       A_BAUD=`awk '/AVRDUDE_ARD_BAUDRATE/ {print $3}' ./arduino/Makefile`
       A_HEXPATH="./build-$A_BOARD/arduino.hex"
       A_TTY=`awk '/ARDUINO_PORT/ {print $3}' ./arduino/Makefile`
       echo "### GOT ARDUINO PARAMS: $A_BAUD - $A_HEXPATH - $A_TTY"
       ## COPY .hex and settings for avrdude
       scp -P $PI_PORT ./arduino/$A_HEXPATH $PI_USER@$PI_IPNAME:$TMP_DEPLOY
       ## Prepare for deploy .hex and settings for avrdude
       DEPLOY_ARDUINO="avrdude -q -V -D -p atmega328p -c arduino -b $A_BAUD -P $A_TTY Makefile Makefile -U flash:w:$DEPLOY_FOLDER/arduino.hex:i;"
    fi

    DEPLOY_SERVICE=""
    for item in $SERVICES_LIST; do
      echo "Setting up service $item ... "
      DEPLOY_SERVICE="sed -i -- 's/PROJECT_NAME/$PROJECT_NAME/g' $DEPLOY_FOLDER/$item/install/* ;"
      DEPLOY_SERVICE="$DEPLOY_SERVICE chmod 644 $DEPLOY_FOLDER/$item/install/* ;"
      DEPLOY_SERVICE="$DEPLOY_SERVICE sudo cp -raf $DEPLOY_FOLDER/$item/install/*  /lib/systemd/system/;"
    done
    DEPLOY_SERVICE="$DEPLOY_SERVICE sudo systemctl daemon-reload;"
    DEPLOY_SERVICE="$DEPLOY_SERVICE sudo systemctl enable  $SERVICES_LIST;"

    echo "Deploying on $DEPLOY_FOLDER, setup config, arduino, start and status..."
    ssh -p $PI_PORT pi@$PI_IPNAME "sudo rm -rf $DEPLOY_FOLDER; sudo mv $TMP_DEPLOY $DEPLOY_FOLDER; $DEPLOY_CONFIG $DEPLOY_SERVICE $DEPLOY_ARDUINO sudo systemctl start $SERVICES_LIST;sudo systemctl status $SERVICES_LIST;"
  else
    echo "ERROR: no extra option selected for deployed remotely"
    usage
  fi
else
  echo "ERROR: no option selected for deployed"
  usage
fi

echo "Deployment finished, check message above just in case something stinks... and have fun"
echo "  Remember cheatsheet:"
echo "    Check status: sudo systemctl status <service>"
echo "    Start service: sudo systemctl start <service>"
echo "    Stop service: sudo systemctl stop <service>"
echo "    Check service's log: sudo journalctl -f -u <service>"

