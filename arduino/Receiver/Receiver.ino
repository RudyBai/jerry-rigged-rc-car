#include <SPI.h>
#include <nRF24L01.h>
#include <RF24.h>

int pwm_a = 3;  //PWM control for motor outputs 1 and 2
int pwm_b = 9;  //PWM control for motor outputs 3 and 4
int dir_a = 2;  //direction control for motor outputs 1 and 2
int dir_b = 8;  //direction control for motor outputs 3 and 4

RF24 radio(6, 7); // CE, CSN

const byte address[6] = "00001";
char value[9];
char steering_chars[4];
char throttle_chars[4];
short throttle = 0;
short steering = 0;

void setup() {

  pinMode(pwm_a, OUTPUT);
  pinMode(pwm_b, OUTPUT);
  pinMode(dir_a, OUTPUT);
  pinMode(dir_b, OUTPUT);

  Serial.begin(9600);
  radio.begin();
  radio.openReadingPipe(0, address);
  radio.setPALevel(RF24_PA_MIN);
  radio.startListening();
}

void loop() {
  if (radio.available()) {
    radio.read(&value, 9);

    if (!(value[0] == 'R' or value[0] == 'L')) {
      return;
    }

    // Steering direction
    if (value[0] == 'R') {
      digitalWrite(dir_b, HIGH);
    } else {
      digitalWrite(dir_b, LOW);
    }

    // Steering
    memcpy(steering_chars, &value[1], 3 * sizeof(char));
    steering = atoi(steering_chars);
    if (steering < 32) analogWrite(pwm_b, 0);
    else analogWrite(pwm_b, steering);

    // Throttle direction
    if (value[4] == 'F') {
      digitalWrite(dir_a, LOW);
    } else {
      digitalWrite(dir_a, HIGH);
    }

    // Throttle
    memcpy(throttle_chars, &value[5], 3 * sizeof(char));
    throttle = atoi(throttle_chars);
    analogWrite(pwm_a, throttle);
  }
}
