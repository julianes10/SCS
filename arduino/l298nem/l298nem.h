#ifndef L298NEM_h
#define L298NEM_h

#include "Arduino.h"



class L298NEM
{
 public:

  L298NEM(uint8_t ena,uint8_t in1,uint8_t in2,uint8_t enb,uint8_t in3,uint8_t in4);
  
  void forward();
  void backward();
  void stop();
  void left();
  void right();
  uint8_t speed(uint8_t s);

 private:


  // Motor A
  uint8_t _ENA;
  uint8_t _IN1;
  uint8_t _IN2;

  // Motor B
  uint8_t _ENB;
  uint8_t _IN3;
  uint8_t _IN4;

  uint8_t _speed;
  uint8_t _speedTurn;
};

#endif


