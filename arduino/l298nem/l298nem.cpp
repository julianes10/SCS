#include <Arduino.h>

#include "l298nem.h"


#define DEFAULT_SPEED 200
#define DEFAULT_TURN_SPEED 150



//------------------------------------------------
//------------------------------------------------
//------------------------------------------------
L298NEM::L298NEM(uint8_t ena,uint8_t in1,uint8_t in2,uint8_t enb,uint8_t in3,uint8_t in4)
{
  // Motor A
  _ENA = ena;
  _IN1 = in1;
  _IN2 = in2;

  // Motor B
  _ENB = enb;
  _IN3 = in3;
  _IN4 = in4;

  _speed = DEFAULT_SPEED;
  _speedTurn = DEFAULT_TURN_SPEED;

  pinMode (_ENA, OUTPUT);
  pinMode (_ENB, OUTPUT);
  pinMode (_IN1, OUTPUT);
  pinMode (_IN2, OUTPUT);
  pinMode (_IN3, OUTPUT);
  pinMode (_IN4, OUTPUT);
}
//------------------------------------------------
void L298NEM::backward ()
{
  //Direccion motor A
  digitalWrite (_IN1, LOW);
  digitalWrite (_IN2, HIGH);
  analogWrite (_ENA, _speed); //Velocidad motor A
  //Direccion motor B
  digitalWrite (_IN3, LOW);
  digitalWrite (_IN4, HIGH);
  analogWrite (_ENB, _speed); //Velocidad motor B

}
//------------------------------------------------
void L298NEM::forward ()
{
  //Direccion motor A
  digitalWrite (_IN1, HIGH);
  digitalWrite (_IN2, LOW);
  analogWrite (_ENA, _speed);  //Velocidad motor A
  //Direccion motor B
  digitalWrite (_IN3, HIGH);
  digitalWrite (_IN4, LOW);
  analogWrite (_ENB, _speed);
}
//------------------------------------------------
void L298NEM::right ()
{
  //Direccion motor A
  digitalWrite (_IN1, LOW);
  digitalWrite (_IN2, HIGH);
  analogWrite (_ENA, _speedTurn); //Velocidad motor A
  //Direccion motor B
  digitalWrite (_IN3, HIGH);
  digitalWrite (_IN4, LOW);
  analogWrite (_ENB, _speedTurn); //Velocidad motor A
}
//------------------------------------------------
void L298NEM::left ()
{
  //Direccion motor A
  digitalWrite (_IN1, HIGH);
  digitalWrite (_IN2, LOW);
  analogWrite (_ENA, _speedTurn); //Velocidad motor A
  //Direccion motor B
  digitalWrite (_IN3, LOW);
  digitalWrite (_IN4, HIGH);
  analogWrite (_ENB, _speedTurn); //Velocidad motor A

}
//------------------------------------------------
void L298NEM::stop ()
{
  //Direccion motor A
  digitalWrite (_IN1, LOW);
  digitalWrite (_IN2, LOW);
  analogWrite (_ENA, 0); //Velocidad motor A
  //Direccion motor B
  digitalWrite (_IN3, LOW);
  digitalWrite (_IN4, LOW);
  analogWrite (_ENB, 0); //Velocidad motor A
}
//------------------------------------------------
uint8_t L298NEM::speed (uint8_t s)
{
  analogWrite (_ENA, s); 
  analogWrite (_ENB, s); 
  _speed=s;
  _speedTurn = s; //TODO not sure fixed speed on turn helps
  return _speed;
}

