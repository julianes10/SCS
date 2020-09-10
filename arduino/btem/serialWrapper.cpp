#include <Arduino.h>
#include <SoftwareSerial.h>
#include "serialWrapper.h"



serialWrapper::serialWrapper(bool hw,unsigned int bps,unsigned int rx,unsigned int tx, unsigned int toutsec)
{
  _serialInputStringReady = false;
  _serialIx=0;
  _debug=true;
  _hw=hw;

  if (! hw){
   _s=new SoftwareSerial(tx, rx);  
   _s->begin(bps);
  }

}
//-------------------------------------------------

int serialWrapper::send(char *text) {
  _s->println(text);
return 0;
}

//-------------------------------------------------

char *serialWrapper::readNB() {
  char *rt=0;
  int inChar=0;
  while (_s->available()) {
     //REMEMBER DO MINIMUN THINGS HERE, OTHERWISE YOU WILL LOSE RX CHARS
     if (_serialInputStringReady){
       Serial.println(F("Buffer overrun in BT")); //Lost char. Unprocessed previous string"));
       return;
     }

     inChar = _s->read();
     if ( (inChar < 0x20) || (_serialIx >= _MAX_INPUT_BUFFER)) {
       /*DEBUG Serial.print(F("Char Rx from <0x20"));
       Serial.println(inChar,HEX);*/
       _serialInputStringReady = true;
       _serialInputStringReady[_serialIx]=0;
       debugLocal=true;
       debugRemote=true;
       _serialIx=0;
       break;
     }
     _serialInputStringReady[_serialIx]=(char)inChar;
     /* DEBUG Serial.print(F("Char Rx from BT:"));
     Serial.print((char)inChar); 
     Serial.print(_serialInputStringReady[_serialIx]);
     Serial.print(F(". Pos:"));
     Serial.print(_serialIx); 
     _serialInputStringReady[_serialIx+1]=0;
     Serial.print(F(". So far:"));
     printString(_serialInputStringReady); */ 
     _serialIx++;
  }

  if (debugLocal)  printString(_serialInputStringReady);
  if (debugRemote) printStringBT(_serialInputStringReady);    

}





