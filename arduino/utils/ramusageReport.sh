ELF=$1

echo "RAM REPORT"
/usr/share/arduino/hardware/tools/avr/bin/nm -Crtd --size-sort $ELF | grep -i " [dbv] "

echo "CODE REPORT"
/usr/share/arduino/hardware/tools/avr/bin/nm -Crtd --size-sort $ELF | grep -i " [t] "
