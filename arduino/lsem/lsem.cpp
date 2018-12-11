#include <Arduino.h>

#include "FastLED.h"
#include "lsem.h"


#define RIGHT 0
#define LEFT  1



//------------------------------------------------
//------------------------------------------------
//------------------------------------------------
LSEM::LSEM(CRGB *ls,uint8_t m,timer_callback cbp,timer_callback cbt)
{
  _NUM_LEDS=m;
  _leds=ls;
  _fullReset();
  randomSeed(analogRead(0));
  _cbp=cbp;
  _cbt=cbt;
  _ProtocolId=TYPE_LED;
}
//------------------------------------------------
void LSEM::callbackTimeout(void)
{
  _timeoutExpired=true;
  _mode=LS_MODE_ZERO;
}
//------------------------------------------------
void LSEM::callbackPause(void)
{
  _pauseExpired=true;
}
//------------------------------------------------
void LSEM::refresh(void)
{
  _timers.run();

  if (_mode==LS_MODE_ZERO) {
    if (_queue.count()>0)
    {
      if (_debug){_debugInfo();}
      processCommands(_queue.peek());
      _queue.pop();
    }
  }

  switch(_mode) {
    case LS_MODE_COLOR:          _doColor();         break;
    case LS_MODE_ROLLING_TEST:   _doRollingTest();   break;
    case LS_MODE_RROLLING_TEST:  _doRollingTest(true);   break;
    case LS_MODE_ROLLING_COLOR:  _doRollingColor(_color); break;
    case LS_MODE_RROLLING_COLOR: _doRollingColor(_color,true); break;
    case LS_MODE_ONE:            _doOne();           break;
    case LS_MODE_RAINBOW:        _doRainbow();       break;
    case LS_MODE_NOISE:          _doNoise();         break;
    case LS_MODE_NOISE_WHITE:    _doNoiseWhite();         break;
    case LS_MODE_KNIGHT_RIDER:   _doRollingColor(_color,false,true); break;
    case LS_MODE_RKNIGHT_RIDER:  _doRollingColor(_color,true,true); break;  
    case LS_MODE_PATTERNS:       _doPatterns();      break;
    default: reset();                       break;
  }
  //FastLED.show();-- do in main loop, affecting all instances
}

//------------------------------------------------
void LSEM::processCommands(char *inputString)
{
  int index=0,readbytes=0;
  int len=0;
  //Serial.print(F("DEBUG:")); Serial.println(inputString);

  len=strlen(inputString);
  while ((len-index) >0)
  { 
    char *subcmd=0; 
    subcmd=strchr(inputString,':');
    if (subcmd==0) {
      if (_debug){ Serial.println(F("DEBUG: no more comands in the line"));}
      break;
    }
    index++; 
    readbytes=_readSerialCommand(&inputString[index]);
    index+=readbytes;  
  }

}

//------------------------------------------------
void LSEM::reset(void)
{
   if (_debug) {Serial.print(F("DEBUG:LSEM::reset"));}
  _mode=LS_MODE_ZERO;
  _one=0;
  _color=CRGB::Black; 
  _setAllLeds(CRGB::Black);
  _rollingTurn=0;
  _rollingTestColor=0x0000FF;
  _direction=RIGHT;
  _debug=false;

  _timeoutExpired=false;
  _pauseExpired=false;
  _timers.deleteTimer(_timerTimeout);
  _timerTimeout=-1;
  _timers.deleteTimer(_timerPause);
  _timerPause=-1;
  _timeout=0; //T
  _pause=0;   //P

  for (int i=0;i<MAX_PATTERNS;i++)
    _patternsList[i]=0;
  _maxPatterns=0;
  _currentPattern=0;

}

//------------------------------------------------
void LSEM::setDebug(bool b)
{
  _debug=b;
  if (b) Serial.println(F("DEBUG: Debug is enable"));
  else   Serial.println(F("DEBUG: Debug is disable"));
}

//------------------------------------------------
void LSEM::setPattern(uint8_t pos,CRGB *p)
{
  _patternsList[pos]=p;

}

//------------------------------------------------
void LSEM::_setPatternDef(uint8_t pos, uint8_t mode, CRGB *p, int max)
{
/*  

       case LS_PATTERN_DEF_ZOOM:
          case LS_PATTERN_DEF_MOSAIC:
            int i=0;
            while ((len-(index+10)) <0) && cmd[index++] ! ":"){
              pos[i]   = (uint8_t)strtol(&cmd[index],kk,10));
              index+=2;
              color[i] = _getColor(&cmd[index]);
              index+=8;
              i++;
            }
            _setPatternDef(pat,patMode,pos,color,i);

  _patternsList[pos]=p;
*/
}

//-------------------------------------------------
//-------------------------------------------------
//-------------------------------------------------
//-------------------------------------------------

uint8_t LSEM::_readSerialCommand(char *cmd) {
  char m=0,bk=0;
  uint8_t index=0;
  uint8_t len=0;
  uint32_t color=0;
  char **kk=0;
  CRGB colorPat[10];
  uint8_t pat,patMode;

  len=strlen(cmd);
  if (_debug){Serial.print(F("DEBUG: Parsing:")); Serial.println(cmd);  }

  if (cmd[index++] != _ProtocolId){
    if (_debug){Serial.println(F("DEBUG: PROTOCOL unexpected type"));} 
    goto exitingCmd;
  }

  if ((len-index) <=0)  {if (_debug){Serial.println(F("DEBUG: incomplete led command"));} goto exitingCmd;}

  switch(cmd[index++]){
    case LS_RESET:
      reset();
      break;
    case LS_COLOR:
      if ((len-(index+8)) <0) {if (_debug){Serial.println(F("DEBUG: incomplete ls_color"));} goto exitingCmd;}
      if (_debug){Serial.print(F("DEBUG: new LS color:"));}
      color=_readColor(&cmd[index]);
      index+=8;
      _setColor(color);
      break;
    case LS_TIMEOUT:
      if ((len-(index+4)) <0) {if (_debug){Serial.println(F("DEBUG: incomplete ls_timeout"));} goto exitingCmd;}
      _setTimeout((uint16_t)strtol(&cmd[index],kk,10));
      index+=4;
      break;
    case LS_PAUSE:
      if ((len-(index+4)) <0) {if (_debug){Serial.println(F("DEBUG: incomplete ls_timeout"));} goto exitingCmd;}
      _setPause((uint16_t)strtol(&cmd[index],kk,10));
      index+=4;
      break;
    case LS_ENQUEUE:
      _queue.push(&cmd[index]);
      if (_debug){_debugInfo();}
      index+=len;
      break;
    case LS_DEBUG_ON:
      setDebug(true);
      break;
    case LS_DEBUG_OFF:
      setDebug(false);
      break;
    case LS_STATUS_REQ:
      _debugInfo();
      break;
    case LS_PATTERN:
      //:Lp00 Z89,89,77 55,88,99 ...
      if ((len-(index+2)) <0) {if (_debug){Serial.println(F("DEBUG: incomplete ls_mode_one"));} goto exitingCmd;}
        pat=(uint8_t)strtol(&cmd[index],kk,10);
        index+=3;
        patMode=cmd[index];
        index+=1;
        switch(patMode){
          case LS_PATTERN_DEF_ZOOM:
          case LS_PATTERN_DEF_MOSAIC:
            int i=0;
            while (((len-(index+10)) <0) && (cmd[index++] != ':')){
              colorPat[i] = _readColor(&cmd[index]);
              index+=8;
              if (cmd[index]==' ') index+=1;
              i++;
            }
            _setPatternDef(pat,patMode,colorPat,i);
        };
      break;
    case LS_MODE:
      m=cmd[index++];
      bk=_getMode();
      _setMode(m);
      switch(m){
          case LS_MODE_RAINBOW:
          case LS_MODE_COLOR:
          case LS_MODE_NOISE:
          case LS_MODE_NOISE_WHITE:
          case LS_MODE_ROLLING_TEST:
          case LS_MODE_RROLLING_TEST:
          case LS_MODE_ROLLING_COLOR:
          case LS_MODE_RROLLING_COLOR:
          case LS_MODE_KNIGHT_RIDER:
          case LS_MODE_RKNIGHT_RIDER:
            break;
          case LS_MODE_ONE:
            if ((len-(index+2)) <0) {if (_debug){Serial.println(F("DEBUG: incomplete ls_mode_one"));} goto exitingCmd;}
            _setLed((uint8_t)strtol(&cmd[index],kk,10));
            index+=2;
            break;
          case LS_MODE_PATTERNS:
            if ((len-(index+2)) <0) {if (_debug){Serial.println(F("DEBUG: incomplete ls_mode_one"));} goto exitingCmd;}
            _setMaxPatterns((uint8_t)strtol(&cmd[index],kk,10));
            index+=2;
            break;
          default: _setMode(bk); if (_debug){Serial.println(F("DEBUG: LS unexpected mode, ignoring it"));} goto exitingCmd;
      }
      break;
    default: if (_debug){Serial.println(F("DEBUG:LS unexpected subtype"));} goto exitingCmd;
    break;
  }

    

if (_debug){Serial.println(F("DEBUG: Command processed successfully"));}

exitingCmd:;
return index;
}


//------------------------------------------------
uint32_t LSEM::_readColor(char *cmd)
{
  uint32_t rt=0;
  int br=0,bg=0,bb=0;
  int index=0;

  sscanf(&cmd[index],"%X",&br); index+=3;
  sscanf(&cmd[index],"%X",&bg); index+=3;
  sscanf(&cmd[index],"%X",&bb); index+=2;
  //Serial.print(F("DEBUG:");Serial.print(br,HEX);Serial.print(bg,HEX);Serial.print(bb,HEX);
  rt=(uint32_t) ( 
                        (((long int)(br))<<16 ) | 
                        (((long int)(bg))<<8)   | 
                        ((long int)(bb))  );
  return rt;
}
//------------------------------------------------
void LSEM::_fullReset(void)
{
  //Serial.print(F("DEBUG:LSEM::fullReset"));
  reset();
  _resetQueue();
}
//------------------------------------------------
void LSEM::_resetQueue(void)
{
  //Serial.print(F("DEBUG:LSEM::resetQueue"));
  _queue.clearQueue();
}

//------------------------------------------------
void LSEM::_setTimeout(uint16_t t)
{
  _timeout=t;

  if (_timerTimeout >= 0) _timers.deleteTimer(_timerTimeout);

  _timerTimeout=-1;
  if (t>0){
    _timerTimeout=_timers.setInterval((long int)t*100,_cbt);
    if (_debug){
      Serial.print(F("DEBUG: setTimeout to "));
      Serial.print(t*100);
      Serial.print(F(" ms. Timer number: "));
      Serial.println(_timerTimeout);
    }
  }
}
//------------------------------------------------
void LSEM::_setPause(uint16_t t)
{
  _pause=t;
  if (_timerPause >= 0) _timers.deleteTimer(_timerPause);
  _timerPause=-1;
  if (t>0){
    _timerPause=_timers.setInterval((long int)t,_cbp);
    if (_debug){ 
      Serial.print(F("DEBUG: setPause to "));
      Serial.print(t);
      Serial.print(F(" ms. Timer number: "));
      Serial.println(_timerPause);
    }
  }
}
//------------------------------------------------
void LSEM::_setMode(char m)
{
  if (_debug){
    Serial.print(F("DEBUG: setMode from: "));
    Serial.print(_mode);
    Serial.print(F(" to: "));
    Serial.println(m);
  }
  _mode=m;
}
//------------------------------------------------
void LSEM::_setColor(uint32_t c)
{ 
  if (_debug){
    Serial.print(F("DEBUG: setColor from: "));
    Serial.print(_color,HEX);
    Serial.print(F(" to: "));
    Serial.println(c,HEX);
  }
  _color=(CRGB)c;
}
//------------------------------------------------
void LSEM::_setLed(uint8_t led)
{
  _one=led;
}

//------------------------------------------------
void LSEM::_doOne()
{
  _leds[_one] = CRGB::White;
}

//------------------------------------------------
void LSEM::_setAllLeds(CRGB color)
{
  // Turn the LED on, then pause
  for (int i=0;i<_NUM_LEDS;i++)
  {
    _leds[i] = color;
  }
}

//------------------------------------------------
void LSEM::_doRollingColor(CRGB color,bool reverse,bool knightRider)
{
   if (!_pauseExpired) return;
   //Setup the led to roll
   if (_rollingTurn>=_NUM_LEDS) 
   {  
     if (knightRider)  {_rollingTurn=_NUM_LEDS-1; _direction=LEFT;}
     else              _rollingTurn=0;     
   }
   if (_rollingTurn<=0) 
   {  
     if (knightRider)  {_rollingTurn=0; _direction=RIGHT;}
     else              _rollingTurn=0;     
   }

   //Check if it is only one, or reverse (all but one)
   if (reverse) {
     _setAllLeds(color);
     _leds[_rollingTurn] = CRGB::Black;
   }
   else {  
     _setAllLeds(CRGB::Black);
     _leds[_rollingTurn] = color;
  }

  //Determine tentative next turn
  if (_direction==RIGHT) {
    _rollingTurn++;
  }
  else {
       _rollingTurn--;
  }

  //Mark to wait until the pause period
   _pauseExpired=false;
}

//------------------------------------------------
void LSEM::_doRollingTest(bool reverse)
{
  if ( _rollingTurn==_NUM_LEDS)
  { 
    if      (_rollingTestColor == (CRGB)CRGB::Red)    _rollingTestColor=CRGB::Green;
    else if (_rollingTestColor == (CRGB)CRGB::Green)  _rollingTestColor=CRGB::Blue;
    else if (_rollingTestColor == (CRGB)CRGB::Blue)   _rollingTestColor=CRGB::Red;
    else                                              _rollingTestColor=CRGB::Red;
  }
  _doRollingColor(_rollingTestColor,reverse); 
}


//------------------------------------------------
void LSEM::_doColor()
{ 
  _setAllLeds(_color);
}
//------------------------------------------------
void LSEM::_doRainbow()
{ //TODO
}
//------------------------------------------------
void LSEM::_doNoise()
{ 
  if (!_pauseExpired) return;
  for (int i=0;i<_NUM_LEDS;i++)
  {
    _leds[i] = random(0xFFFFFF);
  }
  _pauseExpired=false;
}

//------------------------------------------------
void LSEM::_doNoiseWhite()
{ 
  if (!_pauseExpired) return;

  for (int i=0;i<_NUM_LEDS;i++)
  {
    _leds[i] = 0;
    if (random(10)%2 == 0){
      _leds[i] = 0xFFFFFF;
    }
  }
  _pauseExpired=false;
}
//------------------------------------------------
void LSEM::_doPatterns()
{ 

  if (!_pauseExpired) return;

  uint8_t nextPattern=(_currentPattern+1)%_maxPatterns;
  for (int i=0;i<_NUM_LEDS;i++)
  {
    _leds[i]=_patternsList[nextPattern][i];
  }
  _currentPattern=nextPattern;
  _pauseExpired=false;
}
//------------------------------------------------
void LSEM::_debugInfo()
{
  char *str=0;
  Serial.print(":");Serial.print(_ProtocolId);Serial.print("SDEBUG");
  Serial.print(":");Serial.print(_ProtocolId);Serial.print("M"); Serial.print(_mode);
  Serial.print(":");Serial.print(_ProtocolId);Serial.print("T"); Serial.print(_timeout);
  Serial.print(":");Serial.print(_ProtocolId);Serial.print("P"); Serial.print(_pause);
  Serial.print(":");Serial.print(_ProtocolId);Serial.print("C"); Serial.print((long int)_color);
  Serial.print(":");Serial.print(_ProtocolId);Serial.print("MP"); Serial.print((uint8_t)_maxPatterns);
  Serial.print(":");Serial.print(_ProtocolId);Serial.print("q"); Serial.print(_queue.count());
  Serial.print(":");Serial.print(_ProtocolId);Serial.print("h"); Serial.print(_queue.getHead());
  Serial.print(":");Serial.print(_ProtocolId);Serial.print("t"); Serial.print(_queue.getTail());
  for (int i=0;i<MAX_STRINGS_IN_QUEUE;i++){
    str=_queue.peek(i);
    if (str) {
     Serial.print(":");Serial.print(_ProtocolId);Serial.print("t");Serial.print(i);
     Serial.print(str);
    }
  }
  Serial.println("");
}

