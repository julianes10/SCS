/* BASED ON https://www.instructables.com/id/Non-blocking-Ultrasonic-Sensor-for-Arduino */
#include "HCSR04sensor.h"


HCSR04sensor *HCSR04sensor::_instance(NULL);

HCSR04sensor::HCSR04sensor(int trigger, int echo, int interrupt, int max_dist)
    : _trigger(trigger), _echo(echo), _int(interrupt), _max(max_dist), _finished(false)
{
  if(_instance==0) _instance=this;   
  _latestRead=0; 
}

void HCSR04sensor::setup(){
  pinMode(_trigger, OUTPUT);
  digitalWrite(_trigger, LOW);
  pinMode(_echo, INPUT);  
  attachInterrupt(_int, _echo_isr, CHANGE);
}

void HCSR04sensor::trigger(){
  _finished=false;
  digitalWrite(_trigger, HIGH);
  delayMicroseconds(10);
  digitalWrite(_trigger, LOW);  
}

unsigned int HCSR04sensor::getOngoingDistance(){
  unsigned int rt=0;
  if (_finished){
    _latestRead=(_end-_start)/(58);
    rt= _latestRead;
  }
  return rt;
}

void HCSR04sensor::_echo_isr(){
  HCSR04sensor* _this=HCSR04sensor::instance();
  
  switch(digitalRead(_this->_echo)){
    case HIGH:
      _this->_start=micros();
      break;
    case LOW:
      _this->_end=micros();
      _this->_finished=true;
      break;
  }   
}

int HCSR04sensor::refresh()
{
  int rt=-1;
  if (_finished) {
    rt=getOngoingDistance();  
    trigger(); 
  }
  return rt;
}


