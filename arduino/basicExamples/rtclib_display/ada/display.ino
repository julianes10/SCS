// Arduino real time clock and temperature monitor with DS3231 and SSD1306 OLED
 
#include <Wire.h>                        // Include Wire library (required for I2C devices)
#include <Adafruit_GFX.h>                // Include Adafruit graphics library
#include <Adafruit_SSD1306.h>            // Include Adafruit SSD1306 OLED driver

#include "RTClib.h"

RTC_DS3231 rtc;
 
/*#define OLED_RESET 4
Adafruit_SSD1306 display(OLED_RESET);*/

#define SCREEN_WIDTH 128 // OLED display width, in pixels
#define SCREEN_HEIGHT 32 // OLED display height, in pixels

// Declaration for an SSD1306 display connected to I2C (SDA, SCL pins)
#define OLED_RESET     4 // Reset pin # (or -1 if sharing Arduino reset pin)
Adafruit_SSD1306 display(SCREEN_WIDTH, SCREEN_HEIGHT, &Wire, OLED_RESET);

 
#define button1    9                       // Button B1 is connected to Arduino pin 9
#define button2    8                       // Button B2 is connected to Arduino pin 8
 

void draw_text(byte x_pos, byte y_pos, char *text, byte text_size);

void setup(void) {

  Serial.begin(9600);
  Serial.println(F("Setup... 'came on,be my baby,came on'"));
  // SSD1306_SWITCHCAPVCC = generate display voltage from 3.3V internally
  if(!display.begin(SSD1306_SWITCHCAPVCC, 0x3C)) { // Address 0x3C for 128x32
    Serial.println(F("SSD1306 allocation failed"));
    for(;;); // Don't proceed, loop forever
  }

  // Show initial display buffer contents on the screen --
  // the library initializes this with an Adafruit splash screen.
//  display.display();
//  delay(2000); // Pause for 2 seconds

  // Clear the buffer
//  display.clearDisplay();






  // init done
 
  // Clear the display buffer.
  display.clearDisplay();
  display.display();
 
  display.setTextColor(WHITE, BLACK);


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
 
char Time[]     = "  :  :  ";
char Calendar[] = "  /  /20  ";
char temperature[] = " 00.00";
char temperature_msb;
byte i, second, minute, hour, day, date, month, year, temperature_lsb;
 
void display_day(){
  switch(day){
    case 1:  draw_text(40, 0, " SUNDAY  ", 1); break;
    case 2:  draw_text(40, 0, " MONDAY  ", 1); break;
    case 3:  draw_text(40, 0, " TUESDAY ", 1); break;
    case 4:  draw_text(40, 0, "WEDNESDAY", 1); break;
    case 5:  draw_text(40, 0, "THURSDAY ", 1); break;
    case 6:  draw_text(40, 0, " FRIDAY  ", 1); break;
    default: draw_text(40, 0, "SATURDAY ", 1);
  }
}
 


void display_refresh(){
  //byte second, minute, hour, day, date, month, year,
  byte second,minute, hour;
  float temp;
 
  // DISPLAY HH:MM TT.Tº
  DateTime now = rtc.now();

  //second = now.second();
  //year = now.year();
  //month = now.month();
  //day = now.day();

  minute = now.minute();
  hour = now.hour();
  temp =rtc.getTemperature();


  char strTime[]     =    "  :  ";//:  ";
  char strTemperature[] = "00";
  char strTemperatureDec[] = "0";
  char strHumidity[] = "00.0%";
 
  //strTime[7]     = second % 10 + 48;
  //strTime[6]     = second / 10 + 48;
  strTime[4]     = minute % 10 + 48;
  strTime[3]     = minute / 10 + 48;
  strTime[1]     = hour   % 10 + 48;
  strTime[0]     = hour   / 10 + 48;




  strTemperatureDec[0]  = (char)(   int((temp - (int)temp)*10)%10 + 48);
  strTemperature[1]     = (char)(   int(temp)  % 10 + 48);
  strTemperature[0]     = (char)(   temp   / 10 + 48);


  strTemperature[0]     = (char)(   temp   / 10 + 48);

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
  display.display();

}

int counteralive=0; 
void loop() {
  DateTime now = rtc.now();
/*
  Serial.println("Looping...");


  char daysOfTheWeek[7][12] = {"Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"};


  Serial.print(now.year(), DEC);
  Serial.print('/');
  Serial.print(now.month(), DEC);
  Serial.print('/');
  Serial.print(now.day(), DEC);
  Serial.print(" (");
  Serial.print(daysOfTheWeek[now.dayOfTheWeek()]);
  Serial.print(") ");
  Serial.print(now.hour(), DEC);
  Serial.print(':');
  Serial.print(now.minute(), DEC);
  Serial.print(':');
  Serial.print(now.second(), DEC);
  Serial.println();

  Serial.print(" since midnight 1/1/1970 = ");
  Serial.print(now.unixtime());
  Serial.print("s = ");
  Serial.print(now.unixtime() / 86400L);
  Serial.println("d");

  // calculate a date which is 7 days and 30 seconds into the future
  DateTime future (now + TimeSpan(7,12,30,6));

  Serial.print(" now + 7d + 30s: ");
  Serial.print(future.year(), DEC);
  Serial.print('/');
  Serial.print(future.month(), DEC);
  Serial.print('/');
  Serial.print(future.day(), DEC);
  Serial.print(' ');
  Serial.print(future.hour(), DEC);
  Serial.print(':');
  Serial.print(future.minute(), DEC);
  Serial.print(':');
  Serial.print(future.second(), DEC);
  Serial.println();



  Serial.println();
  second=now.second();

 
  //display_day();
  //DS3231_display();                             // Diaplay time & calendar
  */
  display_refresh();
 
  //  delay(50);                                    // Wait 50ms 
  counteralive++;
  if ((counteralive % 100)==0){
    Serial.print(counteralive);
    Serial.print("Temperature: ");
    Serial.print(rtc.getTemperature());
    Serial.println(" C");
  }
}
// End of code.
