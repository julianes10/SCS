#ifndef carEngine_h
#define carEngine_h

#include "l298nem.h"
#include "stringQueue.h"
#include "Arduino.h"


//-------------
/*
EM SERIAL PROTOCOL, INEFFICIENT,UNSECURE, BUT EASY TO READ, QUICK TO IMPLEMENT AND TEST:
:<TYPE>[<SUBTYPE>|<VALUE><SUBTYPE>|<VALUE>...] ;[more commands....]...\n
TYPES:
*/
  #define TYPE_ENGINE    'E'  
// For subtypes of leds see and protocol details go to  _h
//SUBTYPES led strip PROTOCOL
  #define E_DEBUG_ON  'D' // Enable debug
  #define E_DEBUG_OFF 'd' // Disable debug
  #define E_STATUS_REQ 'S'  // Ask for status information over this serial protocol answer TODO spec output
  #define E_SPEED   's'  // (speed, 3 digits 0-255
  #define E_GAS 'G'  // Accelerate a bit
  #define E_BRAKE 'B'  // Brake a bit
  #define E_LEFT  'L'  // move slight left and continue
  #define E_RIGHT 'R'  // move slight right and continue
  #define E_UTURN   'U'  // make uturn turning left and continue

  #define E_MODE    'M'  // (mode) with <SUBTYPE>
    #define E_MODE_ZERO          '0'  // no mode. Stopped. Standby.
    #define E_MODE_STOP           'S'  // motor stopped
    #define E_MODE_FORWARD        'F'  // move forward
    #define E_MODE_BACKWARD       'B'  // move backward
    #define E_MODE_LEFT          'L'  // turn left continuosly
    #define E_MODE_RIGHT         'R'  // turn right continuosly
  #define E_ENQUEUE 'Q'  // Enqueue the rest of the line commands to play when timeout current mode.


class CarEngine
{
 public:

  CarEngine();

  void refresh();
  void processCommands(char *inputString);
  void setDebug(bool b);
  bool getDebug()       {return _debug;}
  void reset();




 private: 
  L298NEM _frontWheels;
  //L298NEM _backWheels; 
  stringQueue _queue;
  char _mode;
  uint8_t _speed;
  bool _debug;

  void _debugInfo();
  void _fullReset(void);

  void _setMode(char m);
  char _getMode(){return _mode;}
  void _resetQueue();
  uint8_t _readSerialCommand(char *cmd);

  void _doForward();
  void _doBackward();
  void _doStop();
  void _doLeft();
  void _doRight();

  void _setSpeed(uint8_t s);
  void _brake();
  void _gas();
  void _uTurn();
  void _slightLeft();
  void _slightRight();


};

#endif


