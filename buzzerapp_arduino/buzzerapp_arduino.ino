#include <Arduino.h>
#include <Wire.h> // TwoWire, Wire
#include <AceWire.h> // TwoWireInterface
#include <AceSegment.h> // Ht16k33Module

using ace_wire::TwoWireInterface;
using ace_segment::LedModule;
using ace_segment::Ht16k33Module;

using WireInterface = TwoWireInterface<TwoWire>;
WireInterface wireInterface(Wire);


#define INPUTS 5
volatile bool in[INPUTS];
volatile bool last_in[INPUTS];
const int in_pin[INPUTS] = {10,3,4,6,9};
const char* in_str[INPUTS] = {
  "white pressed",
  "yellow pressed",
  "blue pressed",
  "green pressed",
  "red pressed",
};

#define OUTPUTS 5
const int out_pin[OUTPUTS] = {11,2,5,7,8};
const bool out_dft[OUTPUTS] = {false,false,false,false,false};

const char* out_cmd[OUTPUTS*2] = {
  "/set whiteLed on","/set whiteLed off",
  "/set yellowLed on","/set yellowLed off",
  "/set blueLed on","/set blueLed off",
  "/set greenLed on","/set greenLed off",
  "/set redLed on","/set redLed off"
};


#define NB_7SEGMENTS 5

const uint8_t SDA_PIN = SDA;
const uint8_t SCL_PIN = SCL;
const uint8_t NUM_DIGITS = 4;

// LED segment patterns.
const uint8_t NUM_PATTERNS = 10;
const uint8_t PATTERNS[NUM_PATTERNS] = {
  0b00111111, // 0
  0b00000110, // 1
  0b01011011, // 2
  0b01001111, // 3
  0b01100110, // 4
  0b01101101, // 5
  0b01111101, // 6
  0b00000111, // 7
  0b01111111, // 8
  0b01101111, // 9
};

Ht16k33Module<WireInterface, NUM_DIGITS> score_red(
    wireInterface, 0x71);
Ht16k33Module<WireInterface, NUM_DIGITS> score_blue(
    wireInterface, 0x74);
Ht16k33Module<WireInterface, NUM_DIGITS> score_yellow(
    wireInterface, 0x70);
Ht16k33Module<WireInterface, NUM_DIGITS> score_green(
    wireInterface, 0x73);
Ht16k33Module<WireInterface, NUM_DIGITS> score_white(
    wireInterface, 0x72);

bool update(bool force = false);
const byte numChars = 32;
char receivedChars[numChars]; 
boolean newSerialData  = false;

void setup()
{ 
  // Init button switches
	for(uint8_t i=0;i<INPUTS;i++) {
		in[i] = false;
		last_in[i] = false;
		pinMode(in_pin[i],INPUT_PULLUP);
	}

  // Init button leds
	for(uint8_t i=0;i<OUTPUTS;i++) {
		pinMode(out_pin[i],OUTPUT);
		digitalWrite(out_pin[i],out_dft[i]?HIGH:LOW);
	}

 // Init scores
  Wire.begin();
  wireInterface.begin();
  score_red.begin();
  score_yellow.begin();
  score_white.begin();
  score_green.begin();
  score_blue.begin();

  score_blue.setBrightness(2);
  score_red.setBrightness(2);
  score_green.setBrightness(2);
  score_yellow.setBrightness(2);
  score_white.setBrightness(2);
  
  reset_scores();
  
	Serial.begin(115200);
	delay(100);
    
}

void reset_scores() {
   for (int i = 0 ; i < 4 ; i++)
     score_red.setPatternAt(i, 0);
   score_red.flush();

   for (int i = 0 ; i < 4 ; i++)
     score_yellow.setPatternAt(i, 0);
   score_yellow.flush();

   for (int i = 0 ; i < 4 ; i++)
     score_green.setPatternAt(i, 0);
   score_green.flush();    

   for (int i = 0 ; i < 4 ; i++)
     score_white.setPatternAt(i, 0);
   score_white.flush();

   for (int i = 0 ; i < 4 ; i++)
     score_blue.setPatternAt(i, 0);
   score_blue.flush();
   
}

void display_score(String param_color, String param_score) {

  String color = param_color;
  color.trim();
  String score = param_score;
  score.trim();

  int index_score = 0;

  for (int i = 0 ; i < 4 ; i++) {
    if (score.length() >= (4-i)){
      int value = score[index_score++] - '0';
      if (color == "red") 
        score_red.setPatternAt(i, PATTERNS[value]);
      if (color == "yellow")
        score_yellow.setPatternAt(i, PATTERNS[value]);
      if (color == "blue")
        score_blue.setPatternAt(i, PATTERNS[value]);
      if (color == "white") 
        score_white.setPatternAt(i, PATTERNS[value]);
      if (color == "green")
        score_green.setPatternAt(i, PATTERNS[value]);
    }
    else {
      if (color == "red") 
        score_red.setPatternAt(i, 0);
      if (color == "yellow")
        score_yellow.setPatternAt(i, 0);
      if (color == "blue")
        score_blue.setPatternAt(i, 0);
      if (color == "white") 
        score_white.setPatternAt(i, 0);
      if (color == "green")
        score_green.setPatternAt(i, 0);
    }
  }
  if (color == "red") 
    score_red.flush();
  if (color == "yellow")
    score_yellow.flush();
  if (color == "blue")
    score_blue.flush();
  if (color == "white") 
    score_white.flush();
  if (color == "green")
    score_green.flush();
}

void loop()
{
	static bool antirebond = false;
	
	if(antirebond)
		delay(20);
    
	for(uint8_t i=0;i<INPUTS;i++)
		in[i]  = (digitalRead(in_pin[i]) == LOW);

  recvFromSerial();

  if (newSerialData == true) {
    processCommand();
  }

	antirebond = update();
}

void recvFromSerial() {
    static byte ndx = 0;
    char endMarker = '\n';
    char rc;
    
    if (Serial.available() > 0) {
        rc = Serial.read();
        if (rc != endMarker) {
            receivedChars[ndx] = rc;
            ndx++;
            if (ndx >= numChars) {
                ndx = numChars - 1;
            }
        }
        else {
            receivedChars[ndx] = '\0';
            ndx = 0;
            newSerialData = true;
        }
    }
}

void processCommand()
{	

  String cmd = String(receivedChars);
	for(uint8_t i=0;i<OUTPUTS;i++) {
		if(strlen(out_cmd[i*2]) > 0 && cmd.startsWith(out_cmd[i*2])) {
			digitalWrite(out_pin[i],HIGH);
		}
		else if(strlen(out_cmd[i*2+1]) > 0 && cmd.startsWith(out_cmd[i*2+1])) {
			digitalWrite(out_pin[i],LOW);
		}
	}
  
  if(cmd.startsWith("/set allLeds on")) {
    for(uint8_t i=0;i<OUTPUTS;i++) {
      digitalWrite(out_pin[i],HIGH);
    }
  }
  
  if(cmd.startsWith("/set allLeds off")) {
    for(uint8_t i=0;i<OUTPUTS;i++) {
      digitalWrite(out_pin[i],LOW);
    }
  }

  if(cmd.startsWith("/set score")) {

    int index_color = cmd.indexOf(' ', 11);
    String color = cmd.substring(11, index_color );
    String score_str = cmd.substring(index_color, cmd.charAt(cmd.length() - 1));
    display_score(color, score_str);
  }

  if(cmd.startsWith("/reset scores")) {
    reset_scores();
  }

  newSerialData = false;

}

bool update(bool force)
{
	bool changed = false;
	
	#if INPUTS > 0
	for(uint8_t i=0;i<INPUTS;i++)
	{
		if(in[i] != last_in[i] || force)
		{
			changed = true;
			if(in[i])
				Serial.println(in_str[i]);
			
			last_in[i] = in[i];
		}
	}
	#endif	
	return changed;
}
