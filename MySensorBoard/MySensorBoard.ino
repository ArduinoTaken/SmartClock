// NeoPixel Ring simple sketch (c) 2013 Shae Erisson
// Released under the GPLv3 license to match the rest of the
// Adafruit NeoPixel library
#include "DHT.h"
#define DHTTYPE DHT11   // DHT 11

#include <SPI.h>
#include <Wire.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>

#define SCREEN_WIDTH 128 // OLED display width, in pixels
#define SCREEN_HEIGHT 64 // OLED display height, in pixels

// Declaration for an SSD1306 display connected to I2C (SDA, SCL pins)
#define OLED_RESET     -1 // Reset pin # (or -1 if sharing Arduino reset pin)
Adafruit_SSD1306 display(SCREEN_WIDTH, SCREEN_HEIGHT, &Wire, OLED_RESET);
#define OLED_ADDR 0x3C

#include <Adafruit_NeoPixel.h>
#ifdef __AVR__
 #include <avr/power.h> // Required for 16 MHz Adafruit Trinket
#endif


#define LED_PIN A0
#define DHT11_PIN 15
#define LIGHT_PIN A2
#define HUMAN_PIN A1
#define BATT_PIN A3

DHT dht(DHT11_PIN, DHTTYPE);

// Which pin on the Arduino is connected to the NeoPixels?
//#define PIN        A0 // On Trinket or Gemma, suggest changing this to 1

// How many NeoPixels are attached to the Arduino?
#define NUMPIXELS 1 // Popular NeoPixel ring size

// When setting up the NeoPixel library, we tell it how many pixels,
// and which pin to use to send signals. Note that for older NeoPixel
// strips you might need to change the third parameter -- see the
// strandtest example for more information on possible values.
Adafruit_NeoPixel pixels(NUMPIXELS, LED_PIN, NEO_GRB + NEO_KHZ800);

#define DELAYVAL 500 // Time (in milliseconds) to pause between pixels


int light_human_count;
int dht11_count;
String info="";
bool display_isopened = true;


void setup() {
  // These lines are specifically to support the Adafruit Trinket 5V 16 MHz.
  // Any other board, you can remove this part (but no harm leaving it):
#if defined(__AVR_ATtiny85__) && (F_CPU == 16000000)
  clock_prescale_set(clock_div_1);
#endif
  // END of Trinket-specific code.

  pixels.begin(); // INITIALIZE NeoPixel strip object (REQUIRED)

  Serial.begin(9600);
  pinMode(HUMAN_PIN,INPUT);
  light_human_count = 0;
  dht.begin();
  // SSD1306_SWITCHCAPVCC = generate display voltage from 3.3V internally
  if(!display.begin(SSD1306_SWITCHCAPVCC, OLED_ADDR)) { // Address 0x3D for 128x64
    Serial.println(F("SSD1306 allocation failed"));
    for(;;); // Don't proceed, loop forever
  }
  // Show initial display buffer contents on the screen --
  // the library initializes this with an Adafruit splash screen.
  display.display();
  
  Serial.println("Welcome sensorbaord!");
  
}

void loop() {
  delay(5);
  light_human_count += 1;
  dht11_count += 1;
  
  if(light_human_count > 100){
    light_human_count = 0;
    info=get_light_human_value();
  }
  if(dht11_count > 400){
    dht11_count = 0;
    info+=get_dht11_value();
    info+=get_battery_value();
    display_info(info);
    info="";
  }
}
void display_info(String msg){
  display.clearDisplay();
  
  display.setTextSize(1);             // Normal 1:1 pixel scale
  display.setTextColor(WHITE);        // Draw white text
  display.setCursor(0,0);             // Start at top-left corner
  display.println(msg);
  
  display.display();
}
String get_battery_value(){
  int value_sum=0;
  for(int i=0;i<10;i++){
    value_sum = value_sum + analogRead(BATT_PIN);
    delay(20);
  }
  
  double value_batt=value_sum / 10.0000 * 8.6889 / 1000 * 1.1239;
  Serial.print("[BATT]:");
  Serial.println(value_batt);
  String msg = "[BATT]:" + String(value_batt)+"\n";
  return msg;
}
String get_dht11_value(){
  // Reading temperature or humidity takes about 250 milliseconds!
  // Sensor readings may also be up to 2 seconds 'old' (its a very slow sensor)
  float h = dht.readHumidity();
  // Read temperature as Celsius (the default)
  float t = dht.readTemperature();

  // Check if any reads failed and exit early (to try again).
  if (isnan(h) || isnan(t) ) {
    Serial.println(F("Failed to read from DHT sensor!"));
    return;
  }
  Serial.print(F("[Humidity]:"));
  Serial.print(h);
  Serial.print(F("%;[Temperature]: "));
  Serial.println(t-1.5);
  String msg = "[Humidity]:" +String(h)+"%\n[Temp]:"+String(t-1.5) +"C\n";
  return msg;
}
String get_light_human_value(){
  int value_light = analogRead(LIGHT_PIN);
  int value_human = digitalRead(HUMAN_PIN);
  //Serial.println("======-----------========");
  Serial.print("[LIGHT]:");
  Serial.print(value_light);
  Serial.print(";[HUMAN]:");
  Serial.println(value_human);
  if(value_light > 800){ //night
    if(1 == value_human){
      set_led(true);
    }else{
      set_led(false);
    }
  }else{ //day
    set_led(false);
  }
  if(1 == value_human && false == display_isopened){
    display.ssd1306_command(0xAF); //open display
    display_isopened = true;
  }
  if(0 == value_human){
    close_display();
  }
  String msg="[LIGHT]:"+String(value_light)+"\n[HUMAN]:"+String(value_human)+"\n";
  return msg;
}
void close_display(){
  if(true == display_isopened){
    display.ssd1306_command(0xAE);
    display_isopened=false;
  }
}
void set_led(bool light_status){
  
  pixels.clear(); // Set all pixel colors to 'off'
  if(!light_status){
    pixels.show();
    return;
  }
  // The first NeoPixel in a strand is #0, second is 1, all the way up
  // to the count of pixels minus one.
  for(int i=0; i<NUMPIXELS; i++) { // For each pixel...

    // pixels.Color() takes RGB values, from 0,0,0 up to 255,255,255
    // Here we're using a moderately bright green color:
    pixels.setPixelColor(i, pixels.Color(255, 255, 255));

    pixels.show();   // Send the updated pixel colors to the hardware.

    //delay(DELAYVAL); // Pause before next pass through loop
  }
}
