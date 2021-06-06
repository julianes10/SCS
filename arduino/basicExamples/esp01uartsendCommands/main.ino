// GOT FROM http://www.martyncurrey.com/arduino-to-esp8266-serial-commincation/
// Basic serial communication with ESP8266
// Uses serial monitor for communication with ESP8266
//
//  Pins
//  Arduino pin 2 (RX) to ESP8266 TX
//  Arduino pin 3 to voltage divider then to ESP8266 RX
//  Connect GND from the Arduiono to GND on the ESP8266
//  Pull ESP8266 CH_PD HIGH
//
// When a command is entered in to the serial monitor on the computer 
// the Arduino will relay it to the ESP8266
//

#include <SoftwareSerial.h>
SoftwareSerial ESPserial(3, 4); // RX | TX

#include <Adafruit_Sensor.h>
#include <DHT.h>
DHT GLBsensorDHT(5, DHT22);
float GLBsensorDHTTemp=0.0;
float GLBsensorDHTHum=0.0;

void setup() 
{
    Serial.begin(9600);     // communication with the host computer
    //while (!Serial)   { ; }
    
    // Start the software serial for communication with the ESP8266
    ESPserial.begin(9600);  
    //ESPserial.begin(115200);
    Serial.println("");
    Serial.println("Remember to to set Both NL & CR in the serial monitor.");
    Serial.println("Ready");
    Serial.println("");    
    ESPserial.print("AT\r\n");
    ESPserial.print("AT\r\n");
    ESPserial.print("AT\r\n");
}

void sendData(){

  GLBsensorDHTTemp = GLBsensorDHT.readTemperature();
  GLBsensorDHTHum  = GLBsensorDHT.readHumidity();

        Serial.println("send data...");
        ESPserial.print("AT+CIPMUX=1\r\n");
        delay(1000);
        ESPserial.print("AT+CIPSTART=4,\"UDP\",\"192.168.1.55\",3000,1112,0\r\n");
        delay(1000);
        ESPserial.print("AT+CIPSEND=4,14\r\n"); //TODO NOT SURE LENGHT
        delay(1000);
        ESPserial.print("HOLA:");
        ESPserial.print(GLBsensorDHTTemp,1);
        ESPserial.print(",");
        ESPserial.print(GLBsensorDHTHum,1);
        ESPserial.print(",000\r\n");
        delay(1000);
        ESPserial.print("AT+CIPCLOSE=4\r\n");
}
int count=0;
void loop() 
{

    // listen for communication from the ESP8266 and then write it to the serial monitor
    if ( ESPserial.available() )   {
      //Serial.print("RX:");
      unsigned char aux=ESPserial.read();
      if (aux!=0) {
        Serial.write(aux);  
        /*Serial.print("[");
        Serial.print(aux, HEX);
        Serial.print("]");*/
      }
    }

    // listen for user input and send it to the ESP8266
    if ( Serial.available() )       {
      //Serial.println("");
      char aux=Serial.read();
      //Serial.print("TX:");
      //Serial.print(aux);
      //Serial.print("[");
      //Serial.print(aux, HEX);
      //Serial.print("]");      
      //ESPserial.write(aux);
      if (aux == 'a')   {
        Serial.println("Ping");
        ESPserial.print("AT\r\n");
      }      
      if (aux == 'c')   {
        Serial.println("Set mode as client");
        ESPserial.print("AT+CWMODE=1\r\n");
      }      
      if (aux == 'l')   {
        Serial.println("List access points");
        ESPserial.print("AT+CWLAP\r\n");
      }  
      if (aux == 'B')   {
        Serial.println("Set Baudrate");
        ESPserial.print("AT+UART_DEF=9600,8,1,0,0\r\n");
        ESPserial.begin(9600);  
      }      
      if (aux == 'J')   {
        Serial.println("Join urban");
        ESPserial.print("AT+CWJAP=\"URBAN\",\"BASURABASURA.1\"\r\n");
      } 
      if (aux == 't')   {
        Serial.println("test...");
        ESPserial.print("AT+CWJAP?\r\n");
      }      
          
      if (aux == 's')   {
        Serial.println("status...");
        ESPserial.print("AT+CIPSTATUS\r\n");
      }   
      if (aux == 'x')   {
        sendData();
        
      }  
    }
    
    count++;
    if (count%5000==0) sendData();
    
}
