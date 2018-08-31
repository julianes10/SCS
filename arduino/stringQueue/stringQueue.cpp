#include <Arduino.h>

#include "stringQueue.h"


class stringQueue stringQueue;

//------------------------------------------------
//------------------------------------------------
//------------------------------------------------
stringQueue::stringQueue()
{
  _reset();
}
//------------------------------------------------
int stringQueue::count(void)
{
 if (_tail==-1) return 0;
 if (_tail >= _head)
   return _tail - _head+1;
 else 
   return MAX_STRINGS_IN_QUEUE - _head + _tail+1;
}
//------------------------------------------------
int stringQueue::push(char* in)
{
 if (in==0)       return -1;
 if (count()>=MAX_STRINGS_IN_QUEUE) return -1;

 if (_tail == -1) {_tail=0; _head=0;}
 else _tail=(_tail+1 % MAX_STRINGS_IN_QUEUE);

 _q[_tail]=strdup(in);
 return _tail;
}

//------------------------------------------------
char *stringQueue::pop(char* out)
{
 if (0==peek(out)) return 0;
 pop();
 return out;
}
//------------------------------------------------
void stringQueue::pop(void)
{
 char *ref=peek();
 if (0==ref) 
   return;

 free(ref);
 _q[_head]=0;

 if (count()==1) {
   _head=-1; _tail=-1;
 }
 else {
   _head=(_head+1 % MAX_STRINGS_IN_QUEUE);
 }
}
//------------------------------------------------
char *stringQueue::peek(char* out)
{
 if (out==0)       return 0;
 if (count()==0)   {out[0]=0; return 0;}

 strcpy(out,_q[_head]); 
 return out;
}
//------------------------------------------------
char *stringQueue::peek(int pos)
{
 if ((count()==0) || (pos<0) || (pos>= MAX_STRINGS_IN_QUEUE) ){
   return 0;
 }
 return _q[pos];
}
//------------------------------------------------
char *stringQueue::peek()
{
 return peek(_head);
}
//------------------------------------------------
void stringQueue::clearQueue(void)
{
  for (int i=0;i<MAX_STRINGS_IN_QUEUE;i++)  {
    if (0!=_q[i]) free(_q[i]);
  }
  _reset();
}
//------------------------------------------------
//------------------------------------------------
void stringQueue::_reset(void)
{
  for (int i=0;i<MAX_STRINGS_IN_QUEUE;i++)  _q[i]=0;
  _head=-1;
  _tail=-1;
}


