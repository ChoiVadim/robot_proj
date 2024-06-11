int IN1 = 6;
int IN2 = 7;
int IN3 = 8;
int IN4 = 9;

void setup() {
  Serial.begin(9600);
  pinMode(IN1, OUTPUT);
  pinMode(IN2, OUTPUT);
  pinMode(IN3, OUTPUT);
  pinMode(IN4, OUTPUT);

  //moveForward(1);
}

void loop() {
    if (Serial.available() > 0) {
        String command = Serial.readStringUntil('\n');
        processCommand(command);
    }
}

void processCommand(String command) {
  int commaIndex = command.indexOf(',');
  if (commaIndex > 0) {
    String cmd = command.substring(0, commaIndex);
    int duration = command.substring(commaIndex + 1).toInt();

    if (cmd == "forward") {
      moveForward(duration);
    } else if (cmd == "backward") {
      moveBackward(duration);
    } else if (cmd == "left") {
      turnLeft(duration);
    } else if (cmd == "right") {
      turnRight(duration);
    } else if (cmd == "wakeup") {
      moveForward(duration);
      moveBackward(duration);
    }
  }
}


void moveForward(int duration){
  digitalWrite(IN2, LOW);
  digitalWrite(IN4, LOW);
  digitalWrite(IN1, HIGH);
  digitalWrite(IN3, HIGH);
  delay(duration*1000);
  stop();
}

void moveBackward(int duration){
  digitalWrite(IN1, LOW);
  digitalWrite(IN3, LOW);
  digitalWrite(IN2, HIGH);
  digitalWrite(IN4, HIGH);
  delay(duration*1000);
  stop();
}

void turnLeft(int duration) {
  digitalWrite(IN1, HIGH);
  digitalWrite(IN3, LOW);
  digitalWrite(IN2, LOW);
  digitalWrite(IN4, HIGH);
  delay(duration*1000);
  stop();
}

void turnRight(int duration) {
  digitalWrite(IN1, LOW);
  digitalWrite(IN3, HIGH);
  digitalWrite(IN2, HIGH);
  digitalWrite(IN4, LOW);
  delay(duration*1000);
  stop();
}

void stop(){
  digitalWrite(IN1, LOW);
  digitalWrite(IN2, LOW);
  digitalWrite(IN3, LOW);
  digitalWrite(IN4, LOW);
}