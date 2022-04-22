
#include <MPU6050_tockn.h>
#include <Wire.h>
#include "Adafruit_VL53L0X.h"
#include "MedianFilter.h"

MPU6050 mpu6050(Wire);
Adafruit_VL53L0X lox = Adafruit_VL53L0X();

MedianFilter filter(10, 0);

long timer = millis();

long prevTimeSinceStart = millis();
float prevYaw = 0;
float prevYawVel = 0;
float prevYawAcc = 0;
float prevPitch = 0;
float prevPitchVel = 0;
float prevPitchAcc = 0;
int prevSurge = 0;
float prevSurgeVel = 0;
float prevSurgeAcc = 0;

int surgeOffset = 40; // Distance from entrance of box to sensor position


void setup() {
  Serial.begin(115200);
  Wire.begin();
  mpu6050.begin();
  //mpu6050.calcGyroOffsets(true); // Last Calibrated March 30th, 2022
  mpu6050.setGyroOffsets(0.23, 1.45, 0.12);

  if (!lox.begin()) {
    Serial.println(F("Failed to boot VL53L0X"));
    while (1);
  }
  Serial.println(F("VL53L0X API Simple Ranging example\n\n"));
}

void loop() {
  mpu6050.update();
  VL53L0X_RangingMeasurementData_t measure;
  lox.rangingTest(&measure, false); // pass in 'true' to get debug data printout!
  
  unsigned long currentMillis = millis();
  uint16_t txSize = 0;

  if (currentMillis - timer > 100) {
  
    unsigned long timeSinceStart = millis();
    float yaw = mpu6050.getAngleY();
    float yawVel = 0;
    float yawAcc = 0;
    float pitch = mpu6050.getAngleX();
    float pitchVel = 0;
    float pitchAcc = 0;
    int surge = 0;
    float surgeVel = 0;
    float surgeAcc = 0;
    
    // Set Surge from filter
    if (measure.RangeStatus != 4) { // phase failures have incorrect data
      filter.in(measure.RangeMilliMeter+surgeOffset);
    } else {
      Serial.println("Measurement Error");
      filter.in(prevSurge);
    }
    surge = int(filter.out());
    
    // Velocities
    if (prevYaw != 0) {
      yawVel = (yaw - prevYaw) * 1000.00 / (timeSinceStart - prevTimeSinceStart); // deg/s
    }
    if (prevPitch != 0) {
      pitchVel = (pitch - prevPitch) * 1000.00 / (timeSinceStart - prevTimeSinceStart); // deg/s
    }
    if (prevSurge != 0) {
      surgeVel = (surge - prevSurge) * 1000.00 / (timeSinceStart - prevTimeSinceStart); // mm/s
    }

    // Accelerations
    if (prevYawVel != 0) {
      yawAcc = (yawVel - prevYawVel) * 1000.00 / (timeSinceStart - prevTimeSinceStart); // deg/s^2
    }
    if (prevPitchVel != 0) {
      pitchAcc = (pitchVel - prevPitchVel) * 1000.00 / (timeSinceStart - prevTimeSinceStart); // deg/s^2
    }
    if (prevSurgeVel != 0) {
      surgeAcc = (surgeVel - prevSurgeVel) * 1000.00 / (timeSinceStart - prevTimeSinceStart); // mm/s^2
    }

    String timeSinceStartStr = String(timeSinceStart);
    String yawStr = String(yaw);
    String yawVelStr = String(yawVel);
    String yawAccStr = String(yawAcc);
    String pitchStr = String(pitch);
    String pitchVelStr = String(pitchVel);
    String pitchAccStr = String(pitchAcc);
    String surgeStr = String(surge);
    String surgeVelStr = String(surgeVel);
    String surgeAccStr = String(surgeAcc);
    
    Serial.println("DATA:"+timeSinceStartStr+":"+yawStr+":"+yawVelStr+":"+yawAccStr+":"+pitchStr+":"+pitchVelStr+":"+pitchAccStr+":"+surgeStr+":"+surgeVelStr+":"+surgeAccStr);

    // Update the previous
    prevTimeSinceStart = timeSinceStart;
    prevYaw = yaw;
    prevYawVel = yawVel;
    prevYawAcc = yawAcc;
    prevPitch = pitch;
    prevPitchVel = pitchVel;
    prevPitchAcc = pitchAcc;
    prevSurge = surge;
    prevSurgeVel = surgeVel;
    prevSurgeAcc = surgeAcc;
    
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
