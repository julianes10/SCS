#!/bin/bash



##################### PARSING ARGUMENTS ########################
ARGtimeout=0
ARGtimeoutSlideShow=0

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
    -v|--video)
    ARGvideo=true
    shift # past value
    ;;
    -s|--slideshow)
    ARGslideshow=true
    shift # past value
    ;;
    -t|--timeout)
    ARGtimeout="$2"
    shift # past argument
    shift # past value
    ;;
    -x|--timeoutslideshow)
    ARGtimeoutSlideShow="$2"
    shift # past argument
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
  pid=`ps -fea | grep "/tmp/image.html" | grep -v grep | awk '{print $2}'`
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
          * {
              margin: 0;
              padding: 0;
          }
          .imgbox {
              display: grid;
              height: 100%;
          }
          .center-fit {
              max-width: 100%;
              max-height: 100vh;
              margin: auto;
          }
      </style>
  </head>
  <body>
  <div class="imgbox">
      <img class="center-fit" src='$url'>
  </div>
  </body>
  </html>
EOL
}

#---------------------------------------------------------
function renderHTML() {
  file=$1
  $browser  --start-maximized --pi $file &
  sleep 1
  xdotool search --name "Chromium" windowfocus key 'ctrl+r'
  xdotool key F11
}

#---------------------------------------------------------
function manageTimeout() {
  tout=$1
  if [ "$tout" == "0" ]; then
    echo "DEBUG no timeout"
  else
    echo "DEBUG sleeping $tout ..."
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
  echo "Options:
    -u|--url URL
    -i|--image
    -v|--video
    -s|--slideshow
    -t|--timeout SECONDS applicable to image
    -x|--timeoutslideshow SECONDS applicable to slideshow
  "

}
##########################################################

killdisplay
chromiumPiCleanUp


echo "DEBUG starting the game...."
if [ $ARGimage ]; then
  echo "DEBUG showing an image: $ARGurl ..."
  prepareHTML $ARGurl /tmp/image.html
  renderHTML /tmp/image.html
  manageTimeout $ARGtimeout
fi


if [ $ARGslideshow ]; then
  path=$ARGurl
  if [ ! -d $path  ]; then
    path=`dirname $ARGurl`
  fi
  echo "DEBUG showing slideshow: $path ..."
  generateSlideShow $path  /tmp/image.gif
  prepareHTML /tmp/image.gif /tmp/image.html
  renderHTML /tmp/image.html
  manageTimeout $ARGtimeoutSlideShow
fi

unclutter &
exit 0
