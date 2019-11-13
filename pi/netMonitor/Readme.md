Simple script that ping configurable server to check connectivity health.
A configurable action and timings can be setup also

Implemented partially a way to prioritize prefered ESSID vs OTHERS, however this is done by free by wpa_supplicant if wicd service is disable

Troubleshooting, to take place changes in wpa_supplicant file do:
systemctl reload-daemon
systemctl restart dhcpd
