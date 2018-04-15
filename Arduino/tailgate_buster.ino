#include "Ultrasonic.h"
#include <Wire.h>
#include "rgb_lcd.h"

Ultrasonic ultrasonic(6);
rgb_lcd lcd;
char dtaUart[15];
int counter = 0;
void setup()
{
    Serial.begin(9600);
    lcd.begin(16, 2);

}
void loop()
{
    long RangeInInches;
    long RangeInCentimeters;
    
    RangeInCentimeters = ultrasonic.MeasureInCentimeters(); // measure in centimeter
    //Serial.print(RangeInCentimeters);//0~400cm
    //Serial.println(" cm");

    if(RangeInCentimeters < 10 && counter < 5)
    {
        lcd.setRGB(255, 0, 0);
        delay(500);
        lcd.setRGB(0, 0, 0);
        counter++;
    }
    else if (RangeInCentimeters < 10 && counter >=5){
      lcd.setRGB(255, 0, 0);
      Serial.println("on");
    }
    else
    {
      //Serial.println("off");
      lcd.setRGB(0, 0, 0);
      counter = 0;
    }
    delay(250);
}
