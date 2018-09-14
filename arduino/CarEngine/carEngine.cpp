#include <Arduino.h>

#include "l298nem.h"
#include "carEngine.h"


#define DEFAULT_SPEED 200



//------------------------------------------------
//------------------------------------------------
//------------------------------------------------
CarEngine::CarEngine(): _frontWheels(6,11,12,5,13,4)
{
_fullReset();
}

//------------------------------------------------
void CarEngine::_doForward ()
{
  _frontWheels.forward();
  //_backWheels.forward();
}
//------------------------------------------------
void CarEngine::_doBackward ()
{
  _frontWheels.backward();
  //_backWheels.backward();
}
//------------------------------------------------
void CarEngine::_doRight ()
{
  _frontWheels.right();
  //_backWheels.right();
}
//------------------------------------------------
void CarEngine::_doLeft ()
{
  _frontWheels.left();
  //_backWheels.left();
}
//------------------------------------------------
void CarEngine::_doStop ()
{
  _frontWheels.stop();
  //_backWheels.stop();
}
//------------------------------------------------
void CarEngine::_setSpeed (uint8_t s)
{
  _speed=s;
  _frontWheels.speed(s);
}
//------------------------------------------------
void CarEngine::_brake ()
{
  if (_speed>130)  _speed=_speed-10;        
  else _speed=120;
  _setSpeed(_speed);
}
//------------------------------------------------
void CarEngine::_gas ()
{
  if (_speed<245)  _speed=_speed+10;        
  else _speed=255;
  _setSpeed(_speed);
}

//------------------------------------------------
void CarEngine::_slightLeft()
{
//TODO so far active delay, next step use simple timers
  _doLeft();
  delay(100);
}
//------------------------------------------------
void CarEngine::_slightRight()
{
  _doRight();
  delay(100);
}

//------------------------------------------------
void CarEngine::_uTurn()
{
  uint8_t bk=_speed;
  _setSpeed(180);
  _doLeft();
  delay(1000);
  _setSpeed(bk);

}

//------------------------------------------------
void CarEngine::refresh(void)
{


  if (_mode==E_MODE_ZERO) {
    if (_queue.count()>0)
    {
      if (_debug){_debugInfo();}
      processCommands(_queue.peek());
      _queue.pop();
    }
  }

  switch(_mode) {
    case E_MODE_STOP:          _doStop();          break;
    case E_MODE_FORWARD:       _doForward();       break;
    case E_MODE_BACKWARD:      _doBackward();      break;
    case E_MODE_LEFT:          _doLeft();          break;
    case E_MODE_RIGHT:         _doRight();         break;
    default: _doStop();                            break;
  }
}

//------------------------------------------------
void CarEngine::processCommands(char *inputString)
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

//-------------------------------------------------
//-------------------------------------------------
//-------------------------------------------------
//-------------------------------------------------

uint8_t CarEngine::_readSerialCommand(char *cmd) {
  char m=0,bk=0;
  uint8_t index=0;
  uint8_t len=0;
  char **kk=0;

  len=strlen(cmd);
  if (_debug){Serial.print(F("DEBUG: Parsing:")); Serial.println(cmd);  }
  switch(cmd[index++]){
    case TYPE_ENGINE:
      if ((len-index) <=0)  {if (_debug){Serial.println(F("DEBUG: incomplete engine command"));} goto exitingCmd;}
      switch(cmd[index++]){
        case E_SPEED:
          if ((len-(index+3)) <0) {if (_debug){Serial.println(F("DEBUG: incomplete E_timeout"));} goto exitingCmd;}
          _setSpeed((uint8_t)strtol(&cmd[index],kk,10));
          index+=3;
          break;
        case E_ENQUEUE:
          _queue.push(&cmd[index]);
          if (_debug){_debugInfo();}
          index+=len;
          break;
        case E_RIGHT:
          _slightRight();
          break;
        case E_LEFT:
          _slightLeft();
          break;
        case E_UTURN:
          _uTurn();
          break;
        case E_GAS:
          _gas();
          break;
        case E_BRAKE:
          _brake();
          break;
        case E_DEBUG_ON:
          setDebug(true);
          break;
        case E_DEBUG_OFF:
          setDebug(false);
          break;
        case E_STATUS_REQ:
          _debugInfo();
          break;
        case E_MODE:
          m=cmd[index++];
          bk=_getMode();
          _setMode(m);
          switch(m){
              case E_MODE_FORWARD:
              case E_MODE_BACKWARD:
              case E_MODE_STOP:
              case E_MODE_LEFT:
              case E_MODE_RIGHT:
                break;
              default: _setMode(bk); if (_debug){Serial.println(F("DEBUG: Engine unexpected mode, ignoring it"));} goto exitingCmd;
          }
          break;
        default: if (_debug){Serial.println(F("DEBUG:Engine unexpected subtype"));} goto exitingCmd;
      };
      break;
    default: if (_debug){Serial.println(F("DEBUG: PROTOCOL unexpected type"));} goto exitingCmd;
  };
  if (_debug){Serial.println(F("DEBUG: Command processed successfully"));}

exitingCmd:;
return index;
}
//------------------------------------------------
void CarEngine::_resetQueue(void)
{
  //Serial.print(F("DEBUG:CarEngine::resetQueue"));
  _queue.clearQueue();
}


//------------------------------------------------
void CarEngine::_setMode(char m)
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
void CarEngine::_debugInfo()
{
  char *str=0;
  Serial.print(":EDEBUG");
  Serial.print(":EM"); Serial.print(_mode);
  Serial.print(":ES"); Serial.print(_speed);
  for (int i=0;i<MAX_STRINGS_IN_QUEUE;i++){
    str=_queue.peek(i);
    if (str) {
     Serial.print(":Et");Serial.print(i);
     Serial.print(str);
    }
  }
  Serial.println("");
}
//------------------------------------------------
void CarEngine::setDebug(bool b)
{
  _debug=b;
  if (b) Serial.println(F("DEBUG: Debug is enable"));
  else   Serial.println(F("DEBUG: Debug is disable"));
}

//------------------------------------------------
void CarEngine::reset(void)
{
   if (_debug) {Serial.print(F("DEBUG:LSEM::reset"));}
  _mode=E_MODE_ZERO;
  _speed=DEFAULT_SPEED;
  _debug=false;
}
//------------------------------------------------
void CarEngine::_fullReset(void)
{
  //Serial.print(F("DEBUG:LSEM::fullReset"));
  reset();
  _resetQueue();
}

