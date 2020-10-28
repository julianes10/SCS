// Arduino real time clock and temperature monitor with DS3231 and SSD1306 OLED
 
#include <Wire.h>                        // Include Wire library (required for I2C devices)
#include <Adafruit_GFX.h>                // Include Adafruit graphics library
#include <Adafruit_SSD1306.h>            // Include Adafruit SSD1306 OLED driver
 
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


  pinMode(button1, INPUT_PULLUP);
  pinMode(button2, INPUT_PULLUP);
  delay(1000);
 
  // SSD1306_SWITCHCAPVCC = generate display voltage from 3.3V internally
  if(!display.begin(SSD1306_SWITCHCAPVCC, 0x3C)) { // Address 0x3C for 128x32
    Serial.println(F("SSD1306 allocation failed"));
    for(;;); // Don't proceed, loop forever
  }

  // Show initial display buffer contents on the screen --
  // the library initializes this with an Adafruit splash screen.
  display.display();
  delay(2000); // Pause for 2 seconds

  // Clear the buffer
  display.clearDisplay();






  // init done
 
  // Clear the display buffer.
  display.clearDisplay();
  display.display();
 
  display.setTextColor(WHITE, BLACK);
  display.drawRect(117, 56, 3, 3, WHITE);     // Put degree symbol ( ° )
  draw_text(0, 56, "TEMPERATURE =", 1);
  draw_text(122, 56, "C", 1);
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
 
void DS3231_display(){
  // Convert BCD to decimal
  second = (second >> 4) * 10 + (second & 0x0F);
  minute = (minute >> 4) * 10 + (minute & 0x0F);
  hour   = (hour >> 4)   * 10 + (hour & 0x0F);
  date   = (date >> 4)   * 10 + (date & 0x0F);
  month  = (month >> 4)  * 10 + (month & 0x0F);
  year   = (year >> 4)   * 10 + (year & 0x0F);
  // End conversion
 
  Time[7]     = second % 10 + 48;
  Time[6]     = second / 10 + 48;
  Time[4]     = minute % 10 + 48;
  Time[3]     = minute / 10 + 48;
  Time[1]     = hour   % 10 + 48;
  Time[0]     = hour   / 10 + 48;
  Calendar[9] = year   % 10 + 48;
  Calendar[8] = year   / 10 + 48;
  Calendar[4] = month  % 10 + 48;
  Calendar[3] = month  / 10 + 48;
  Calendar[1] = date   % 10 + 48;
  Calendar[0] = date   / 10 + 48;
  if(temperature_msb < 0){
    temperature_msb = abs(temperature_msb);
    temperature[0] = '-';
  }
  else
    temperature[0] = ' ';
  temperature_lsb >>= 6;
  temperature[2] = temperature_msb % 10  + 48;
  temperature[1] = temperature_msb / 10  + 48;
  if(temperature_lsb == 0 || temperature_lsb == 2){
    temperature[5] = '0';
    if(temperature_lsb == 0) temperature[4] = '0';
    else                     temperature[4] = '5';
  }
  if(temperature_lsb == 1 || temperature_lsb == 3){
    temperature[5] = '5';
    if(temperature_lsb == 1) temperature[4] = '2';
    else                     temperature[4] = '7';
  }
 
//  draw_text(4,  14, Calendar, 2);                     // Display the date (format: dd/mm/yyyy)
//  draw_text(16, 35, Time, 2);                         // Display the time
//  draw_text(80, 56, temperature, 1);                  // Display the temperature
  draw_text(4, 14, Time, 2);                         // Display the time
  draw_text(60, 56, temperature, 1);                  // Display the temperature

}
 
void blink_parameter(){
  byte j = 0;
  while(j < 10 && digitalRead(button1) && digitalRead(button2)){
    j++;
    delay(25);
  }
}
 
byte edit(byte x_pos, byte y_pos, byte parameter){
  char text[3];
  sprintf(text,"%02u", parameter);
  while(!digitalRead(button1));                      // Wait until button B1 released
  while(true){
    while(!digitalRead(button2)){                    // If button B2 is pressed
      parameter++;
      if(i == 0 && parameter > 31)                   // If date > 31 ==> date = 1
        parameter = 1;
      if(i == 1 && parameter > 12)                   // If month > 12 ==> month = 1
        parameter = 1;
      if(i == 2 && parameter > 99)                   // If year > 99 ==> year = 0
        parameter = 0;
      if(i == 3 && parameter > 23)                   // If hours > 23 ==> hours = 0
        parameter = 0;
      if(i == 4 && parameter > 59)                   // If minutes > 59 ==> minutes = 0
        parameter = 0;
      sprintf(text,"%02u", parameter);
      draw_text(x_pos, y_pos, text, 2);
      delay(200);                                    // Wait 200ms
    }
    draw_text(x_pos, y_pos, "  ", 2);
    blink_parameter();
    draw_text(x_pos, y_pos, text, 2);
    blink_parameter();
    if(!digitalRead(button1)){                       // If button B1 is pressed
      i++;                                           // Increament 'i' for the next parameter
      return parameter;                              // Return parameter value and exit
    }
  }
}
 
void draw_text(byte x_pos, byte y_pos, char *text, byte text_size) {
  display.setCursor(x_pos, y_pos);
  display.setTextSize(text_size);
  display.print(text);
  display.display();

  Serial.println(text);
}
 
void loop() {


  Serial.println("Looping...");

 
  Wire.beginTransmission(0x68);                 // Start I2C protocol with DS3231 address
  Wire.write(0);                                // Send register address
  Wire.endTransmission(false);                  // I2C restart
  Wire.requestFrom(0x68, 7);                    // Request 7 bytes from DS3231 and release I2C bus at end of reading
  second = Wire.read();                         // Read seconds from register 0
  minute = Wire.read();                         // Read minuts from register 1
  hour   = Wire.read();                         // Read hour from register 2
  day    = Wire.read();                         // Read day from register 3
  date   = Wire.read();                         // Read date from register 4
  month  = Wire.read();                         // Read month from register 5
  year   = Wire.read();                         // Read year from register 6
  Wire.beginTransmission(0x68);                 // Start I2C protocol with DS3231 address
  Wire.write(0x11);                             // Send register address
  Wire.endTransmission(false);                  // I2C restart
  Wire.requestFrom(0x68, 2);                    // Request 2 bytes from DS3231 and release I2C bus at end of reading
  temperature_msb = Wire.read();                // Read temperature MSB
  temperature_lsb = Wire.read();                // Read temperature LSB
 
  display_day();
  DS3231_display();                             // Diaplay time & calendar
 
  delay(50);                                    // Wait 50ms 
}
// End of code.
