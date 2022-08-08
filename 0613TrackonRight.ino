/*************************************************************/
#include <Arduino.h>
#include <LiquidCrystal.h>//lcd
#include <SoftwareSerial.h>
#include <Servo.h>
#include <String.h>



Servo My_Servo; //用 Servo 关键字定义一个舵机 My_Servo
#define Servo_1 2 //定义舵机信号口对应的 arduino 引脚为 2

#define L1_DIR 4           //左电机的方向控制接口对应 arduino 引脚 4
#define L1_EN 7            //左电机的使能端控制接口对应 arduino 引脚 7
#define L1_STP 5           //左电机的脉冲信号接口对应 arduino 引脚 5

#define R1_DIR 16          //右电机的方向控制接口对应 arduino 引脚 49
#define R1_EN 18          //右电机的使能端控制接口对应 arduino 引脚 53
#define R1_STP 19          //右电机的脉冲信号接口对应 arduino 引脚 51

#define L_infraredray 48   //定义左红外传感器接口引脚 A6
#define R_infraredray 52  //定义右红外传感器接口引脚 A10

#define RaspberryPi 22     //定义树莓派GPIO接口引脚
#define raspberrypi 24     //定义树莓派GPIO接口引脚
#define RaspberryPiback 26     //定义树莓派GPIO接口引脚
#define raspberrypiback 28 //定义树莓派GPIO接口引脚

#define STOP 22     //定义引脚 22
/**************************参数定义***********************************/

volatile int b[2]; //循迹储存数组
int number=0;
/*************************************************************/

void Track_PWM(int Pin, int delay_us) {
digitalWrite(Pin, HIGH);
delayMicroseconds(delay_us);
digitalWrite(Pin, LOW);
delayMicroseconds(delay_us);
}

void BreathLED(int LED) {
  for(int led=1;led<=100;led++){
    float zyl=led/10;
    digitalWrite(LED,HIGH);
    delay(zyl);
    digitalWrite(LED,LOW);
    delay(10-zyl);
  }
    for(int ledd=1;ledd<=100;ledd++){
    float sxy=ledd/10;
    digitalWrite(LED,LOW);
    delay(sxy);
    digitalWrite(LED,HIGH);
    delay(10-sxy);
  }

}
/*************************************************************/

void Track_Setup(){
pinMode(L1_DIR, OUTPUT);
pinMode(L1_EN, OUTPUT);
pinMode(L1_STP, OUTPUT);
pinMode(R1_DIR, OUTPUT);
pinMode(R1_EN, OUTPUT);
pinMode(R1_STP, OUTPUT);
digitalWrite(L1_EN, HIGH);         //L1_EN 置高，表明之后可以控制左电机
digitalWrite(R1_EN, HIGH);         //R1_EN 置高，表明之后可以控制右电机
}

void Stop()
{
  digitalWrite(L1_EN,LOW);         //L1_EN 置低，表明之后无法控制左电机
  digitalWrite(R1_EN,LOW);         //R1_EN 置低，表明之后无法控制右电机

  }

void GoStraight(int Step)
{
  digitalWrite(L1_EN, HIGH);
  digitalWrite(L1_DIR, LOW);

  digitalWrite(R1_EN, HIGH);
  digitalWrite(R1_DIR, HIGH);
  
  for (int x = 0; x < Step; x++)
  {
      Track_PWM(L1_STP, 80); 
      Track_PWM(R1_STP, 80);
  }
}

void TrackStraightRight(int Step){
  digitalWrite(L1_EN, HIGH);
  digitalWrite(L1_DIR, LOW);

  digitalWrite(R1_EN, HIGH);
  digitalWrite(R1_DIR, HIGH);

  for (int xlyy = 0; xlyy < Step; xlyy++)
  {
    digitalWrite(R1_STP, HIGH);
    digitalWrite(L1_STP, HIGH);
    delayMicroseconds(200);
    digitalWrite(L1_STP, LOW);
    delayMicroseconds(200);
    digitalWrite(L1_STP, HIGH);
    digitalWrite(R1_STP, LOW);
    delayMicroseconds(200);
    digitalWrite(L1_STP, LOW);
    delayMicroseconds(200);
  }
  
}

void TrackStraightLeft(int Step)
{
  digitalWrite(L1_EN, HIGH);
  digitalWrite(L1_DIR, LOW);

  digitalWrite(R1_EN, HIGH);
  digitalWrite(R1_DIR, HIGH);
  for (int xLYY = 0; xLYY < Step; xLYY++)
  {
    digitalWrite(L1_STP, HIGH);
    digitalWrite(R1_STP, HIGH);
    delayMicroseconds(200);
    digitalWrite(R1_STP, LOW);
    delayMicroseconds(200);
    digitalWrite(R1_STP, HIGH);
    digitalWrite(L1_STP, LOW);
    delayMicroseconds(200);
    digitalWrite(R1_STP, LOW);
    delayMicroseconds(200);
  }
}


void TrackStraight(int step){
  int lyy;
  for(lyy=0;lyy<step;lyy++){
    b[0]=digitalRead(L_infraredray);
    b[1]=digitalRead(R_infraredray);
    //该版本红外高电平输出0，低电平输出1
    if(b[0]==1&& b[1]==1)            //两个红外都不亮，直走
      {GoStraight(20);}
    else if(b[0]==1 && b[1]==0)   //车头向右前方，应该往左边调整，车向左转
      {TrackStraightLeft(1);
      }
    else if(b[0] ==0 && b[1]==1)   //车头向左前方，应该往右边调整
       {TrackStraightRight(1);}
    else
       {GoStraight(20);}    //  左0右1向右走   左1右零直走  其它向右走
  }
}


/*************************************************************/

void Servo_Setup(){
  pinMode(Servo_1, OUTPUT);
  My_Servo.attach(Servo_1);
  for(int servoi=122;servoi>=68;servoi=servoi-9){
    My_Servo.write(servoi);
    delay(20);
  }
  delay(200);
  My_Servo.detach();
}

void Servo_Setupfinal() {
  pinMode(Servo_1, OUTPUT);           //设定 Servo_1 引脚为输出模式，以控制舵机
  My_Servo.attach(Servo_1);           //将舵机引脚和我们定义的舵机 attach 起来
  My_Servo.write(150);                 //写入舵机角度，让舵机在初始状态固定在 20°（根据实际情况写入角度）
  delay(500);                         //延迟一段时间，给舵机足够的转动时间到预设角度
  My_Servo.detach();                  //用完了将引脚和我们定义的舵机 detach，否则可能有 bug
}

void sensorsetup(){
  pinMode(RaspberryPi,OUTPUT);
  pinMode(raspberrypi,OUTPUT);
  pinMode(RaspberryPiback,INPUT);
  pinMode(raspberrypiback,INPUT);
//  pinMode(L_laser,INPUT);
//  pinMode(R_laser,INPUT);
  pinMode(L_infraredray,INPUT);
  pinMode(R_infraredray,INPUT);
}
/**************************************************************/

void setup() {
    sensorsetup();
    Track_Setup();  
    Servo_Setup();
    digitalWrite(3,HIGH);
}       //void setup 结束大括号

void loop() {
  TrackStraight(1);
      if(digitalRead(raspberrypiback)==1&&digitalRead(RaspberryPiback)==0){
        number++;
        delay(1000);
        while(1){
          digitalWrite(raspberrypi,LOW);
          if(digitalRead(raspberrypiback)==0&&digitalRead(RaspberryPiback)==1){
            break;
          }
        }     
      }
      
//      for(int i=0;i<3000;i++){
//         digitalWrite(L1_DIR, LOW); 
//         digitalWrite(R1_DIR, HIGH);
//         Track_PWM(L1_STP, 80); 
//         Track_PWM(R1_STP, 80);
//      }  
    
 
//    }
  
  if(number==12){
    for(int j=-3000;j<3000;j++){
         digitalWrite(L1_DIR, LOW); 
         digitalWrite(R1_DIR, HIGH);
         Track_PWM(L1_STP, 80); 
         Track_PWM(R1_STP, 80);
         }
      BreathLED(3);
      Servo_Setupfinal();

    while(1){
         Stop();
         digitalWrite(Stop,LOW);
    }
  }
}        // loop 结束大括号
