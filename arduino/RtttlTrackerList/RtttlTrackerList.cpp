#include "RtttlTrackerList.h"

void RtttlTrackerList::setup( RtttlTrackerItem ousideTracker[],int maxsize)
{
  _tracker=ousideTracker;
  _size=maxsize;
  _notUsed=0;

  for (int i=0;i<_size;i++)
  {
    #ifdef RTTTLTRACKERLIST_DEBUG
    Serial.print("setup... item  ");
    Serial.println(i);
    #endif
    _tracker[i].song=0;
    _tracker[i].used=false;
    #ifdef RTTTLTRACKERLIST_DEBUG
    Serial.println((int)_tracker[i].song);
    #endif


  }
}

void RtttlTrackerList::addItem(const char *song)
{
  for (int i=0;i<_size;i++)
  {
    if (_tracker[i].song==0){
      _tracker[i].song=song;
      _tracker[i].used=false;
      _notUsed++;
      return;
    }
  }
}

const char *RtttlTrackerList::getRandomItem(bool nrepeat=true,bool reload=true)
{
  #ifdef RTTTLTRACKERLIST_DEBUG
  Serial.print("getRandomItem notUsed ");
  Serial.println(_notUsed);
  #endif

  if (nrepeat && (_notUsed==0) && reload==false) return 0;

  int i=random(_size);
  if (_tracker[i].song!=0){
    if (nrepeat) {
      if (_tracker[i].used == false){
        _tracker[i].used=true;
        _notUsed--;
        return  _tracker[i].song;
      }
      else {
        return getRandomItem(nrepeat,reload);
      }    
    }
    return  _tracker[i].song;
   }
   else {
     return getRandomItem(nrepeat,reload);
   }
}

const char *RtttlTrackerList::getOrderedItem(bool reload=true)
{
  #ifdef RTTTLTRACKERLIST_DEBUG
  Serial.print("getOrderedItem notUsed ");
  Serial.println(_notUsed);
  #endif
  if (_notUsed==0  && reload==false) return 0;
  
  //Give 1st not used
  for (int i=0;i<_size;i++)
  {
    if (_tracker[i].song!=0){
      if (_tracker[i].used == false){
        _tracker[i].used=true;
        _notUsed--;
        return  _tracker[i].song;
      }
    }
  }
  //No songs or all used
  if (reload)
  {
    resetTrackUsed();
    return getOrderedItem(reload);
  }
  return 0; //should never be here
}


void  RtttlTrackerList::resetTrackUsed()
{
  for (int i=0;i<_size;i++)
  {
    _tracker[i].used=false;
    if (_tracker[i].song !=0) _notUsed++;
  }
}
