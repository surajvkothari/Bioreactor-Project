/*
 sketch.ino

 Copyright 2020 - Suraj, Iason, Arslan, Arnas
  
 */
#include <stdio.h>
#include <string.h>
#include <Wire.h> // for pH

// These define which pins are connected to what device on the virtual bioreactor
//
const byte lightgatePin  = 2;
const byte stirrerPin    = 5;
const byte heaterPin     = 6;
const byte thermistorPin = A0;
const byte pHPin         = A1;


// Initialise setpoints
double heatingSetpoint = 25;
int stirringSetpoint = 0;
float pHSetpoint = 5;


/* Heating subsystem constants */
const int windowSamples = 70;

float voltageMultiplier = 5.0;
float lowerTemp = 25.0;
float higherTemp = 35.0;
float setPoint;

//PID constants and vars
float pidErrorOld,pidError;
float pidP,pidI,pidD;
float pConst = 70;
float iConst = 40;
float dConst = 40;
float Time,TimeOld;


/* stirring subsystem constants */
int pwm;
double TrueRPM = 0;

unsigned long currentTimePhoto; // timing to get TrueRPM
unsigned long previousTimePhoto = 0; // subtract from currentTimePhoto
// to get time difference since last collection of data over 1000ms
volatile unsigned long ticker = 0, firstTick = 0; // ticks +1 for every Rising pin2
volatile unsigned long tickNum; // ticks in (currentTimePhoto - previousTimePhoto) time
volatile unsigned long prevTicker = 0; // prev tickNum at last collection

// PID
unsigned long currentTimePID;
unsigned long prevTimePID = 0;
int elapsedPID;
int error = 0;
int prevError = 0;
int errorIntegral;
float errorDeriv;


/* pH subsystem constants */
#define MODE1 0x00
#define PRESCALE 0xFE
#define OSCILLATORF 25000000
bool changepH = 1;
const byte PCA_addr = 0x40; //default PCA address


int delay_counter = 0;

// The PCA9685 is connected to the default I2C connections. There is no need
// to set these explicitly.
void setup() {
  Serial.begin(9600);

  pinMode(lightgatePin,  INPUT);
  pinMode(stirrerPin,    OUTPUT);
  pinMode(heaterPin,     OUTPUT);
  pinMode(thermistorPin, INPUT);
  pinMode(pHPin,         INPUT);
  
  /* Heating subsystem setup */
  Time = millis();
  
  /* Stirring subsystem setup */
  attachInterrupt(digitalPinToInterrupt(lightgatePin), tickCount, RISING);
  
  /* pH subsystem setup */
  Wire.begin();
  write(MODE1, 0x80); //Reset PCA

  float prescaleval = ((OSCILLATORF/(1000*4096.0))+0.5)-1; //Set PWM frequency to 1000Hz
  uint8_t prescale = (uint8_t)prescaleval;

  Wire.beginTransmission(PCA_addr);
  Wire.write(MODE1);
  Wire.endTransmission();
  Wire.requestFrom((uint8_t)PCA_addr, (uint8_t)1);

  uint8_t oldmode = Wire.read();
  uint8_t newmode = (oldmode & 0x80) | 0x10;

  write(MODE1, newmode);
  write(PRESCALE, prescale);
  write(MODE1, oldmode);
  write(MODE1, oldmode | 0x80); //Reset PCA
  
  
  Serial.println("Start Bioreactor Interface...");
  delay(3000);
}


/* HEATING SUBSYSTEM FUNCTIONS */
float calibrateTemp(float temp)
{
    temp = 1.07*(temp) + -21.3;
    return temp;
}


float getVoltage()
{
    int inputValue = analogRead(thermistorPin);
    float inputVoltage = inputValue * voltageMultiplier;
    inputVoltage /= 1024.0;
    inputVoltage = (inputVoltage);
    return inputVoltage;
}


float calcTemp(float inputVoltage)
{
    float totalTemp = 0;
    for(int index =0;index<5;index++)
    {
        float temperatureK =  -17.7*(inputVoltage) + 70 + 273.15; //THIS NEEDS TO CHANGE
        temperatureK = calibrateTemp(temperatureK);
        totalTemp+=temperatureK;
    }
    float avgTemperatureK = totalTemp/5.0;
    //Serial.print(inputVoltage*1000.0);
    //Serial.println("mV ");
    //Serial.print(avgTemperatureK);
    //Serial.println("K");
    return avgTemperatureK;
}


void manageHeater(float heatingSetPoint,float currentTemp)
{
    //P
    pidError = (heatingSetPoint+273.15)-currentTemp; //negative denotes we are above the setpoint and positve denotes being below the heatingSetPoint.
    pidErrorOld = pidError;
    pidP = pidError*pConst;
    //I
    if(fabs(pidError)<5)
    {
        float pidI = (pidError*iConst) + pidI;
    }
    //D
    TimeOld = Time;
    Time = millis();  
    pidD = ((pidError-pidError)/((Time-TimeOld)/1000))*dConst;
    float PID = pidP+pidI+pidD;
    //Serial.print("The PID is");
    //Serial.println(PID);
    if(PID>255) // we are below the setpoint MUST ACTUATE
    {
        PID =255; //prevent actuator saturation
    }
    else if (PID<0) //we are above the setpoint MUST TURN OFF  
    {
        PID = 0; //prevent actuator starvation
    }
    analogWrite(heaterPin, PID);
}


float AverageVoltage()
{
  float voltageTotal = 0.0;
  for(int index =0;index<windowSamples;index++)
  {
    float voltageReading = getVoltage();
    voltageTotal= voltageTotal+voltageReading;
    delay(1);
  }
  float voltageAverage = voltageTotal/windowSamples;  
  return voltageAverage;
}


/* Stirring SUBSYSTEM FUNCITONS */
void tickCount() {
  ticker++;
  //firstTick++;
}


/* pH SUBSYSTEM FUNCTIONS */
float getpHData(){

  int n = 10; //Moving average 15 is enough, less could be used, if speed is required

  float currentpH = 0;

  for(int i = 0; i < n; i++){

    currentpH = currentpH + float(analogRead(pHPin));

  }

  currentpH = (currentpH/n - 65.7)/61.4; //from error analysis, we have to only account for two types of errors (datasheet), so only two variables used

  return currentpH;

}
 

void write(uint8_t addr, uint8_t d){
  //Moving pointer to register addr, and putting data d there

  Wire.beginTransmission(PCA_addr);
  Wire.write(addr);
  Wire.write(d);
  Wire.endTransmission();

}


void setMotorSpeed(float PWM, uint8_t n){

  if (PWM == 0){

    //Turning off motor by changing 4th bit to 1 in register LED0_OFF_H

    write(0x09 + n*4, 0x10);

  }

  else {
    //Read datasheet of PCA for more explanation

    int onTime = PWM * 4095;

    int offTime = 410 + onTime - 1;

    uint8_t L = offTime;

    uint8_t H = (offTime >> 8) & B00001111;

    write(0x06 + 4*n, 0x99);

    write(0x07 + 4*n, 0x01);

    write(0x08 + 4*n, L);

    write(0x09 + 4*n, H);

  }

}


String heating_subsystem() {
    //Serial.print("The setpoint is ");
    //Serial.print(heatingSetpoint +273.15);
    //Serial.print(" | The Temperature is ");
    float inputVoltage = AverageVoltage();
    float currentTemp = calcTemp(inputVoltage);

    manageHeater(heatingSetpoint,currentTemp);
    
    //Serial.println("=======");
    return String(currentTemp-273.15);
}


String stirring_subsystem() {
  currentTimePhoto = millis();
  
  unsigned long interval = currentTimePhoto - previousTimePhoto;

  if (interval >= 1000) {
    if (interval > 0) {
    	TrueRPM = ticker * 30000.0 / interval;
        previousTimePhoto = currentTimePhoto;
        ticker = 0;
    } 
    else {
      TrueRPM = 0;
    }
  }
 
  // PID
  currentTimePID = millis();
  elapsedPID = (currentTimePID - prevTimePID);
  
  error = stirringSetpoint - TrueRPM;
  errorIntegral = error * (elapsedPID / 100);
  errorDeriv = -(prevError - error)/elapsedPID;
  
  prevError = error;
  prevTimePID = currentTimePID;
 
  
  if (error > 10 || error < -10) { 
      pwm = (int)(0.008*error + 0.009*errorIntegral + 0.03*errorDeriv) + pwm;
  }

  if (pwm >= 255) {pwm = 255;}
  if (pwm <= 0) {pwm = 0;}
  
  analogWrite(stirrerPin, pwm);
  /*
  Serial.print("Current RPM: ");
  Serial.print(TrueRPM);
  Serial.print(" | Setpoint RPM: ");
  Serial.print(stirringSetpoint);
  Serial.print(" | PWM: ");
  Serial.println(pwm);
   */
  return String(TrueRPM);
}

String pH_subsystem() {
  float currentpH = getpHData();

  currentpH = int(currentpH *100.0)/100.0;

  //Serial.println(currentpH);

  //if (currentpH == pHSetpoint){}

  if (!(currentpH - pHSetpoint < 0.1 & currentpH - pHSetpoint > -0.1) && changepH){

    float A = 6.5;

    float B = 2.302;

    float e = 2.71828;

    bool negativeWaitTime = 0;

   

    int waitTime = pow(e, A*B)*(pow(e, -B*pHSetpoint)-pow(e, -B*currentpH));

    if (waitTime < 0){

        waitTime = -1* waitTime;

        negativeWaitTime = 1;

    }

    waitTime = waitTime / 10;

    //Serial.println(waitTime);

    if (waitTime == 0){

      waitTime = 1;

    }

    if (!negativeWaitTime){

      setMotorSpeed(0.1, 0);

      delay(waitTime);

      setMotorSpeed(0,0);

    }

    else{

      setMotorSpeed(0.1, 1);

      delay(waitTime);

      setMotorSpeed(0,1);

    }

   

    //delay(100);

  }
  
  return String(currentpH);
}



/*
The following ID's mean:
HR - Heating Data for python to READ
SR - Stirring Data for python to READ
PR - pH Data for python to READ

HW - Heating Data written from Python
SW - Heating Data written from Python
PW - Heating Data written from Python
*/

void readData() {
    if (Serial.available() > 0) {
      String line = Serial.readString();
      String ID = line.substring(0,2);  // First 2 characters
      String data = line.substring(2);

      if (ID == "HW") {
  	heatingSetpoint = data.toFloat();
      }
      else if (ID == "SW") {
	stirringSetpoint = data.toInt();
      }
      else if (ID == "PW") {
	pHSetpoint = data.toFloat();
      }
    }
}
 
 
void writeToPython(String heatingCurrent, String stirringCurrent, String phCurrent) {
    // Bytes format: HR298.01;SR600;PR5
    String bytes = "HR"+heatingCurrent+";"+"SR"+stirringCurrent+";"+"PR"+phCurrent;
    Serial.println(bytes);
}


void loop() {
    readData();
    String heatingCurrentVal = heating_subsystem();
    String stirringCurrentVal = stirring_subsystem();
    String pHCurrentVal = pH_subsystem();
    if (delay_counter % 10 == 0) {
	writeToPython(heatingCurrentVal, stirringCurrentVal, pHCurrentVal);
    }
    delay_counter += 1;
    delay(100);
}
