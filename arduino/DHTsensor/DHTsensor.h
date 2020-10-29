/***********************************/
/* CONDITIONAL COMPILATION ITEMS   */
// DHTSENSOR_ENABLE_LOWCOST22
/***********************************/
#ifndef THSEM_h
#define THSEM_h

#include "Arduino.h"
#include "DHTsensor.h"

#ifdef DHTSENSOR_ENABLE_LOWCOST22
#include <DHT_lowfootprint.h>
#else
#include <Adafruit_Sensor.h>
#include <DHT.h>
#endif


class DHTsensor
{
 public:

  DHTsensor();
  int setup(unsigned int datapin);
  int refresh();
  float getTemperature(){return t;}
  float getHumidity(){return h;}

 private:
#ifdef DHTSENSOR_ENABLE_LOWCOST22
  DHT_lowfootprint *dht;

#else
 DHT *dht; 
#endif
 float t;
 float h;
};

#endif


