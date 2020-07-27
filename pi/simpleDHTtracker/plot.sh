#!/bin/bash

if [ "$1" == "-h" ];then
  echo "Usage: $0 <inputfile> <outputfile> [opt] [aux]"
  echo "  Where opt:"
  echo "    raw: show all data without xranges"
  echo "    today: show all data gather today"
  echo "    ntoday: show all data gather today until now"
  echo "    h: show all data gather in latest <aux> hours, counting backwards since last sample"
  echo "    nh: show all data gather in latest <aux> hours, counting backwards since now"
fi


inputFile="$1"
outputFile="$2"
opt="$3"
hours="$4"
if [ "$hours" == "" ]; then
  hours=24
fi

myTitle="Temperature and Humidity"

offset_tz=`echo "$(date +%z) * 36" | sed 's/\+//g' | bc`

# rest of script, after gnuplot exits

#------------------------------------------
function show_raw()
{
gnuplot <<-EOFMarker
    set title "$myTitle" font ",14" textcolor rgbcolor "royalblue"
    set timefmt "%s"
    set xdata time
    set format x "%d-%H:%M"
    set pointsize 1
    set term png
    set output "$outputFile"
    set grid
    set y2tics nomirror
    set ytics nomirror
    set autoscale  y 
    set autoscale y2 
    set style line 1 lt rgb "red" lw 3 pt 6
    set style line 2 lt rgb "blue" lw 2 pt 6
    set xtics rotate by 60 right
    set y2label "Temperature Celsius"
    set ylabel  "Humidity %"
    plot "$inputFile" using (column(1) + $offset_tz):2 title "Temperature" with line axes x1y2 ls 1, "$inputFile" using (column(1) + $offset_tz):3 title "Humidity"  with line axes x1y1 ls 2
EOFMarker
}
#------------------------------------------
function show_ranges()
{ 
gnuplot <<-EOFMarker
    set title "$myTitle" font ",14" textcolor rgbcolor "royalblue"
    set timefmt "%s"
    set autoscale  y
    set autoscale y2
    set y2tics nomirror
    set ytics nomirror
    set xrange [$xrange1:$xrange2]
    set xdata time
    set format x "%d-%H:%M"
    set pointsize 1
    set term png
    set output "$outputFile"
    set grid
    set xtics rotate by 60 right
    set style line 1 lt rgb "red" lw 3 pt 6
    set style line 2 lt rgb "blue" lw 2 pt 6
    set y2label "Temperature Celsius"
    set ylabel  "Humidity %"
    plot "$inputFile" using (column(1) + $offset_tz):2 title "Temperature" with line axes x1y2 ls 1, "$inputFile" using (column(1) + $offset_tz):3 title "Humidity"  with line axes x1y1 ls 2
EOFMarker
}


xrange1_dft=`head -2 $inputFile | awk '{print $1}' | tail -1`
xrange2_dft=`tail -1 $inputFile | awk '{print $1}'`

todayBegin=`date -d "$(date +"%D")" +"%s"`

nowtime=`date +"%s"`
if [ "$opt" == "today" ]; then
  xrange1=$todayBegin
  xrange2=$xrange2_dft
elif [ "$opt" == "h" ]; then
  xrange1=$((xrange2_dft-hours*3600))
  xrange2=$xrange2_dft
elif [ "$opt" == "ntoday" ]; then
  xrange1=$todayBegin
  xrange2=$nowtime
elif [ "$opt" == "nh" ]; then
  xrange1=$((nowtime-hours*3600))
  xrange2=$nowtime
else
  xrange1=$xrange1_dft
  xrange2=$xrange2_dft
fi

xrange1=$((xrange1 + offset_tz))
xrange2=$((xrange2 + offset_tz))

### DEBUG echo "Showing DHT (option $opt). Range $xrange1 $xrange2"

if [ "$opt" == "raw" ]; then
  show_raw
else
  show_ranges
fi
# DEBUG display $outputFile &

