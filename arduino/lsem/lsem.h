#ifndef LSEM_h
#define LSEM_h

#include "Arduino.h"
#include "FastLED.h"
#include "SimpleTimer.h"
#include "stringQueue.h"

#define NUM_MAX_QUEUE 5
#define MAX_PATTERNS  10
//-------------
/*
EM SERIAL PROTOCOL, INEFFICIENT,UNSECURE, BUT EASY TO READ, QUICK TO IMPLEMENT AND TEST:
:<TYPE>[<SUBTYPE>|<VALUE><SUBTYPE>|<VALUE>...] ;[more commands....]...\n
TYPES:
*/
  #define TYPE_LED    'L' // (led strip protocol id default identifier)
// For subtypes of leds see and protocol details go to  _h
//SUBTYPES led strip PROTOCOL
  #define LS_RESET   'X'  // off led strip and reset any variable to default
  #define LS_COLOR   'C'  // (color) with VALUE:RGB in 8 ascii hexadecimal RR,GG,BB
                          //    e.g 66,AB,4F. All led set to this color. Default 00,00,00
  #define LS_TIMEOUT 'T'  // (timeout) with VALUE:DS in 4 ascii in decs of seconds filled with zeros 
                          //    e.g 0300, 30 seconds. Default 0 NO timeout
  #define LS_PAUSE   'P'  // (pause)   with VALUE:MS in 4 ascii in decs of seconds filled with zeors 
                          //    e.g 4000, 4  seconds. Default 0 no pause
  #define LS_PERCENTAGE 'G'  // (percentage) 0-100%  4 ascii  filled with zeors 
                          //    e.g 0050, 50 %. Default 0 no impact.
  #define LS_DEBUG_ON  'D'// Enable debug
  #define LS_DEBUG_OFF 'd' // Disable debug
  #define LS_STATUS_REQ 'S'  // Ask for status information over this serial protocol answer TODO spec output

  #define LS_MODE    'M'  // (mode) with <SUBTYPE>
    #define LS_MODE_ZERO           '0'  // no mode. All leds forced to black. Standby.
    #define LS_MODE_COLOR          'A'  // (all) setup all leds with general settings: C,T,P.
    #define LS_MODE_ROLLING_TEST   'T'  // rolling 3 test colors. With general settings: T,P.
    #define LS_MODE_RROLLING_TEST  't'  // reverse rolling 3 test colors. With general settings: T,P.
    #define LS_MODE_ROLLING_COLOR  'C'  // rolling bit With general settings: C,T,P.
    #define LS_MODE_RROLLING_COLOR 'c'  // reverse rolling bit With general settings: C,T,P.
    #define LS_MODE_ONE            'O'  //(1 led bit change) with VALUE:LED_POSITION 2 ascii decimal 
                                       //  e.g 00 or 40. With general settings: C,T,P.
    #define LS_MODE_RAINBOW        'W'  //rainbow. With general settings: T.
    #define LS_MODE_NOISE          'N'  //random leds random color. With general settings: T,P
    #define LS_MODE_NOISE_COLOR    'n'  //random leds fixed color. With general settings: T,P,C
    #define LS_MODE_KNIGHT_RIDER   'K'  //knight rider effect. With general settings: T,P,C
    #define LS_MODE_RKNIGHT_RIDER  'k'  //reverse knight rider effect. With general settings: T,P,C
    #define LS_MODE_PATTERNS       'P'  //put configured patters VALUE:POSITION 2 ascii decimal. With general settings: T,P
  #define LS_ENQUEUE 'Q'  // Enqueue the rest of the line commands to play when timeout current mode.

  #define LS_PATTERN    'p'  // (pattern operation) over position POSITION 2 ascii decimal,COLOR0,COLOR1,COLOR...
    #define LS_PATTERN_DEF_ZOOM        'Z'  // N leds, later zoom in strip
    #define LS_PATTERN_DEF_MOSAIC      'M'  // N leds, later mosaic in strip



class LSEM
{
 public:
  LSEM(CRGB *ls,uint8_t m, timer_callback cbp,timer_callback cbt);

  void refresh();

  void reset();
  int processCommands(char *inputString);
  int processCommands(const char PROGMEM *inputString);
  bool isIdle(){return ((_mode==LS_MODE_ZERO) && (_queue.count()==0)); }

  void callbackTimeout();
  void callbackPause();

  bool getDebug()       {return _debug;}
  void setDebug(bool b);

  void customProtocolId(char p){_ProtocolId=p;}

  void setPattern(uint8_t pos,CRGB *p);

 private:
  char _auxBuff[100];
  char _ProtocolId;
  CRGB *_leds;
  CRGB *_patternsList[MAX_PATTERNS];
  uint8_t _maxPatterns;
  uint8_t _currentPattern;  
  stringQueue _queue;
  char _mode;
  uint8_t _one;
  CRGB _color; //C
  SimpleTimer _timers;
  int _rollingTurn;
  CRGB _rollingTestColor;
  int _direction;
  bool _debug;
  uint8_t _NUM_LEDS;

  int  _timeout; //T
  int  _pause; //P
  int  _timerTimeout; 
  int  _timerPause; 
  int  _percentage; 
  bool _timeoutExpired;
  bool _pauseExpired;

  timer_callback _cbt;
  timer_callback _cbp;


  void _setMode(char m);
  char _getMode(){return _mode;}
  void _setColor(uint32_t c);
  void _setLed(uint8_t led);
  void _setMaxPatterns(uint8_t p){ _maxPatterns=p; }
  void _setTimeout(uint16_t t);
  void _setPause(uint16_t p);
  void _setPercentage(uint16_t p);
  void _resetQueue();
  void _fullReset();
  uint8_t _readSerialCommand(char *cmd,int *pok);
  void _debugInfo();
  void _doRollingTest(bool reverse=false);
  void _doRollingColor(CRGB color,bool reverse=false,bool knightRider=false);
  void _doOne();
  void _doColor();
  void _doRainbow();
  void _doNoise();
  void _doNoiseColor();
  void _doPatterns();
  void _setAllLeds(CRGB color);
  void _setPatternDef(uint8_t pos, uint8_t mode, CRGB *p, int max);
  uint32_t _readColor(char *cmd);

};

//extern class LSEM LSEM;
#endif


