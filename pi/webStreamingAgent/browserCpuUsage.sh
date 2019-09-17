#!/bin/bash
browser="chromium"
ps -fea | grep -v grep| grep $browser >>/dev/null
if [ $? == 0 ]; then
  top -b -n 3 | grep $browser |  awk 'BEGIN {SUM=0} { SUM +=$9 } END { if (NR==0) print 0; else printf("%u",SUM/NR)}'
else
  echo "-1"
  exit -1
fi
exit 0
