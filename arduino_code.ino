//유량센서를 2번핀에 연결하여 유량을 얻는다.
//경광등은 12V 모터로, 릴레이 모듈을 사용하여 on/off를 설정한다. 
byte statusLed    = 13;

byte sensorInterrupt = 0;  
byte sensorPin       = 2;  //유량센서 핀

float calibrationFactor = 4.5;

volatile byte pulseCount;  

float flowRate;
unsigned int flowMilliLitres;
unsigned long totalMilliLitres;

unsigned long oldTime;

void setup()
{
  pinMode(13, OUTPUT);
  
  Serial.begin(9600);
   
  
  pinMode(statusLed, OUTPUT);
  digitalWrite(statusLed, HIGH); 
  
  pinMode(sensorPin, INPUT);
  digitalWrite(sensorPin, HIGH);

  pulseCount        = 0;
  flowRate          = 0.0;
  flowMilliLitres   = 0;
  totalMilliLitres  = 0;
  oldTime           = 0;

 
  attachInterrupt(sensorInterrupt, pulseCounter, FALLING);
}


void loop()
{
   while (Serial.available() > 0){ 
    char c = Serial.read();
    if(c=='1'){           //1일때 경광등 on, 0일때 off
      digitalWrite(13, HIGH);
    }else if(c=='0'){
      digitalWrite(13, LOW);
    }
   }

   if((millis() - oldTime) > 1000)   
  { 
    
    detachInterrupt(sensorInterrupt);
        
    flowRate = ((1000.0 / (millis() - oldTime)) * pulseCount) / calibrationFactor;
    
    oldTime = millis();
    flowMilliLitres = (flowRate / 60) * 1000;
    
    totalMilliLitres += flowMilliLitres;
      
    unsigned int frac;
    
    float flowRate_cm;
    flowRate_cm=flowRate*16.7/0.64;
    Serial.print(int(flowRate_cm));
    Serial.print("\n");
    

   
    attachInterrupt(sensorInterrupt, pulseCounter, FALLING);
  }
}


void pulseCounter()
{
  pulseCount++;
}
