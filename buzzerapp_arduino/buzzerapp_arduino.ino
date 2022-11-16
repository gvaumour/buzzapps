
#define INPUTS 3
volatile bool in[INPUTS];
volatile bool last_in[INPUTS];
const int in_pin[INPUTS] = {4,5,6};
const char* in_str[INPUTS] = {
  "Button0 pressed",
  "Button1 pressed",
  "Button2 pressed",
};

// Output
#define OUTPUTS 0
#if OUTPUTS > 0
const int out_pin[OUTPUTS] = {3};
const bool out_dft[OUTPUTS] = {false};

// Pair : met a HIGH, impair : met à LOW
// exemple : {"/ea fermer", "/ea ouvrir"} 
const char* out_cmd[OUTPUTS*2] = {
  "/set Led1 on","/set Led1 off"
};
#endif


bool update(bool force = false);

void setup()
{ 
  
	#if INPUTS > 0
	for(uint8_t i=0;i<INPUTS;i++)
	{
		in[i] = false;
		last_in[i] = false;
		pinMode(in_pin[i],INPUT_PULLUP);
	}
	#endif
    
	#if OUTPUTS > 0
	for(uint8_t i=0;i<OUTPUTS;i++)
	{
		pinMode(out_pin[i],OUTPUT);
		digitalWrite(out_pin[i],out_dft[i]?HIGH:LOW);
	}
	#endif
	
	Serial.begin(115200);
	delay(100);
    
}

void loop()
{
	static bool antirebond = false;
	
	if(antirebond)
		delay(100);
    
	#if INPUTS > 0
	for(uint8_t i=0;i<INPUTS;i++)
		in[i]  = (digitalRead(in_pin[i]) == LOW);
	#endif    

  if (Serial.available()> 0){
    String cmd = Serial.readString();    
    onCommand(cmd);
  }
  
	antirebond = update();
}

void onCommand(const String &cmd)
{	
	#if OUTPUTS > 0
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
	#endif	
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
