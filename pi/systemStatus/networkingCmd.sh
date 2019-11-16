#!/bin/bash 
echo "------------------------------"
echo "Interface settings"
echo "------------------------------"
echo "--All interfaces--"
ifconfig
echo "--WLAN interfaces--"
iwconfig
echo "--Preferred WLAN interfaces--"
cat /etc/wpa_supplicant/wpa_supplicant.conf | grep ssi

echo "------------------------------"
echo "Route settings"
echo "------------------------------"
ip r

