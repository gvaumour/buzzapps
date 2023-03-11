
#define INPUTS 5
volatile bool in[INPUTS];
volatile bool last_in[INPUTS];
const int in_pin[INPUTS] = {11,3,4,6,9};
const char* in_str[INPUTS] = {
  "white pressed",
  "yellow pressed",
  "blue pressed",
  "green pressed",
  "red pressed",
};

#define OUTPUTS 5
const int out_pin[OUTPUTS] = {10,2,5,7,8};
const bool out_dft[OUTPUTS] = {false,false,false,false,false};

const char* out_cmd[OUTPUTS*2] = {
  "/set whiteLed on","/set whiteLed off",
  "/set yellowLed on","/set yellowLed off",
  "/set blueLed on","/set blueLed off",
  "/set greenLed on","/set greenLed off",
  "/set redLed on","/set redLed off"
};

bool update(bool force = false);

const byte numChars = 32;
char receivedChars[numChars]; 
boolean newSerialData  = false;

void setup()
{ 
	for(uint8_t i=0;i<INPUTS;i++)
	{
		in[i] = false;
		last_in[i] = false;
		pinMode(in_pin[i],INPUT_PULLUP);
	}
    
	for(uint8_t i=0;i<OUTPUTS;i++)
	{
		pinMode(out_pin[i],OUTPUT);
		digitalWrite(out_pin[i],out_dft[i]?HIGH:LOW);
	}
	
	Serial.begin(115200);
	delay(100);
    
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
	for(uint8_t i=0;i<OUTPUTS;i++)
	{
		if(strlen(out_cmd[i*2]) > 0 && cmd.startsWith(out_cmd[i*2]))
		{
			digitalWrite(out_pin[i],HIGH);
			return;
		}
		else if(strlen(out_cmd[i*2+1]) > 0 && cmd.startsWith(out_cmd[i*2+1]))
		{
			digitalWrite(out_pin[i],LOW);
			return;
		}
	}
  
  if(cmd.startsWith("/set allLeds on"))
  {
    for(uint8_t i=0;i<OUTPUTS;i++)
    {
      digitalWrite(out_pin[i],HIGH);
    }
    return;
  }
  if(cmd.startsWith("/set allLeds off"))
  {
    for(uint8_t i=0;i<OUTPUTS;i++)
    {
      digitalWrite(out_pin[i],LOW);
    }
    return;
  }
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
