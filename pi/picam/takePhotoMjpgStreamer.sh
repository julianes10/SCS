#!/bin/bash 
theHost=$1
thePort=$2
outputFile=$3
wget http://$theHost:$thePort/?action=snapshot -O $outputFile

