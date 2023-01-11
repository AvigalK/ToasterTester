#include <Stream.h>
#include <Wire.h>
#include <MCP23017.h>
int snc1_c_p = 2;
int snc1_c_n = 3;int snc2_c_p = 4;
int snc2_c_n = 5;int snc3_c_p = 6;
int snc3_c_n = 7;int act_c = 8;int swaddr_0 = 9;
int swaddr_1 = 10;
int swaddr_2 = 11;
int swaddr_3 = 12;int usb_en = A7;int VdigitalSense = A0;
int iE_CLK = A1;
int iE_DATA = A2;
int iE_VDIG = A3;
float tSNC1, tSNC2, tSNC3, tACT, tLed;
#define MCP23017_ADDR_0 0x20
#define MCP23017_ADDR_1 0x24MCP23017 mcp0 = MCP23017(MCP23017_ADDR_0);
MCP23017 mcp1 = MCP23017(MCP23017_ADDR_1);void setup() {  mcpinit();  mcp0.writePort(MCP23017Port::A, 0x00);
  mcp0.writePort(MCP23017Port::B, 0x00);
  mcp1.writePort(MCP23017Port::A, 0x00);
  mcp1.writePort(MCP23017Port::B, 0x00);  analogReference(EXTERNAL);
  tSNC1 = micros();
  tSNC2 = tSNC1;
  tSNC3 = tSNC1;
  tACT = tSNC1;
  tLed = tSNC1;
  // put your setup code here, to run once:
  Serial.begin(57600);
  while ( !Serial ) ;  pinMode(snc1_c_p, OUTPUT);
  pinMode(snc1_c_n, OUTPUT);
  digitalWrite(snc1_c_n, !digitalRead(snc1_c_p));  pinMode(snc2_c_p, OUTPUT);
  pinMode(snc2_c_n, OUTPUT);
  digitalWrite(snc2_c_n, !digitalRead(snc2_c_p));  pinMode(snc3_c_p, OUTPUT);
  pinMode(snc3_c_n, OUTPUT);
  digitalWrite(snc3_c_n, !digitalRead(snc3_c_p));  pinMode(act_c, OUTPUT);  pinMode(swaddr_0, OUTPUT);
  pinMode(swaddr_1, OUTPUT);
  pinMode(swaddr_2, OUTPUT);
  pinMode(swaddr_3, OUTPUT);  pinMode(usb_en, OUTPUT);
  digitalWrite(usb_en, 1);  pinMode(iE_CLK, OUTPUT);
  digitalWrite(iE_CLK, 0);  pinMode(iE_DATA, OUTPUT);
  digitalWrite(iE_DATA, 0);  pinMode(iE_VDIG, OUTPUT);
  digitalWrite(iE_VDIG, 0);}bool snc1_status = false;
float snc1_cycle = 5000;bool snc2_status = false;
float snc2_cycle = 5000;bool snc3_status = false;
int snc3_cycle = 5000;bool act_status = false;
float act_cycle = 50000;void loop() {  gen();
  if (Serial.available()) {
    Serial.println(">>>");
    String s = Serial.readStringUntil('\n');
    Serial.println(">>>" + s);
    String eintity;
    String function;
    String Value;
    int i = 0;
    int point = 0;
    while (s.charAt(i) != ' ' && i < s.length())
      i++;    eintity = s.substring(0, i);
    i++;
    point = i;    while (s.charAt(i) != ' ' && i < s.length())
      i++;
    function = s.substring(point, i);
    i++;
    point = i;    while (s.charAt(i) != ' ' && i < s.length())
      i++;
    Value = s.substring(point, i);    if (eintity == "snc1") {
      if ( function == "power")
      {
        if ( Value == "on") {
          snc1_status = true;
          Serial.println("snc1 is on");
        }
        else if ( Value == "off") {
          snc1_status = false;
          Serial.println("snc1 is off");
        }
      } else if ( function == "phase")
      {
        if ( Value == "on") {
          set_phase(1, true);
          Serial.println("snc1_p = snc1_n");
        }
        else if ( Value == "off") {
          set_phase(1, false);
          Serial.println("snc1_p = !snc1_n");
        }
      } else if ( function == "cycle") {
        snc1_cycle = Value.toInt();
        Serial.println("snc1 cycle set to" + Value);      }
    }    else if (eintity == "snc2") {
      if ( function == "power")
      {
        if ( Value == "on") {
          snc2_status = true;
          Serial.println("snc2 is on");
        }
        else if ( Value == "off") {
          snc2_status = false;
          Serial.println("snc2 is off");
        }
      } else if ( function == "phase")
      {
        if ( Value == "on") {
          set_phase(2, true);
          Serial.println("snc2_p = snc2_n");
        }
        else if ( Value == "off") {
          set_phase(2, false);
          Serial.println("snc2_p = !snc2_n");
        }
      } else if ( function == "cycle")
      {
        snc2_cycle = Value.toInt();
        Serial.println("snc2 cycle set to" + Value);
      }
    }
    else if (eintity == "snc3") {
      if ( function == "power")
      {
        if ( Value == "on")
        {
          snc3_status = true;
          Serial.println("snc3 is on");
        }
        else if ( Value == "off")
        {
          snc3_status = false;
          Serial.println("snc3 is off");
        }
      } else if ( function == "phase")
      {
        if ( Value == "on")
        {
          set_phase(3, true);
          Serial.println("snc3_p = snc3_n");
        }
        else if ( Value == "off")
        {
          set_phase(3, false);
          Serial.println("snc3_p = !snc3_n");
        }
      } else if ( function == "cycle") {
        snc3_cycle = Value.toInt();
        Serial.println("snc3 cycle set to" + Value);
      }
    } else if (eintity == "act") {
      if ( function == "power")
      {
        if ( Value == "on") {
          //  act_status=true;
          digitalWrite(act_c, HIGH);
          Serial.println("actuator is on");
        }
        else if ( Value == "off") {
          //  act_status=false;
          digitalWrite(act_c, LOW);
          Serial.println("actuator is off");
        }      } /*else if( function == "cycle")
                             {
                                 act_cycle =Value.toInt();
                                  Serial.println("actuator cycle set to" + Value);
                              }
*/
    } else if (eintity == "band") {
      if ( function == "select")
      {
        setAddr(Value.toInt());
        Serial.println("switch address set to" + Value);
      }
    } else if (eintity == "Vdigital") {
      if ( function == "read")
      {
        float sensorValue = analogRead(VdigitalSense);
        for (int i = 1; i < 10; i++) {
          sensorValue += analogRead(VdigitalSense);
          delay(3);
        }
        Serial.println(sensorValue * 4.5 / (10240));
      }
    } else if (eintity == "indicate")  {
      indicateBoardStatus(function.toInt(), Value);
      mcpPrintState();
    } else if (eintity == "Flasher") {
      if (function == "ena") {
        digitalWrite(usb_en, 1);
        Serial.println(" Flasher Enabled");
      }
      else if (function == "dis")
      {
        digitalWrite(usb_en, 0);
        Serial.println(" Flasher Disabled");
      }
    }  }}void set_phase (int snc, bool phase) {  switch (snc) {
    case 1:
      if (phase)
        digitalWrite(snc1_c_n, digitalRead(snc1_c_p));
      else
        digitalWrite(snc1_c_n, !digitalRead(snc1_c_p));
      break;
    case 2:
      if (phase)
        digitalWrite(snc2_c_n, digitalRead(snc2_c_p));
      else
        digitalWrite(snc2_c_n, !digitalRead(snc2_c_p));
      break;
    case 3:
      if (phase)
        digitalWrite(snc3_c_n, digitalRead(snc3_c_p));
      else
        digitalWrite(snc3_c_n, !digitalRead(snc3_c_p));
      break;
    default:
      Serial.println(" wrong channel enterd");
      break;
  }}void gen() {  //  Serial.println(snc1_cycle/2);
  if (snc1_status && micros() - tSNC1 >= snc1_cycle / 2) {
    digitalWrite(snc1_c_p, !digitalRead(snc1_c_p));
    digitalWrite(snc1_c_n, !digitalRead(snc1_c_n));
    tSNC1 = micros();
  }  if (snc2_status && micros() - tSNC2 >= snc2_cycle / 2) {
    digitalWrite(snc2_c_p, !digitalRead(snc2_c_p));
    digitalWrite(snc2_c_n, !digitalRead(snc2_c_n));
    tSNC2 = micros();
  }  if (snc3_status && micros() - tSNC3 >= snc3_cycle / 2) {
    digitalWrite(snc3_c_p, !digitalRead(snc3_c_p));
    digitalWrite(snc3_c_n, !digitalRead(snc3_c_n));
    tSNC3 = micros();
  }  if (act_status && micros() - tACT >= act_cycle / 2) {
    digitalWrite(act_c, !digitalRead(act_c));
    tACT = micros();
  }  if ( micros() - tLed >= 500000) {
    //mcpTogle();
    tLed = micros();
  }
}void setAddr(byte addr) {
  digitalWrite(swaddr_0, (addr & 0x01));
  digitalWrite(swaddr_1, (addr & 0x02) >> 1);
  digitalWrite(swaddr_2, (addr & 0x04) >> 2);
  digitalWrite(swaddr_3, (addr & 0x08) >> 3);
}void indicateBoardStatus(uint8_t pcb, String state)
{
  uint8_t _state;  if (state == "fail")
    _state = 2;
  else if (state == "test")
    _state = 0;
  else if (state == "pass")
    _state = 1;
  else {
    Serial.println(" wrong pcb status");
    return;
  }
  mcpPcbLedOn(pcb, _state);
}void mcpPcbLedsOff(uint8_t pcb)
{  for (int i = 0; i <= 2 ; i++) {
    mcpWritePin(pcb * 3 + i, 0);
  }
}void mcpPcbLedOn(uint8_t pcb, uint8_t state)
{
  mcpPcbLedsOff(pcb);
  mcpWritePin(pcb * 3 + state, 1);
  Serial.println(pcb * 3 + state);
}void mcpWritePin(uint8_t pin, uint8_t state) {  if (pin <= 15)
    mcp0.digitalWrite(pin, state);
  else
    mcp1.digitalWrite(pin - 16, state);}uint8_t gpio0, gpio1, gpio2, gpio3, tog = 0;void mcpTogle() {
  if (tog == 0) {
    gpio0 = mcp0.readPort(MCP23017Port::A);
    gpio1 = mcp0.readPort(MCP23017Port::B);
    gpio2 = mcp1.readPort(MCP23017Port::A);
    gpio3 = mcp1.readPort(MCP23017Port::B);
    mcp0.writePort(MCP23017Port::A, 0);
    mcp0.writePort(MCP23017Port::B, 0);
    mcp1.writePort(MCP23017Port::A, 0);
    mcp1.writePort(MCP23017Port::B, 0);
    tog = 1;
  }
  else {
    mcp0.writePort(MCP23017Port::A, gpio0);
    mcp0.writePort(MCP23017Port::B, gpio1);
    mcp1.writePort(MCP23017Port::A, gpio2);
    mcp1.writePort(MCP23017Port::B, gpio3);
  }}void mcpPrintState() {
  gpio0 = mcp0.readPort(MCP23017Port::A);
  gpio1 = mcp0.readPort(MCP23017Port::B);
  gpio2 = mcp1.readPort(MCP23017Port::A);
  gpio3 = mcp1.readPort(MCP23017Port::B);
  Serial.println(gpio0, BIN);
  Serial.println(gpio1, BIN);
  Serial.println(gpio2, BIN);
  Serial.println(gpio3, BIN);}
void mcpinit() {
  Wire.begin();  mcp0.init();  mcp1.init();
  mcp0.portMode(MCP23017Port::A, 0);
  mcp0.portMode(MCP23017Port::B, 0);
  mcp1.portMode(MCP23017Port::A, 0);
  mcp1.portMode(MCP23017Port::B, 0);
  mcp0.writeRegister(MCP23017Register::GPIO_A, 0x00);
  mcp0.writeRegister(MCP23017Register::GPIO_B, 0x00);
  mcp1.writeRegister(MCP23017Register::GPIO_A, 0x00);
  mcp1.writeRegister(MCP23017Register::GPIO_B, 0x00);
}
