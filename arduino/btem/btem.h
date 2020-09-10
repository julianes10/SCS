#ifndef BTEM_h
#define BTEM_h

#include "Arduino.h"
#include <SoftwareSerial.h>
#include "btem.h"

#define MAX_BT_RX_BUFFER 30

class btem
{
 public:

  btem();
  int setup(unsigned int rx,unsigned int tx,unsigned int toutsec);
  int setup(unsigned int v,unsigned int rx,unsigned int tx,unsigned int toutsec);
  int send(char *text);
  int send(unsigned int id,float t,float h);
  int sendWaitNewPeriod(unsigned int id,float t,float h);
  int sendKO(unsigned int id);
  char *refresh();
  void powerOn();
  void powerOff();

 private:
  SoftwareSerial *_bt;
  bool _serialInputStringReady;
  char _serialInputString[MAX_BT_RX_BUFFER];
  int _serialIx;
  int vcc;
  bool _debug;
 
};

#endif


