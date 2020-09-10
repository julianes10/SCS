#include <Arduino.h>
#include <SoftwareSerial.h>
#include "btem.h"



btem::btem()
{
  vcc=-1;
  _serialInputStringReady = false;
  _serialIx=0;
  _debug=true;

}

int btem::setup(unsigned int v,unsigned int rx,unsigned int tx, unsigned int toutsec)
{
  vcc=v;
  pinMode(vcc, OUTPUT); 
  powerOn();
  return this->setup(rx,tx,toutsec);
}

int btem::setup(unsigned int rx,unsigned int tx, unsigned int toutsec)
{
  // WORKING _bt=new SoftwareSerial(10, 11);
  // NOTE Rx pin _bt is my arduino serial TX
  // NOTE Tx pin _bt is my arduino serial RX
  _bt=new SoftwareSerial(tx, rx); // SoftwareSerial(rxPin, txPin, inverse_logic)
  _bt->begin(9600);
  _bt->setTimeout(toutsec*1000);
  if (_bt!=0) return 0;
  return 1;
}
int btem::send(char *text) {
  _bt->println(text);
return 0;
}

int btem::send(unsigned int id,float t,float h) {
  _bt->print("{\"id\":\"id");
  _bt->print(id);
  _bt->print("\",\"status\":\"");
  _bt->print("OK");
  _bt->print("\",\"data\":{\"t\":\"");
  _bt->print(t);
  _bt->print("\",\"h\":\"");
  _bt->print(h);
  _bt->println("\"}}");

return 0; //TODO
}

int btem::sendWaitNewPeriod(unsigned int id,float t,float h) {
  String s="";
  this->send(id,t,h);
  s=_bt->readString();
  
return s.toInt(); 
}

int btem::sendKO(unsigned int id) {    
  String s="";
  _bt->print("{\"id\":\"id");
  _bt->print(id);
  _bt->print("\",\"status\":\"");
  _bt->print("KO");
  _bt->println("\"}");
  s=_bt->readString();
  return s.toInt();
}

void btem::powerOn()
{
  if (this->vcc >= 0) {
    digitalWrite(vcc,HIGH);
    delay(5000);
  }
}

void btem::powerOff()
{
  if (this->vcc >= 0) {
    delay (5000);
    digitalWrite(vcc,LOW);
  }
}

char *btem::refresh() {
  char *rt=0;

  if (_debug){ Serial.println(F("DEBUG: BT refresh...******"));}


  String s="";
  s=_bt->readString();
  return s.c_str();

  while (_bt->available()) {
     if (_debug){ Serial.println(F("DEBUG: BT available..."));}
     char inChar = (char)_bt->read();
     if (_debug){ Serial.print(F("DEBUG: BT rx char: ")); Serial.println(inChar);}


     if ( (inChar < 0x20) || 
          ( (_serialIx+1) >= MAX_BT_RX_BUFFER))
     {
       _serialInputStringReady = true;
       _serialInputString[_serialIx]=0;
       _serialIx=0;
       rt=_serialInputString;
       if (_debug){
         Serial.print(F("DEBUG: BT rx string: "));
         Serial.println(_serialInputString);
       }
     }
     _serialInputString[_serialIx++]=inChar;      

  }







  return rt;
}




