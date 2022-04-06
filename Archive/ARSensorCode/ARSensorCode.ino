
#include <MPU6050_tockn.h>
#include <Wire.h>
#include "SerialTransfer.h"

MPU6050 mpu6050(Wire);
SerialTransfer computer;
long timer = 0;
unsigned long millisAtStart = millis();

struct DATA {
  float millisSince = 0;
  float yaw;
  float pitch; 
} data; // 12 bytes

void setup() {
  Serial.begin(115200);
  Wire.begin();
  mpu6050.begin();
  mpu6050.setGyroOffsets(0.25, 1.50, 0.35);
  computer.begin(Serial);
}

void loop() {
  mpu6050.update();
  unsigned long currentMillis = millis();
  uint16_t txSize = 0;

  if (millis() - timer > 100) {
    
    data.millisSince = currentMillis - millisAtStart;
    data.yaw = mpu6050.getAngleX();
    data.pitch = mpu6050.getAngleY();

    txSize = computer.txObj(data, txSize);
    computer.sendData(txSize);
    timer = millis();    
  }
}



//Serial.println("=======================================================");
//Serial.print("temp : ");Serial.println(mpu6050.getTemp());
//Serial.print("accX : ");Serial.print(mpu6050.getAccX());
//Serial.print("\taccY : ");Serial.print(mpu6050.getAccY());
//Serial.print("\taccZ : ");Serial.println(mpu6050.getAccZ());

//Serial.print("gyroX : ");Serial.print(mpu6050.getGyroX());
//Serial.print("\tgyroY : ");Serial.print(mpu6050.getGyroY());
//Serial.print("\tgyroZ : ");Serial.println(mpu6050.getGyroZ());

//Serial.print("accAngleX : ");Serial.print(mpu6050.getAccAngleX());
//Serial.print("\taccAngleY : ");Serial.println(mpu6050.getAccAngleY());

///Serial.print("gyroAngleX : ");Serial.print(mpu6050.getGyroAngleX());
///Serial.print("\tgyroAngleY : ");Serial.print(mpu6050.getGyroAngleY());
///Serial.print("\tgyroAngleZ : ");Serial.println(mpu6050.getGyroAngleZ());
//Serial.print("angleX : ");Serial.print(mpu6050.getAngleX());
//Serial.print("\t angleY : ");Serial.print(mpu6050.getAngleY());
//Serial.print("\t angleZ : ");Serial.println(mpu6050.getAngleZ());
///Serial.println("=======================================================\n");
