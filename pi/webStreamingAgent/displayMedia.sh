#!/bin/bash
## ONE SHOOT, NOT AGGREGATING TROUBLESHOOTING AND MONITORING
SS="/tmp/displayMedia.log"
echo "Starting $@..." | tee $SS
date | tee -a $SS

##################### PARSING ARGUMENTS ########################
ARGtimeout=0
ARGtimeoutSlideShow=0
ARGnosound=false
ARGreplaynumber=3

POSITIONAL=()
while [[ $# -gt 0 ]]
do
key="$1"

case $key in
    -u|--url)
    ARGurl="$2"
    shift # past argument
    shift # past value
    ;;
    -i|--image)
    ARGimage=true
    shift # past value
    ;;
    -d|--text)
    ARGtxt=true
    shift # past value
    ;;
    -v|--video)
    ARGvideo=true
    shift # past value
    ;;
    -y|--youtube-video)
    ARGurlYTvideo=true
    shift # past value
    ;;
    -s|--slideshow)
    ARGslideshow=true
    shift # past value
    ;;
    -w|--videoshow)
    ARGvideoshow=true
    shift # past value
    ;;
    -m|--mediashow)
    ARGmediashow=true
    shift # past value
    ;;
    -t|--timeout)
    ARGtimeout="$2"
    shift # past argument
    shift # past value
    ;;
    -r|--replaynumber)
    ARGreplaynumber="$2"
    shift # past argument
    shift # past value
    ;;
    -x|--timeoutslideshow)
    ARGtimeoutSlideShow="$2"
    shift # past argument
    shift # past value
    ;;
    -n|--nosound)
    ARGnosound=true
    shift # past value
    ;;
    *)    # unknown option
    POSITIONAL+=("$1") # save it in an array for later
    shift # past argument
    ;;
esac
done
set -- "${POSITIONAL[@]}" # restore positional parameters
#echo "Executing $0 with arguments: $@"
#echo "url     = ${ARGurl}"
#################################################################



##################### GLOBAL VARS SETUP ########################
browser="chromium-browser"
#browser="firefox"

if [ "$#" -gt 1 ]; then
  ARGtimeout=$2
fi

# Run this script in display 0 - the monitor
export DISPLAY=:0

#################################################################


##################### FUNCTIONS  ########################
#---------------------------------------------------------
function chromiumPiCleanUp() {
  # If Chromium crashes (usually due to rebooting), clear the crash flag so we don't have the annoying warning bar
  sed -i 's/"exited_cleanly":false/"exited_cleanly":true/' /home/pi/.config/chromium/Default/Preferences 1> /dev/null 2>/dev/null 
  sed -i 's/"exit_type":"Crashed"/"exit_type":"Normal"/' /home/pi/.config/chromium/Default/Preferences 1> /dev/null 2>/dev/null 
}
#---------------------------------------------------------
function killdisplay() {
  pkill -f $browser
  killall $browser

  pid=`ps -fea | grep $browser | grep -v grep | awk '{print $2}'`
  re='^[0-9]+$'
  if  [[ $pid =~ $re ]] ; then
    kill $pid
  fi

  pkill -f mplayer
  killall mplayer

  pkill -f omxplayer
  killall omxmplayer

  pkill -f feh
  killall feh



  pid=`ps -fea | grep mplayer | grep -v grep | awk '{print $2}'`
  re='^[0-9]+$'
  if  [[ $pid =~ $re ]] ; then
    kill $pid
  fi

  pid=`ps -fea | grep omxplayer | grep -v grep | awk '{print $2}'`
  re='^[0-9]+$'
  if  [[ $pid =~ $re ]] ; then
    kill $pid
  fi


  pid=`ps -fea | grep feh | grep -v grep | awk '{print $2}'`
  re='^[0-9]+$'
  if  [[ $pid =~ $re ]] ; then
    kill $pid
  fi


}

#---------------------------------------------------------
function prepareHTML() {
  url=$1
  file=$2
  cat >$file<<EOL
  <html>
   <head>
    <style>
     img {
          border: 1px solid blue;
          min-height: 98%;
          max-width: 99%;
          max-height: 98%;
          width: auto;
          height: auto;
          position: absolute;
          top: 0;
          bottom: 0;
          left: 0;
          right: 0;
          margin: auto;
        }
    </style>
   </head>
  <body>
  <div>
      <img src='$url'>
  </div>
  </body>
  </html>
EOL
}

#---------------------------------------------------------
function prepareHTMLtxt() {
  txt=$1
  file=$2
  cat >$file<<EOL
  <html>
   <head>
    <style>
     p {
          font-size: 10vh;
          font-size: 10vw;
        }
    </style>
   </head>
  <body style="background-color:lightgreen;">
  <div>
    <p>
      $txt
  </div>
  </body>
  </html>
EOL
}



#---------------------------------------------------------
function prepareHTMLvideo() {
  url=$1
  file=$2
  cat >$file<<EOL
  <html>
  <head>
    <script>
     function playIt() {  
        item=document.getElementsByTagName('video')[0]
        item.load();
        item.play();        
     }

     function manageLoop() {  
        playIt()
        document.getElementsByTagName('video')[0].onended = playIt
     }
    </script>
    <style>
     video {
          border: 1px solid blue;
          min-height: 98%;
          max-width: 99%;
          max-height: 98%;
          width: auto;
          height: auto;
          position: absolute;
          top: 0;
          bottom: 0;
          left: 0;
          right: 0;
          margin: auto;
        }
    </style>
  </head>
  <body onLoad="manageLoop()">
   <video controls>
    <source src='$url' type="video/mp4">
    NO PUEDORRR.
  </video>
  </body>
  </html>
EOL
}



#---------------------------------------------------------
function renderHTML() {
  file=$1
  $browser  --start-maximized --pi $file &
  sleep 2
  xdotool search --onlyvisible --name "Chromium" windowfocus key F11
}

#---------------------------------------------------------
function renderHTMLvideo() {
  file=$1
  $browser  --autoplay-policy=no-user-gesture-required --start-maximized --pi $file &
  sleep 2
  xdotool search --onlyvisible --name "Chromium" windowfocus key F11
}

#---------------------------------------------------------
function renderMplayerVideo() {
  ############## BLOCKING ################
  file=$1
  argSound=""
  if [ $ARGnosound == true ]; then
    argSound="-nosound"
  fi
  for (( i = 0; i < $ARGreplaynumber; i++ )); do
    echo "### DEBUG playing video - $ARGnosound-$argSound - $i times. " | tee -a $SS
    mplayer -fs -zoom $argSound $file 
    checkIfExit
  done
}


#---------------------------------------------------------
function renderVideo() {
  ############## BLOCKING ################
  file=$1
  for (( i = 0; i < $ARGreplaynumber; i++ )); do
    echo "### DEBUG playing video $file, $i out of $ARGreplaynumber times. " | tee -a $SS
    omxplayer $file 
    checkIfExit
  done
}

#---------------------------------------------------------
function renderYTVideo() {
  ############## BLOCKING ################
  # Check latest https://github.com/ytdl-org/youtube-dl
  omxplayer -o hdmi $(youtube-dl -g $1)
}

#---------------------------------------------------------
function renderVideos() {
  ############## BLOCKING ################
  echo "### DEBUG playing videos from $1..." | tee -a $SS
  for i in $1/*
  do
    if test -f "$i" 
    then
       echo "### DEBUG playing video: $i..." | tee -a $SS
       omxplayer $i 
       checkIfExit
    fi
  done
}

#---------------------------------------------------------
function renderImages() {
  ############## BLOCKING ################
  echo "### DEBUG playing slideshow each image 4 seconds from $1... "  | tee -a $SS
  file=$1
#  feh -Y -x -q -Z -z -F --cycle-once -D 7 $file
  feh -Y -x -q -Z -z -F --on-last-slide quit -D 4 $file


}

#---------------------------------------------------------
function renderImage() {
  echo "### DEBUG playing image $1... "  | tee -a $SS
  file=$1
  feh -Y -x -q -Z -z -F $file  &
}
#---------------------------------------------------------
function renderMplayerVideoShow() {
  ############## BLOCKING ################
  path=$1
  argSound=""
  if [ $ARGnosound == true ]; then
    argSound="-nosound"
  fi
  for (( i = 0; i < $ARGreplaynumber; i++ )); do
    echo "### DEBUG playing video show - $ARGnosound-$argSound - $i times"   | tee -a $SS
    mplayer -fs -zoom $argSound $path/*
    checkIfExit
  done
}

#---------------------------------------------------------
function manageTimeout() {
  tout=$1
  if [ "$tout" == "0" ]; then
    echo "DEBUG no timeout"
  else
    ############## BLOCKING ################
    echo "DEBUG sleeping $tout ..."  | tee -a $SS
    sleep $tout
    killdisplay
    chromiumPiCleanUp
  fi
}

#---------------------------------------------------------
function generateSlideShow() {
  path=$1
  output=$2 
  convert -delay 500 -loop 0 $path/*.jpg $output 
}

#---------------------------------------------------------
function usage() {
  if [ ! -f /tmp$path  ]; then
    path=`dirname $ARGurl`
  fi
}

#---------------------------------------------------------
function checkIfExit() {
  runninPID=`cat /tmp/displayMedia_pid`

  if [ "$runninPID" == "$myPID" ]; then
    echo "### DEBUG still the only one. Cool"
  else
    echo "### DEBUG I must die now, other fresher is running. Bye"  | tee -a $SS
    exit
  fi

}


#---------------------------------------------------------
function getActiveSourceHDMI() {
  echo 'as' | cec-client -s -d 1
}




##########################################################


myPID=`echo $$` 
echo $myPID >/tmp/displayMedia_pid
killdisplay
chromiumPiCleanUp
checkIfExit





echo "DEBUG starting $0 game...."  | tee -a $SS
getActiveSourceHDMI

if [ $ARGtxt ]; then
  echo "DEBUG showing a text: $ARGurl ..."  | tee -a $SS
  prepareHTMLtxt "$ARGurl" /tmp/txt.html
  renderHTML /tmp/txt.html
  manageTimeout $ARGtimeout
fi


if [ $ARGimage ]; then
  echo "DEBUG showing an image: $ARGurl ..."  | tee -a $SS
  #prepareHTML $ARGurl /tmp/image.html
  #renderHTML /tmp/image.html
  renderImage $ARGurl
  manageTimeout $ARGtimeout
fi


if [ $ARGvideo ]; then
  echo "DEBUG showing an video: $ARGurl ..."  | tee -a $SS
  ## renderMplayerVideo $ARGurl
  renderVideo $ARGurl
fi

if [ $ARGurlYTvideo ]; then
  echo "DEBUG showing an video from youtube: $ARGurl ..."  | tee -a $SS
  ## renderYTVideo $ARGurl
  renderYTVideo $ARGurl
fi


if [ $ARGslideshow ]; then
  path=$ARGurl
  if [ ! -d $path  ]; then
    path=`dirname $ARGurl`
  fi
  echo "DEBUG showing slideshow: $path ..."  | tee -a $SS
  #not needed with feh generateSlideShow $path  /tmp/image.gif
  #not needed with feh prepareHTML /tmp/image.gif /tmp/image.html
  #not needed with feh renderHTML /tmp/image.html manageTimeout $ARGtimeoutSlideShow
  renderImages $path
  checkIfExit
fi

if [ $ARGvideoshow ]; then
  path=$ARGurl
  if [ ! -d $path  ]; then
    path=`dirname $ARGurl`
  fi
  echo "DEBUG showing videoshow: $path ..."  | tee -a $SS
  # too slow when zoom renderMplayerVideoShow $path
  renderVideos $path
fi

if [ $ARGmediashow ]; then
  ############## BLOCKING ################
  p=$ARGurl
  if [ ! -d $p  ]; then
    pp=`dirname $ARGurl`
    p=`dirname $pp`
  fi

  echo "DEBUG showing mediashow: $p ..."  | tee -a $SS
  pathVideo=$p/video
  pathPhoto=$p/photo

  #generateSlideShow $pathPhoto  /tmp/image.gif
  #prepareHTML /tmp/image.gif /tmp/image.html

  while  [ true ]
  do
    date | tee -a $SS
    ## to slow renderMplayerVideoShow $pathVideo
    renderVideos $pathVideo
    checkIfExit
    date | tee -a $SS
    #renderHTML /tmp/image.html      manageTimeout $ARGtimeoutSlideShow
    renderImages $pathPhoto
    checkIfExit
  done
  ############## BLOCKING ################
fi

echo "DEBUG Exiting."  | tee -a $SS
#unclutter &
exit 0
