#include <Stream.h>


int snc1_c_p =2;
int snc1_c_n =3;

int snc2_c_p =4;
int snc2_c_n =5;

int snc3_c_p =6;
int snc3_c_n =7;

int act_c = 8;

int swaddr_0 = 9;
int swaddr_1 = 10;
int swaddr_2 = 11;
int swaddr_3 = 12;

int VdigitalSense = A0; 

float tSNC1,tSNC2,tSNC3,tACT;

void setup() {
  tSNC1=micros();
  tSNC2=tSNC1;
  tSNC3=tSNC1;
  tACT=tSNC1;
  // put your setup code here, to run once:
  Serial.begin(57600);
  while ( !Serial ) ;
  
  pinMode(snc1_c_p,OUTPUT);
  pinMode(snc1_c_n,OUTPUT);
  digitalWrite(snc1_c_n,!digitalRead(snc1_c_p));

  pinMode(snc2_c_p,OUTPUT);
  pinMode(snc2_c_n,OUTPUT);
  digitalWrite(snc2_c_n,!digitalRead(snc2_c_p));

  pinMode(snc3_c_p,OUTPUT);
  pinMode(snc3_c_n,OUTPUT);
  digitalWrite(snc3_c_n,!digitalRead(snc3_c_p));

  pinMode(act_c,OUTPUT);

  pinMode(swaddr_0,OUTPUT);
  pinMode(swaddr_1,OUTPUT);
  pinMode(swaddr_2,OUTPUT);
  pinMode(swaddr_3,OUTPUT);
}

bool snc1_status = false;
float snc1_cycle = 5000;

bool snc2_status = false;
float snc2_cycle= 5000;

bool snc3_status = false;
int snc3_cycle = 5000;

bool act_status= false;
float act_cycle= 50000;


void loop() {
  
   gen();
   if (Serial.available()){
      Serial.println(">>>");
      String s = Serial.readStringUntil('\n');
      Serial.println(">>>" +s);
      String eintity;
      String function;
      String Value;
      int i=0;
      int point=0;
      while(s.charAt(i)!=' ' && i<s.length())
         i++;
   
      eintity=s.substring(0,i);
      i++;
      point =i;
       
      while(s.charAt(i)!=' ' && i<s.length())
         i++; 
      function=s.substring(point,i);
      i++;
      point =i;   

      while(s.charAt(i)!=' ' && i<s.length())
         i++; 
      Value=s.substring(point,i);

    

      if (eintity == "snc1"){
          if( function == "power")
          {
               if ( Value == "on"){
                      snc1_status=true;
                      Serial.println("snc1 is on");
               }
               else
                if ( Value == "off"){
                       snc1_status=false;
                       Serial.println("snc1 is off");
                }
          } else if( function == "phase")
          {
               if ( Value == "on"){
                       set_phase(1,true);
                       Serial.println("snc1_p = snc1_n");
               }
               else
                if ( Value == "off"){
                       set_phase(1,false);
                       Serial.println("snc1_p = !snc1_n");
                }
           } else if( function == "cycle"){
                 snc1_cycle =Value.toInt();
                  Serial.println("snc1 cycle set to" + Value);

           }
       } 

        else
        if (eintity == "snc2"){
            if( function == "power")
             {
                if ( Value == "on"){
                        snc2_status=true;
                        Serial.println("snc2 is on");
                 }
                 else
                    if ( Value == "off"){
                       snc2_status=false;
                       Serial.println("snc2 is off");
                 }
              } else if( function == "phase")
                {
                    if ( Value == "on"){
                       set_phase(2,true);
                       Serial.println("snc2_p = snc2_n");
                 }
                   else
                      if ( Value == "off"){
                           set_phase(2,false);
                            Serial.println("snc2_p = !snc2_n");
                 }
              } else if( function == "cycle")
                {
                  snc2_cycle =Value.toInt();
                  Serial.println("snc2 cycle set to" + Value);
                }
           }
            else
            if (eintity == "snc3"){
                   if( function == "power")
                       {  
                           if ( Value == "on")
                           {
                                snc3_status=true;
                                Serial.println("snc3 is on");
                           }
                          else
                           if ( Value == "off")
                          {
                                snc3_status=false;
                                Serial.println("snc3 is off");
                           }
                    } else if( function == "phase")
                         {
                              if ( Value == "on")
                               {
                                 set_phase(3,true);
                                 Serial.println("snc3_p = snc3_n");
                        }
                       else
                          if ( Value == "off")
                              {
                                 set_phase(3,false);
                                  Serial.println("snc3_p = !snc3_n");
                              }
                       } else if( function == "cycle"){
                                   snc3_cycle =Value.toInt();
                                   Serial.println("snc3 cycle set to" + Value);
                        }
                } else
                      if (eintity == "act"){
                          if( function == "power")
                           {
                                if ( Value == "on"){
                                   //  act_status=true;
                                     digitalWrite(act_c,HIGH);                    
                                     Serial.println("actuator is on");
                                 }
                       else
                              if ( Value == "off"){
                              //  act_status=false;
                               digitalWrite(act_c,LOW);   
                              Serial.println("actuator is off");
                              }
          
                       } /*else if( function == "cycle")
                             {
                                 act_cycle =Value.toInt();
                                  Serial.println("actuator cycle set to" + Value);
                              }
                          */
               } else
                         if (eintity == "band"){
                                if( function == "select")
                                  {
                                     setAddr(Value.toInt());                                  
                                     Serial.println("switch address set to" + Value);
                                    }
             }else
                         if (eintity == "Vdigital"){
                                if( function == "read")
                                  {
                                     int sensorValue = analogRead(VdigitalSense);   
                                     for (int i=1;i<10;i++){
                                         sensorValue += analogRead(VdigitalSense);   
                                         delay(3);
                                     }                 
                                     Serial.println(sensorValue*5.0/(10240));
                                    }
             }
    

       }

}

void set_phase (int snc, bool phase){

  switch (snc){
    case 1:
          if (phase)
                digitalWrite(snc1_c_n,digitalRead(snc1_c_p));            
           else 
                digitalWrite(snc1_c_n,!digitalRead(snc1_c_p));           
     break;
     case 2:
            if (phase)
                 digitalWrite(snc2_c_n,digitalRead(snc2_c_p));           
             else
                 digitalWrite(snc2_c_n,!digitalRead(snc2_c_p));
     break;
     case 3:
            if (phase) 
               digitalWrite(snc3_c_n,digitalRead(snc3_c_p));
            else
               digitalWrite(snc3_c_n,!digitalRead(snc3_c_p));
     break;
     default:
      Serial.println(" wrong channel enterd");
       break;
  }

    
}

void gen(){    
  
//  Serial.println(snc1_cycle/2);
   if (snc1_status && micros()-tSNC1>=snc1_cycle/2){
        digitalWrite(snc1_c_p,!digitalRead(snc1_c_p));
        digitalWrite(snc1_c_n,!digitalRead(snc1_c_n));
        tSNC1=micros();
       }

    if (snc2_status && micros()-tSNC2>= snc2_cycle/2){
        digitalWrite(snc2_c_p,!digitalRead(snc2_c_p));
        digitalWrite(snc2_c_n,!digitalRead(snc2_c_n));
        tSNC2=micros();
      }

      if (snc3_status && micros()-tSNC3>=snc3_cycle/2){
        digitalWrite(snc3_c_p,!digitalRead(snc3_c_p));
        digitalWrite(snc3_c_n,!digitalRead(snc3_c_n));
        tSNC3=micros();
        }
    
       if (act_status && micros()-tACT>=act_cycle/2){
        digitalWrite(act_c,!digitalRead(act_c));
        tACT=micros();
       }
  }
  
 void setAddr(byte addr){
    digitalWrite(swaddr_0,(addr & 0x01));
    digitalWrite(swaddr_1,(addr & 0x02)>>1);
    digitalWrite(swaddr_2,(addr & 0x04)>>2);
    digitalWrite(swaddr_3,(addr & 0x08)>>3);
 }
  
