#!/bin/bash
#Note, considering both interfaces, typically only one conected

PKTSRX()
{
 cat /proc/net/dev | grep 'eth0\|wlan0' | awk '{SUM+=$2} END {printf "%0.f",SUM}'
}

echo $(PKTSRX)

