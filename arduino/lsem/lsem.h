/***********************************/
/* CONDITIONAL COMPILATION ITEMS   */
// LSEM_ENABLE_PROTOCOL_LIGHT
// LSEM_DEBUG
/***********************************/

#ifndef LSEM_h
#define LSEM_h

#include "Arduino.h"
#include "FastLED.h"


#ifdef LSEM_ENABLE_PROTOCOL

#include "SimpleTimer.h"

#ifdef LSEM_ENABLE_PROTOCOL_LIGHT
#define MAX_PATTERNS  0
#define MAX_LSEM_LOCAL_BUFF 20
#else
#include "stringQueue.h"
#define MAX_PATTERNS  10
#define MAX_LSEM_LOCAL_BUFF 100
#endif
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

#ifdef LSEM_DEBUG
  #define LS_DEBUG_ON  'D'// Enable debug
  #define LS_DEBUG_OFF 'd' // Disable debug
  #define LS_STATUS_REQ 'S'  // Ask for status information over this serial protocol answer TODO spec output
#endif

#ifndef LSEM_ENABLE_PROTOCOL_LIGHT
  #define LS_PERCENTAGE 'G'  // (percentage) 0-100%  4 ascii  filled with zeors 
                             //    e.g 0050, 50 %. Default 0 no impact.
  #define LS_ENQUEUE 'Q'  // Enqueue the rest of the line commands to play when timeout current mode.

#endif



  #define LS_MODE    'M'  // (mode) with <SUBTYPE>
    #define LS_MODE_ZERO           '0'  // no mode. All leds forced to black. Standby.
    #define LS_MODE_COLOR          'A'  // (all) setup all leds with general settings: C,T,P.
    #define LS_MODE_NOISE          'N'  //random leds random color. With general settings: T,P
#ifndef LSEM_ENABLE_PROTOCOL_LIGHT
    #define LS_MODE_ROLLING_TEST   'T'  // rolling 3 test colors. With general settings: T,P.
    #define LS_MODE_RROLLING_TEST  't'  // reverse rolling 3 test colors. With general settings: T,P.
    #define LS_MODE_ROLLING_COLOR  'C'  // rolling bit With general settings: C,T,P.
    #define LS_MODE_RROLLING_COLOR 'c'  // reverse rolling bit With general settings: C,T,P.
    #define LS_MODE_ONE            'O'  //(1 led bit change) with VALUE:LED_POSITION 2 ascii decimal 
                                       //  e.g 00 or 40. With general settings: C,T,P.
    #define LS_MODE_RAINBOW        'W'  //rainbow. With general settings: T.

    #define LS_MODE_NOISE_COLOR    'n'  //random leds fixed color. With general settings: T,P,C
    #define LS_MODE_KNIGHT_RIDER   'K'  //knight rider effect. With general settings: T,P,C
    #define LS_MODE_RKNIGHT_RIDER  'k'  //reverse knight rider effect. With general settings: T,P,C
    #define LS_MODE_PATTERNS       'P'  //put configured patters VALUE:POSITION 2 ascii decimal. With general settings: T,P


  #define LS_PATTERN    'p'  // (pattern operation) over position POSITION 2 ascii decimal,COLOR0,COLOR1,COLOR...
    #define LS_PATTERN_DEF_ZOOM        'Z'  // N leds, later zoom in strip
    #define LS_PATTERN_DEF_MOSAIC      'M'  // N leds, later mosaic in strip
#endif


#endif

class LSEM
{
 public:
  void setAllLeds(CRGB color){_setAllLeds(color);}
#ifdef LSEM_ENABLE_PROTOCOL
  LSEM(CRGB *ls,uint8_t m, timer_callback cbp,timer_callback cbt);
#else
  LSEM(CRGB *ls,uint8_t m);
#endif

#ifdef LSEM_ENABLE_PROTOCOL
  void refresh();

  void reset();
  int processCommands(const char *input,bool flash=false);

#ifdef LSEM_ENABLE_PROTOCOL_LIGHT
  bool isIdle(){return ((_mode==LS_MODE_ZERO)); }
#else
  bool isIdle(){return ((_mode==LS_MODE_ZERO) && (_queue.count()==0)); }
#endif


  void callbackTimeout();
  void callbackPause();
#ifdef LSEM_DEBUG
  bool getDebug()       {return _debug;}
  void setDebug(bool b);
#endif
#ifndef LSEM_ENABLE_PROTOCOL_LIGHT
  void customProtocolId(char p){_ProtocolId=p;}
  void setPattern(uint8_t pos,CRGB *p);
#endif

#endif


 private:

  CRGB *_leds;
  void _setAllLeds(CRGB color);
  uint8_t _NUM_LEDS;
#ifdef LSEM_ENABLE_PROTOCOL
  char _auxBuff[MAX_LSEM_LOCAL_BUFF];
  char _ProtocolId;


  char _mode;
  uint8_t _one;
  CRGB _color; //C
  SimpleTimer _timers;

  int  _timeout; //T
  int  _pause; //P
  int  _timerTimeout; 
  int  _timerPause; 
  bool _timeoutExpired;
  bool _pauseExpired;
  timer_callback _cbt;
  timer_callback _cbp;

#ifdef LSEM_DEBUG
  bool _debug;
#endif

#ifndef LSEM_ENABLE_PROTOCOL_LIGHT
  stringQueue _queue;
  CRGB *_patternsList[MAX_PATTERNS];
  uint8_t _maxPatterns;
  uint8_t _currentPattern;  
  int _rollingTurn;
  CRGB _rollingTestColor;
  int _direction;
  int  _percentage; 
#endif

  void _setMode(char m);
  char _getMode(){return _mode;}
  void _setColor(uint32_t c);
  void _setLed(uint8_t led);
  void _setTimeout(uint16_t t);
  void _setPause(uint16_t p);

  void _fullReset();
  uint8_t _readSerialCommand(char *cmd,int *pok);
  void _doColor();
  void _doNoise();

  uint32_t _readColor(char *cmd);

#ifdef LSEM_DEBUG
  void _debugInfo();
#endif 

#ifndef LSEM_ENABLE_PROTOCOL_LIGHT
  void _resetQueue();
  void _setMaxPatterns(uint8_t p){ _maxPatterns=p; }
  void _setPercentage(uint16_t p);
  void _doRollingTest(bool reverse=false);
  void _doRollingColor(CRGB color,bool reverse=false,bool knightRider=false);
  void _doOne();
  void _doRainbow();
  void _doNoiseColor();
  void _doPatterns();
  void _setPatternDef(uint8_t pos, uint8_t mode, CRGB *p, int max);
#endif

#endif


};

//extern class LSEM LSEM;
#endif


