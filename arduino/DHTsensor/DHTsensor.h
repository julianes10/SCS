#ifndef THSEM_h
#define THSEM_h

#include "Arduino.h"
#include "DHTsensor.h"
#include <Adafruit_Sensor.h>
#include <DHT.h>


class DHTsensor
{
 public:

  DHTsensor();
  int setup(unsigned int datapin);
  int refresh();
  float getTemperature(){return t;}
  float getHumidity(){return h;}

 private:
 DHT *dht; 
 float t;
 float h;
};

#endif


