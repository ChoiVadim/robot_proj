// Пины для управления моторами
const int motor1Pin1 = 6;
const int motor1Pin2 = 7;
const int motor2Pin1 = 8;
const int motor2Pin2 = 9;

void setup() {
    // Устанавливаем пины как выходы
    pinMode(motor1Pin1, OUTPUT);
    pinMode(motor1Pin2, OUTPUT);
    pinMode(motor2Pin1, OUTPUT);
    pinMode(motor2Pin2, OUTPUT);
    
    Serial.begin(9600);
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
        String direction = command.substring(0, commaIndex);
        int duration = command.substring(commaIndex + 1).toInt();

        if (direction == "forward") {
            moveForward(duration);
        } else if (direction == "backward") {
            moveBackward(duration);
        } else if (direction == "left") {
            turnLeft(duration);
        } else if (direction == "right") {
            turnRight(duration);
        } else {
            stopMotors();
        }
    }
}

void moveForward(int duration) {
    digitalWrite(motor1Pin1, HIGH);
    digitalWrite(motor1Pin2, LOW);
    digitalWrite(motor2Pin1, HIGH);
    digitalWrite(motor2Pin2, LOW);
    delay(duration * 1000);
    stopMotors();
}

void moveBackward(int duration) {
    digitalWrite(motor1Pin1, LOW);
    digitalWrite(motor1Pin2, HIGH);
    digitalWrite(motor2Pin1, LOW);
    digitalWrite(motor2Pin2, HIGH);
    delay(duration * 1000);
    stopMotors();
}

void turnLeft(int duration) {
    digitalWrite(motor1Pin1, LOW);
    digitalWrite(motor1Pin2, HIGH);
    digitalWrite(motor2Pin1, HIGH);
    digitalWrite(motor2Pin2, LOW);
    delay(duration * 1000);
    stopMotors();
}

void turnRight(int duration) {
    digitalWrite(motor1Pin1, HIGH);
    digitalWrite(motor1Pin2, LOW);
    digitalWrite(motor2Pin1, LOW);
    digitalWrite(motor2Pin2, HIGH);
    delay(duration * 1000);
    stopMotors();
}

void stopMotors() {
    digitalWrite(motor1Pin1, LOW);
    digitalWrite(motor1Pin2, LOW);
    digitalWrite(motor2Pin1, LOW);
    digitalWrite(motor2Pin2, LOW);
}
