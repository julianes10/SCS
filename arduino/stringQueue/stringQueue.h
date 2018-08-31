#ifndef STRINGQUEUE_h
#define STRINGQUEUE_h

#include "Arduino.h"


#define MAX_STRINGS_IN_QUEUE   7

class stringQueue
{
 public:
  stringQueue();
  int push(char* in);
  char *pop(char* out);   //return a copy in out and free mem
  char *peek(char* out);  //return a copy in out, not free
  char *peek(int pos);    //return the reference at pos, not free
  char *peek();           //return the reference at head, not free
  void pop();             //just free head mem
  int getHead(){return _head;}
  int getTail(){return _tail;}
  int count();
  void clearQueue();
 private:
  void _reset();
  char *_q[MAX_STRINGS_IN_QUEUE];
  int _head;
  int _tail;
};

//extern class stringQueue stringQueue;
#endif


