#include <Arduino.h>

#include "DHTsensor.h"

DHTsensor::DHTsensor()
{
  dht=0;
  t=0;
  h=0;
}

int DHTsensor::setup(unsigned int datapin)
{
#ifdef DHTSENSOR_ENABLE_LOWCOST22
 dht=new DHT_lowfootprint();
 dht->setup(datapin);
#else
  dht=new DHT(datapin, DHT22); //// Initialize DHT sensor for normal 16mhz Arduino
  if (dht)
    dht->begin();
  else
    return -1;
  return 0;
#endif
}
int DHTsensor::refresh()
{
#ifdef DHTSENSOR_ENABLE_LOWCOST22
  h = dht->getHumidity();
  t = dht->getTemperature(); 
#else
  //Read data and store it to variables hum and temp
  h = dht->readHumidity();
  t = dht->readTemperature();
  if (isnan(h) || isnan(t))
    return 1;
  else
    return 0;
#endif
}




