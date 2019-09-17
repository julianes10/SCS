#!/bin/bash
#Note, considering both interfaces, typically only one conected

PKTSRX()
{
 cat /proc/net/dev | grep 'en' | awk '{SUM+=$2} END {printf "%0.f",SUM}'
}

echo $(PKTSRX)
