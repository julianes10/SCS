#ifndef RtttlTrackerList_H
#define RtttlTrackerList_H

#include <Arduino.h>


//#define RTTTLTRACKERLIST_DEBUG


typedef struct  {
    char *song;
    bool used;
} RtttlTrackerItem;

//TODO encapsulate a dynamic  list using light weighted list template...
//Now real tracker ram info must be allocated ouside in main project...
class RtttlTrackerList {
  public:
    RtttlTrackerList(){};
    void setup( RtttlTrackerItem ousideTracker[],int maxsize);
    void addItem(const char *song);
    const char *getRandomItem(bool nrepeat,bool reload);
    const char *getOrderedItem(bool reload);
    void resetTrackUsed(); 
  private:
    RtttlTrackerItem *_tracker;
    int _size;
    int _notUsed;
};

#endif
