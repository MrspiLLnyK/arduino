#include <Arduino.h>
#include <Wire.h>

#include <avr/eeprom.h>

#define red_pin  11
#define green_pin  9
#define blue_pin  10


long degr;
int hue;
uint32_t myTimer1;


char str[20];    
int amount;

byte  data[10];
 

byte count = 0; 


char* offset;
float synNumber;

bool connected = false;
int inTest;


void setup() {
  Serial.begin(1000000);
  pinMode(red_pin, OUTPUT);
  pinMode(green_pin, OUTPUT);
  pinMode(blue_pin, OUTPUT); 
  Serial.setTimeout(1000);
  for (byte i = 0; i <= 4; i++ ) {
      data[i] = eeprom_read_byte(i);    
   }
  }

void setLedColor(int red, int green, int blue) {
  //Note that we are reducing 1/4 the intensity for the green and blue components because 
  //  the red one is too dim on my LED. You may want to adjust that.
  analogWrite(red_pin ,red); //Red pin attached to 9
  analogWrite(green_pin ,green/3); //Red pin attached to 9
  analogWrite(blue_pin ,blue/3);} //Red pin attached to 9}

void setLedColorHSV(int h, double s, double v) {
  //this is the algorithm to convert from RGB to HSV
  double r=0; 
  double g=0; 
  double b=0;
  
  int i=(int)floor(h/60.0);
  double f = h/60.0 - i;
  double pv = v * (1 - s);
  double qv = v * (1 - s*f);
  double tv = v * (1 - s * (1 - f));

  switch (i) {
  case 0: //rojo dominante
    r = v;
    g = tv;
    b = pv;
    break;
  case 1: //verde
    r = qv;
    g = v;
    b = pv;
    break;
  case 2: 
    r = pv;
    g = v;
    b = tv;
    break;
  case 3: //azul
    r = pv;
    g = qv;
    b = v;
    break;
  case 4:
    r = tv;
    g = pv;
    b = v;
    break;
  case 5: //rojo
    r = v;
    g = pv;
    b = qv;
    break;}
  
  //set each component to a integer value between 0 and 255
  int red=constrain((int)255*r,0,255);
  int green=constrain((int)255*g,0,255);
  int blue=constrain((int)255*b,0,255);
  setLedColor(red,green,blue);}

void staticColor(float pot, int red, int green, int blue, bool syn) {
  if (syn) {
    synNumber = (0.5*sin(radians(degr)/(pot * 20)) + 0.5);
    delay(1);
    degr++;  
    analogWrite(red_pin, floor(red*synNumber));
    analogWrite(green_pin, floor(green*synNumber));
    analogWrite(blue_pin, floor(blue*synNumber));
  } else {
    analogWrite(red_pin, ceil(red*pot));
    analogWrite(green_pin, ceil(green*pot));
    analogWrite(blue_pin, ceil(blue*pot));
  }
}

void loop() {
// ???????????????? ??.1
// 0|100|255|255|255 (0100255255255)send something like this into Serial to control LED strip 
// 1. Mode(0-2)
// 2. Speed or brightness(0-100)
// 3. Red color(0-255)
// 4. Green color(0-255)
// 5. Blue color(0-255) 

// ???????????????? ??.2
// 0|100|255|255|255 (0,100,255,255,255;) ?? ?????????????? ???????????? ?????????????????? ?????????????????????? ?????? "String" 
// ?????????? ?????? ???????????????????? ?????????????????? ?????????? ???????????? ?????????????? ???????? ?????? ???????????????????????? ???????????????????????? "String"
// ???? ?????????????????? ??????'??????, ???? ?? ?????????????????????? ?????????????????? ?????????????? ???????????????????? ???????? ?? EEPROM  

// data[0] == key   (0-2)
// data[1] == pot   (0-100)
// data[2] == red   (0-255)
// data[3] == green (0-255)
// data[4] == blue  (0-255)

  if (data[0] == 0) {
    //Breath mode
    staticColor(data[1]/100, data[2], data[3], data[4], true); 
  } else if (data[0] == 1) {
    //Static color mode
    staticColor(data[1]/100, data[2], data[3], data[4], false);
  } else if (data[0] == 2) {
    //Color wheel mode
    if (millis() - myTimer1 >= data[1] * 5) { 
      myTimer1 = millis();
      if (hue == 359) {
        hue = 0;}   
      setLedColorHSV(hue,1,1);
      hue++;}
  } else {
    // if "in Mode" != (0-2) , LED strip will got red
    analogWrite(red_pin, 255); 
    analogWrite(green_pin, 0);
    analogWrite(blue_pin, 10);
  }


  if (Serial.available() > 2) {
    amount = Serial.readBytesUntil(';', str, 20);   
    if (!connected) {
      if (str[0] == 'a') {
        delay(500);
        Serial.write('1');
        connected = true;
      }
    }
    
    str[amount] = NULL;    
    offset = str; 
    byte count = 0;

    while (true) { 
      data[count++] = atoi(offset);   
      offset = strchr(offset, ','); 
      if (offset) offset++;
      else break;
    } 
    
    for (byte i = 0; i <= count; i++ ) {
      eeprom_write_byte(i, data[i]);
    }    
  }
}
    

    // if (inMode == 0) {
    //   staticColor(pot, 255, 0, 0, false);
    // } else if (inMode == 1) {
    //   staticColor(pot, 0, 255, 0, false);
    // } else if (inMode == 2) {
    //   staticColor(pot, 0, 0, 255, false);
    // } else if (inMode == 3) {
    //   staticColor(pot, 255, 255, 255, false);
    // } else if (inMode == 4) {
    //   staticColor(pot, 0, 0, 0, true); 

    // } else if (inMode == 5) {
    //   analogWrite(red_pin, 0);
    //   analogWrite(green_pin, 0);
    //   analogWrite(blue_pin, 0);
    //   boolean loop_active = true;
    //   int loop_counter = 0;
    //   int RGB[3];
    //   while (loop_active) {
    //     int butt = !digitalRead(butt_pin);
    //     if (loop_counter == 3) {
    //       flag = 0;
    //       delay(20);
    //       break;}
    //     if (butt == 1 && flag == 0) {
    //       flag = 1;
    //       RGB[loop_counter] = map(analogRead(A0), 0, 1023, 0, 256);
    //       loop_counter++;
    //       delay(20);} 
    //     if (butt == 0 && flag == 1) {
    //       flag = 0;
    //       delay(20);}}
    //   boolean flag_2 = true;
    //   while (butt == 1) {
    //     int butt = !digitalRead(butt_pin);
    //     if (butt == 0) {
    //       break;}}
    //   while (flag_2){
    //     int butt = !digitalRead(butt_pin);
    //     if (butt == 1 && flag == 0) {
    //       flag = 1;
    //       pressCounter ++;
    //       delay(20);
    //       pressCounter = 6;
    //       break;}
    //     analogWrite(red_pin, RGB[0]);
    //     analogWrite(green_pin, RGB[1]);
    //     analogWrite(blue_pin, RGB[2]);}  
    // } else if (inMode == 6) {
    //   lcd.setCursor(2, 2);
    //   lcd.print("Got 6");
    //   lcd.setCursor(3, 3);
    //   lcd.print(pot);
    //   if (millis() - myTimer1 >= map(analogRead(A0), 0, 1023, 1, 81)) {   // ???????? ?????????????? (500 ????)
    //     myTimer1 = millis();
    //     if (hue == 359) {
    //       hue = 0;}   
    //     setLedColorHSV(hue,1,1);
    //     hue++;}}
    // } else {
      // lcd.clear();
      // lcd.setCursor(0, 0);
      // lcd.print(inChar);
      // lcd.setCursor(0, 1);
      // lcd.print(inChar[1]);
      // lcd.setCursor(1, 1);
      // lcd.print(inChar[2]);
      // lcd.setCursor(2, 1);
      // lcd.print(inChar[3]);
      // lcd.setCursor(0, 2);
      // // lcd.print(int(inChar[1]) + int(inChar[2]) + int(inChar[3]));
      // lcd.print(String(inChar[1]) + String(inChar[2]) + String(inChar[3]));

      // int x = ((inChar[1]) + String(inChar[2]) + String(inChar[3])).toInt();

      // if (x == 255){
      //   lcd.setCursor(0, 3);
        
      //   lcd.print("asdasd");
      
      // }
      

  // int butt = !digitalRead(butt_pin);
  // if (butt == 1 && flag == 0) {
  //   flag = 1;
  //   pressCounter ++;
  //   delay(20);}
  // if (butt == 0 && flag == 1) {
  //   flag = 0;
  //   delay(20);}
  

  // if (pressCounter != 4) {
    
  //   if (pressCounter == 7) {
  //     pressCounter =0;}
  //   if (pressCounter == 0 || pressCounter == 1 || pressCounter == 2 || pressCounter == 3) {
      
  //     analogWrite(red_pin, int(ceil(float(mode[pressCounter][0])*pot)));
  //     analogWrite(green_pin, int(ceil(float(mode[pressCounter][1])*pot)));
  //     analogWrite(blue_pin, int(ceil(float(mode[pressCounter][2])*pot))); }
    
  //   if (pressCounter == 5) {
  //   analogWrite(red_pin, 0);
  //   analogWrite(green_pin, 0);
  //   analogWrite(blue_pin, 0);
  //    boolean loop_active = true;
  //    int loop_counter = 0;
  //    int RGB[3];
  //    while (loop_active) {
  //     int butt = !digitalRead(butt_pin);
  //     if (loop_counter == 3) {
  //       flag = 0;
  //       delay(20);
  //       break;}
  //     if (butt == 1 && flag == 0) {
  //       flag = 1;
  //       RGB[loop_counter] = map(analogRead(A0), 0, 1023, 0, 256);
  //       loop_counter++;
  //       delay(20);} 
  //     if (butt == 0 && flag == 1) {
  //       flag = 0;
  //       delay(20);}}
  //   boolean flag_2 = true;
  //   while (butt == 1) {
  //     int butt = !digitalRead(butt_pin);
  //     if (butt == 0) {
  //       break;}}
  //   while (flag_2){
  //     int butt = !digitalRead(butt_pin);
  //     if (butt == 1 && flag == 0) {
  //       flag = 1;
  //       pressCounter ++;
  //       delay(20);
  //       pressCounter = 6;
  //       break;}
  //     analogWrite(red_pin, RGB[0]);
  //     analogWrite(green_pin, RGB[1]);
  //     analogWrite(blue_pin, RGB[2]);}}}


  //   if (pressCounter == 6) {
  //       if (millis() - myTimer1 >= map(analogRead(A0), 0, 1023, 1, 81)) {   // ???????? ?????????????? (500 ????)
  //         myTimer1 = millis();
  //         if (hue == 359) {
  //           hue = 0;}   
  //         setLedColorHSV(hue,1,1);
  //         hue++;}}
    
  // if (pressCounter == 4) {
  //   int pot_syn = ceil(map(analogRead(A0), 0, 1000, 1, 10));
  //   int x = (((255/2) + 0.5)*sin(radians(degr)/pot_syn) + (255/2) +0.5); 
  //   degr++;  
  //   analogWrite(red_pin, x);
  //   analogWrite(green_pin, x);
  //   analogWrite(blue_pin, x);}}

