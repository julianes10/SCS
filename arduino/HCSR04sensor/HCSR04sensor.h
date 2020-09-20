/* BASED ON https://www.instructables.com/id/Non-blocking-Ultrasonic-Sensor-for-Arduino */
#ifndef HCSR04sensor_H
#define HCSR04sensor_H

#include <Arduino.h>


class HCSR04sensor {
  public:
    HCSR04sensor(int trigger, int echo, int interrupt, int max_dist=200);   
    void setup();
    void trigger();
    int refresh();

    bool isFinished(){ return _finished; }
    unsigned int getOngoingDistance();
    unsigned int getLatestDistanceRead() {return _latestRead; }
    static HCSR04sensor* instance(){ return _instance; }
    
  private:
    static void _echo_isr();
    
    int _trigger, _echo, _int, _max;
    int _latestRead;
    volatile unsigned long _start, _end;
    volatile bool _finished;
    static HCSR04sensor* _instance;
};

#endif
