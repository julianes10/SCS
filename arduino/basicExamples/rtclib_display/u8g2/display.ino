// Arduino real time clock and temperature monitor with DS3231 and SSD1306 OLED
 
#include <Arduino.h>
#include <U8g2lib.h>

#ifdef U8X8_HAVE_HW_SPI
#include <SPI.h>
#endif
#ifdef U8X8_HAVE_HW_I2C
#include <Wire.h>
#endif

#include "RTClib.h"

//U8G2_SSD1306_128X32_UNIVISION_1_SW_I2C u8g2(U8G2_R0, /* clock=*/ SCL, /* data=*/ SDA, /* reset=*/ U8X8_PIN_NONE);  

U8G2_SSD1306_128X32_UNIVISION_F_HW_I2C u8g2(U8G2_R0, /* clock=*/ SCL, /* data=*/ SDA, /* reset=*/ U8X8_PIN_NONE);  


RTC_DS3231 rtc;


void setup(void) {

  Serial.begin(9600);
  Serial.println(F("Setup... 'came on,be my baby,came on'"));

  u8g2.begin(); 
  return;

  if (! rtc.begin()) {
    Serial.println("Couldn't find RTC");
  }

  if (rtc.lostPower()) {
    Serial.println("RTC lost power, let's set the time!");
    // When time needs to be set on a new device, or after a power loss, the
    // following line sets the RTC to the date & time this sketch was compiled
    rtc.adjust(DateTime(F(__DATE__), F(__TIME__)));
    // This line sets the RTC with an explicit date & time, for example to set
    // January 21, 2014 at 3am you would call:
    // rtc.adjust(DateTime(2014, 1, 21, 3, 0, 0));
  }
}
 uint8_t m = 24;




void display_refresh(){
  //byte second, minute, hour, day, date, month, year,
  byte second,minute, hour;
  float temp;
 
  // DISPLAY HH:MM TT.Tº
  DateTime now = rtc.now();

  second = now.second();
  //year = now.year();
  //month = now.month();
  //day = now.day();

  minute = now.minute();
  hour = now.hour();
  temp =rtc.getTemperature();


  char strTime[]     =    "  :  ";


  char strTemperature[] = "00";
  char strTemperatureDec[] = "0";
  char strHumidity[] = "00.0%";
 
  //strTime[7]     = second % 10 + 48;
  //strTime[6]     = second / 10 + 48;
  strTime[4]     = minute % 10 + 48;
  strTime[3]     = minute / 10 + 48;
  strTime[1]     = hour   % 10 + 48;
  strTime[0]     = hour   / 10 + 48;

  u8g2.firstPage();
  do {
    u8g2.drawVLine(48, 2, 30);
    u8g2.drawHLine(2, 16, 46);

    u8g2.setFont(u8g2_font_helvB12_tn);
    u8g2.drawStr(0,14,strTime);

    u8g2.setCursor(0,32);
    u8g2.print(temp,1);
    u8g2.print("%");
    //u8g2.drawStr(0,24,"Hello World!");
    u8g2.setFont(u8g2_font_logisoso32_tn);
    u8g2.setCursor(50,32);
    u8g2.print(temp,1);
    u8g2.drawCircle(125, 5, 2, U8G2_DRAW_ALL);

  } while ( u8g2.nextPage() );

/*
  display.setCursor(2,4);
  display.setTextSize(1.8);  
  display.print(strTime);
  display.display();

  display.drawLine(0,16,35,16,WHITE);

  display.setCursor(2,20);
  display.setTextSize(1.8);  
  display.print(strHumidity);
  display.display();

  display.drawLine(42,2,42,30,WHITE);

  display.drawRect(125, 0, 3, 3, WHITE);     // Put degree symbol ( ° )
  display.setCursor(50,2);
  display.setTextSize(4); 
  display.print(strTemperature);
  display.drawRect(99, 29, 2, 2, WHITE);     // Put decimal dot without consuming full char
  display.setCursor(102,2);
  display.setTextSize(4);    
  display.print(strTemperatureDec);
  display.display();*/
}
int counteralive=0; 
void loop(void) {
  display_refresh();
 
  //  delay(50);                                    // Wait 50ms 
  counteralive++;
  if ((counteralive % 100)==0){
    DateTime now = rtc.now();
    Serial.print(counteralive);
    Serial.print("Temperature: ");
    Serial.print(rtc.getTemperature());
    Serial.println(" C");
  }
}

