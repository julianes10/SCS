#!/bin/bash
#CHECK https://blog.vpetkov.net/2019/07/12/netflix-and-spotify-on-a-raspberry-pi-4-with-latest-default-chromium/
url=$1
x=$2
y=$3
tout=$4

echo "Executing $0 with arguments: $@"

browser="chromium-browser"
pkill -f $browser
killall $browser


#Note setup visudo first
#<yourusername> ALL=NOPASSWD: <command1>, <command2>
#pi ALL=NOPASSWD: swapoff, swapoff TODO
#sudo swapoff -a
#sudo swapon -a

if [ "$1" == "STOP" ]; then
  echo "$browser has been closed"
  exit 0
fi

#---------------------------------------------------------
function clickAroundMini() {
  x=$1
  y=$2
  delta=10
  xdotool mousemove $x $y
  xdotool click 1

  xx=$((x+d))
  yy=$((y))
  xdotool mousemove $xx $yy
  xdotool click 1

  xx=$((x))
  yy=$((y+d))
  xdotool mousemove $xx $yy
  xdotool click 1

  xx=$((x-d))
  yy=$((y))
  xdotool mousemove $xx $yy
  xdotool click 1

  xx=$((x))
  yy=$((y-d))
  xdotool mousemove $xx $yy
  xdotool click 1

}

#---------------------------------------------------------
function clickAround() {
  x=$1
  y=$2
  d=40

  clickAroundMini $x $y

  xx=$((x+d))
  yy=$((y))
  clickAroundMini $xx $yy
  xx=$((x))
  yy=$((y+d))
  clickAroundMini $xx $yy

  xx=$((x-d))
  yy=$((y))
  clickAroundMini $xx $yy
  xx=$((x))
  yy=$((y-d))
  clickAroundMini $xx $yy

}
#---------------------------------------------------------


# Run this script in display 0 - the monitor
export DISPLAY=:0
 
# Hide the mouse from the display
# NOT SEEM TO WORK OK unclutter &
 
# If Chromium crashes (usually due to rebooting), clear the crash flag so we don't have the annoying warning bar
sed -i 's/"exited_cleanly":false/"exited_cleanly":true/' /home/pi/.config/chromium/Default/Preferences
sed -i 's/"exit_type":"Crashed"/"exit_type":"Normal"/' /home/pi/.config/chromium/Default/Preferences
 
$browser --start-maximized --pi $url &

sleep 2
xdotool search --name "Chromium" windowfocus key 'ctrl+r'
sleep 2
xdotool key F11
sleep $tout



xdotool key space
sleep 10
xdotool mousemove $x $y
xdotool click 1

unclutter &

exit 0
