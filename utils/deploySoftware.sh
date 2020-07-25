#!/bin/bash 
# Deploy and setup release into pi system

echo "Here we go: $@"
usage(){
  echo "------------------------------------------------------------------"
	echo "Usage: $0 <fileSettings> (remote|egg) (local) [arduino][config])"
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

TMP_DEPLOY=`mktemp -d`
SS="$TMP_DEPLOY/eggSurprise.sh"

dumpGIT() {
  file=$1
  path=$2
  suffix=$3

  pushd $path
  GIT=`git log -n 1 --pretty=format:"%ad" --date=iso`

  echo "\"git-date$suffix\":\"$GIT\"," >> $file


  GIT=`git log -n 1 --pretty=format:"%h" --date=iso`
  echo "\"git-hash$suffix\":\"$GIT\"," >> $file


  aux=`git status --porcelain --untracked-files=no`
  if [ "$aux" = "" ]; then
    echo -n "\"git-dirty$suffix\":false" >> $file
  else
    echo -n "\"git-dirty$suffix\":true" >> $file
  fi
  git status --porcelain --untracked-files=no > $file.git.dirty$suffix
  popd
}

VSW_FILE="/tmp/vsw"
dumpVersionInfo() {
  file=$1
  DATE=`date '+%Y-%m-%d %H:%M:%S %z'`
  echo "{\"deployment-date\":\"$DATE\"," > $file 
  dumpGIT $file "." ""
  echo "," >>$file

  dumpGIT $file "./SCS" "-scs"

  echo "}" >>$file

}

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

dumpVersionInfo $VSW_FILE


if [ "$arg_dest" == "remote" ] || [ "$arg_dest" == "egg" ] ; then
  if [ "$arg_ori" == "local" ]; then

    # Cleaning
    echo "# Preparing the tarball locally..." 
    echo "## Cleaning local repo..." 
    find -L . -type f -name '*.o' -exec rm {} +
    find -L . -type f -name '*~' -exec rm {} +
    find -L . -type f -name '*.a' -exec rm {} +
    find -L . -type f -name '*.pyc' -exec rm {} +

    echo "## Copying local software files from . to $TMP_DEPLOY..."
    export GLOBIGNORE=".git:./arduino/build-uno:./arduino/build-nano";
    cp -rL ./pi/* $VSW_FILE* $TMP_DEPLOY

    for item in $SERVICES_LIST; do
      echo "## Customizing the service $item to $PROJECT_NAME... "
      sed -i -- 's/PROJECT_NAME/$PROJECT_NAME/g' $TMP_DEPLOY/$item/install/*
      chmod 644 $TMP_DEPLOY/$item/install/*.service 
    done

    if [ ! $deployConfig -eq 1 ]; then
       echo "## Skipping copying config files in $TMP_DEPLOY..."
       rm -rf $TMP_DEPLOY/etc
    fi

    if [ $deployArduino -eq 1 ]; then
       echo "## Compiling local arduino software..."
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
       echo "## Copying arduino binary and settings for avrdude..."
       cp ./arduino/$A_HEXPATH $TMP_DEPLOY
       cp ./arduino/Makefile   $TMP_DEPLOY

    fi


    echo "# Preparing script to run remotely..." 
    echo "#!/bin/bash">$SS 
    if [ -f install/custom-install.pre.sh ]; then
       cat install/custom-install.pre.sh >> $SS
    fi

    echo "systemctl stop $SERVICES_LIST" >>$SS
    echo "systemctl disable $SERVICES_LIST" >>$SS


    if [ $deployConfig -eq 1 ]; then
       echo "cp -rf $TMP_DEPLOY/etc /etc">>$SS
    fi


    if [ $deployArduino -eq 1 ]; then
       echo "avrdude -q -V -D -p atmega328p -c arduino -b $A_BAUD -P $A_TTY Makefile Makefile -U flash:w:$TMP_DEPLOY/arduino.hex:i">>$SS
    fi

    echo "rm -rf $DEPLOY_FOLDER" >>$SS    
    echo "cp -raf $TMP_DEPLOY $DEPLOY_FOLDER">>$SS
    for item in $SERVICES_LIST; do
      echo "cp -raf $TMP_DEPLOY/$item/install/*  /lib/systemd/system/">>$SS
    done
    echo "systemctl daemon-reload">>$SS
    echo "systemctl enable $DEPLOY_SERVICE">>$SS
    echo "systemctl start $SERVICES_LIST">>$SS

    if [ -f install/custom-install.post.sh ];then
       cat install/custom-install.post.sh >> $SS
    fi
   
    chmod +x $SS 
    #LET IT FOR DEBUGGING: echo "rm -rf $TMP_DEPLOY" >>$SS 
    

    if [ "$arg_dest" == "egg" ]  ; then
       #ZIP
       tar zcvf "eggSurprise.tgz" $TMP_DEPLOY
       echo "EGG ready $TMP_DEPLOY" 
       #LET IT FOR DEBUGGING: "rm -rf $TMP_DEPLOY"     
    fi


    if [ "$arg_dest" == "remote" ]  ; then
      echo "# Transfering the files..." 
      scp -r -P $PI_PORT $TMP_DEPLOY $PI_USER@$PI_IPNAME:$TMP_DEPLOY
    fi

    if [ "$arg_dest" == "remote" ]  ; then
      echo "# Deploying remotely..." 
      ssh -p $PI_PORT pi@$PI_IPNAME "sudo $SS"
    fi

  else
    echo "ERROR: no extra option selected for deployed remotely"
    usage
  fi
else
  echo "ERROR: no option selected for deployed"
  usage
fi

echo "------------------------------------------------"
echo "------------------------------------------------"
echo "Deployment finished, check message above just in case something stinks... and have fun"
echo "  Remember cheatsheet:"
echo "    Check status: sudo systemctl status <service>"
echo "    Start service: sudo systemctl start <service>"
echo "    Stop service: sudo systemctl stop <service>"
echo "    Check service's log: sudo journalctl -f -u <service>"

