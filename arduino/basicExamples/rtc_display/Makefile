BOARD_TAG    = nano
MCU = atmega328p

ARDUINO_PORT = /dev/ttyUSB0
ARDUINO_LIBS = SoftwareSerial FastLed stringQueue lsem SimpleTimer EEPROM Adafruit_Sensor Low-Power DHT-sensor-library DHTsensor HCSR04sensor NonBlockingRTTTL/src Arduino-MedianFilter/src  RtttlTrackerList U8g2_Arduino SPI Wire RTClib Adafruit-GFX-Library Adafruit_SSD1306 Adafruit_BusIO

USER_LIB_PATH = $(realpath ../SCS/arduino)

AVRDUDE_ARD_BAUDRATE = 115200

ARDUINO_DIR=/home/jes/arduino-1.8.13
ARDMK_DIR=/usr/share/arduino



#Cheatsheet 
#CPPFLAGS -c pre procesor-, should be on for any compilation C or C++. Not for linking
#CXXFLAGS compiling and linking c++
#CFLAGS   compiling and linking c
#Some flags: -Os optimized in size, setup by default 
#Some flags: -O3 optimized in speed (others 1,2 available also)



############## CONDITIONAL COMPILATION
# LAMP_ENABLE_LSLIB
# LAMP_ENABLE_SERIAL_INPUT
# LAMP_DEBUG_STATES
# LAMP_DEBUG_HCSR04_MEDIAN
# LAMP_DEBUG_TEMPCOLOR
# LAMP_DEBUG_RTC
############## 
#CPPFLAGS+= -DLAMP_ENABLE_LSLIB
CPPFLAGS+= -DLAMP_DEBUG_STATES -DLAMP_DEBUG_RTC

include $(ARDMK_DIR)/Arduino.mk



