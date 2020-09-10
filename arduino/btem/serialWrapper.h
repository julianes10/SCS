#ifndef BTEM_h
#define BTEM_h

#include "Arduino.h"
#include <SoftwareSerial.h>
#include "serialWrapper.h"



class SerialWrapper
 public:

  SerialWrapper(bool hw);
  int send(char *text);
  char *readNB();

 private:
  SoftwareSerial *_s;
  bool _serialInputStringReady;
  char *_serialInputString;
  int _serialIx;
  int _MAX_INPUT_BUFFER;
  bool _debug;
  bool _hw;

};

#endif


