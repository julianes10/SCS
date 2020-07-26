#!/bin/bash 
# Deploy and setup release into pi system

echo "Here we go: $@"
usage(){
  echo "------------------------------------------------------------------"
	echo "Usage: $0 <fileSettings> (remote|egg|telegram) (local) [arduino][config])"
  echo "  remote use ssh scp for deploying and requires PI_IPNAME/USER/PORT"
  echo "  egg just tenerate tarball"
  echo "  telegram push tarball to a bot as document, requires TELEGRAM_TOKEN/CHATID"
  echo "Settings must be define the following environment variables:"
  echo "  SERVICES_LIST service1 service2 ...."
  echo "  DEPLOY_FOLDER e.g /opt/project/...."
  echo "  PI_USER pi"
  echo "  PI_IPNAME pi32"
  echo "  PI_PORT 22"
  echo "  TELEGRAM_TOKEN as token bot where tarball will be upload"
  echo "  TELEGRAM_CHATID with the user id on behalf this script upload the tarball"
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


if [ "$arg_dest" == "telegram" ] || [ "$arg_dest" == "remote" ] || [ "$arg_dest" == "egg" ] ; then
  if [ "$arg_ori" == "local" ]; then

    # Cleaning
    echo "#-----------------------------------------------#"       
    echo "# Preparing the tarball locally..." 
    echo "#-----------------------------------------------#"       

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
      sed -i -- "s/PROJECT_NAME/$PROJECT_NAME/g" $TMP_DEPLOY/$item/install/*
      sed -i -- "s/SERVICE_NAME/$item/g" $TMP_DEPLOY/$item/install/*
      chmod 644 $TMP_DEPLOY/$item/install/*.service 
    done

    if [ ! $deployConfig -eq 1 ]; then
       echo "## Skipping copying config files in $TMP_DEPLOY..."
       rm -rf $TMP_DEPLOY/etc
    fi

    if [ $deployArduino -eq 1 ]; then
       echo "#-----------------------------------------------#"       
       echo "## Compiling local arduino software..."
       echo "#-----------------------------------------------#"       
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

    echo "#-----------------------------------------------#"
    echo "# Preparing script to run remotely..." 
    echo "#-----------------------------------------------#" 
    echo "#!/bin/bash">$SS 
    echo "exec > /tmp/eggSurprise.log 2>&1">>$SS
    echo "echo 'Starting into the egg... '">>$SS
    echo "date">>$SS
    echo "whoami">>$SS
    #echo "set">>$SS
    echo "echo 'Executing custom-install-pre...'">>$SS

    if [ -f install/custom-install.pre.sh ]; then
       cat install/custom-install.pre.sh >> $SS
    fi

    echo "echo 'Stopping services...'">>$SS
    echo "systemctl stop $SERVICES_LIST" >>$SS
    echo "echo 'Disabling services...'">>$SS
    echo "systemctl disable $SERVICES_LIST" >>$SS

    if [ $deployConfig -eq 1 ]; then
       echo "echo 'Deploying config...'">>$SS
       echo "cp -rf etc/* /etc">>$SS
    fi

    if [ $deployArduino -eq 1 ]; then
       echo "avrdude -q -V -D -p atmega328p -c arduino -b $A_BAUD -P $A_TTY Makefile Makefile -U flash:w: arduino.hex:i">>$SS
    fi


    echo "echo 'Removing target folder...'">>$SS

    echo "rm -rf $DEPLOY_FOLDER" >>$SS    
    echo "mkdir -p $DEPLOY_FOLDER" >>$SS    

    echo "echo 'Copying new binaries...'">>$SS

    echo "cp -raf * $DEPLOY_FOLDER">>$SS

    echo "echo 'Enabling new services...'">>$SS
    for item in $SERVICES_LIST; do
      echo "cp -raf $item/install/*  /lib/systemd/system/">>$SS
    done
    echo "systemctl daemon-reload">>$SS
    echo "systemctl enable $SERVICES_LIST">>$SS
    echo "echo 'Starting new services...'">>$SS
    echo "systemctl start  $SERVICES_LIST">>$SS


    echo "echo 'Executing custom-install-post...'">>$SS
    if [ -f install/custom-install.post.sh ];then
       cat install/custom-install.post.sh >> $SS
    fi
    echo "echo 'Ending in the egg...'">>$SS
   
    chmod +x $SS 
    #LET IT FOR DEBUGGING: echo "rm -rf $TMP_DEPLOY" >>$SS 
    

    if [ "$arg_dest" == "egg" ] || [ "$arg_dest" == "telegram" ] ; then
       #ZIP
       MYHOME=`pwd`
       pushd $TMP_DEPLOY
       tar zcvf "$MYHOME/eggSurprise.tgz" .
       popd 
       echo "EGG ready $TMP_DEPLOY" 
       #LET IT FOR DEBUGGING: "rm -rf $TMP_DEPLOY"     
    fi

    if [ "$arg_dest" == "telegram" ]  ; then
      echo "#-----------------------------------------------#"       
      echo "# Transfering the tarball egg via TELEGRAM..." 
      echo "#-----------------------------------------------#"      
      curl -F document=@"eggSurprise.tgz" https://api.telegram.org/bot$TELEGRAM_TOKEN/sendDocument?chat_id=$TELEGRAM_CHATID
    fi

    if [ "$arg_dest" == "remote" ]  ; then
      echo "#-----------------------------------------------#"       
      echo "# Transfering the files via SSH..." 
      echo "#-----------------------------------------------#"      
      scp -r -P $PI_PORT $TMP_DEPLOY $PI_USER@$PI_IPNAME:$TMP_DEPLOY
    fi


    if [ "$arg_dest" == "remote" ]  ; then
      echo "#-----------------------------------------------#"       
      echo "# Deploying remotely via SSH..." 
      echo "#-----------------------------------------------#"       
      ssh -p $PI_PORT pi@$PI_IPNAME "cd $TMP_DEPLOY; sudo ./eggSurprise.sh"

      echo "#-----------------------------------------------#"       
      echo "# Checking service status via SSH..." 
      echo "#-----------------------------------------------#"       
      ssh -p $PI_PORT pi@$PI_IPNAME "systemctl status $SERVICES_LIST -n 0"
    fi
  else
    echo "ERROR: no extra option selected for deployed remotely"
    usage
  fi
else
  echo "ERROR: no option selected for deployed"
  usage
fi
echo ""
echo ""
echo "-----------------    DONE    -------------------"
echo "------------------------------------------------"
echo "Deployment finished, check message above just in case something stinks... and have fun"
echo "  Remember cheatsheet:"
echo "    Check status: sudo systemctl status <service>"
echo "    Start service: sudo systemctl start <service>"
echo "    Stop service: sudo systemctl stop <service>"
echo "    Check service's log: sudo journalctl -f -u <service>"

