#include <Adafruit_ST7735.h>
#include <Adafruit_GFX.h>

#define TFT_CS 10
#define TFT_RST 9
#define TFT_DC 8

Adafruit_ST7735 tft = Adafruit_ST7735(TFT_CS, TFT_DC, TFT_RST);
unsigned long previousMillis = 0;
unsigned long blinkInterval = 0; // Variable to store the random interval
const long minInterval = 1000; // Minimum interval for blinking
const long maxInterval = 5000; // Maximum interval for blinking
int faceState = 0;

void setup()
{
  Serial.begin(9600);

  tft.initR(INITR_BLACKTAB);
  tft.fillScreen(ST7735_BLACK);

  tft.setTextColor(ST7735_WHITE);
  tft.setTextSize(5);

  randomSeed(analogRead(0)); // Initialize random number generator
  blinkInterval = random(minInterval, maxInterval); // Generate the initial random interval
}

void loop()
{
  unsigned long currentMillis = millis();

  if (currentMillis - previousMillis >= blinkInterval)
  {
    previousMillis = currentMillis;
    faceState = 3; // Set faceState to blinking
    FaceMode();
    delay(20); // Duration of the blink
    faceState = 0; // Reset faceState to neutral
    FaceMode();
    blinkInterval = random(minInterval, maxInterval); // Generate a new random interval
  }
  else
  {
    // FaceMode();
    // faceState = (faceState + 1) % 3; // Cycle through 0, 1, 2 (excluding blinking)
  }

  if (Serial.available() > 0)
  {
    String command = Serial.readStringUntil('\n');
    processCommand(command);
  }
}

void FaceMode()
{
  tft.fillScreen(ST7735_BLACK);

  if (faceState != 3) {
    tft.fillCircle(32, 64, 25, ST77XX_WHITE); // Left eye
    tft.fillCircle(96, 64, 25, ST77XX_WHITE); // Right eye
  } else {
    tft.fillRect(7, 59, 50, 10, ST7735_WHITE); // Closed left eye
    tft.fillRect(71, 59, 50, 10, ST7735_WHITE); // Closed right eye
  }

  switch (faceState)
  {
    case 0:
      drawNeutralFace();
      break;
    case 1:
      drawHappyFace();
      break;
    case 2:
      drawSadFace();
      break;
    case 3:
      drawBlinkingFace();
      break;
  }
}

void drawNeutralFace()
{
  tft.fillCircle(32, 64, 10, ST7735_BLACK); // Left pupil
  tft.fillCircle(96, 64, 10, ST7735_BLACK); // Right pupil
  tft.drawLine(32, 110, 96, 110, ST7735_WHITE); // Neutral mouth
}

void drawHappyFace()
{
  tft.fillCircle(32, 64, 10, ST7735_BLACK); // Left pupil
  tft.fillCircle(96, 64, 10, ST7735_BLACK); // Right pupil
  drawArc(64, 110, 30, 180, 360, ST7735_WHITE); // Happy mouth
}

void drawSadFace()
{
  tft.fillCircle(32, 64, 10, ST7735_BLACK); // Left pupil
  tft.fillCircle(96, 64, 10, ST7735_BLACK); // Right pupil
  drawArc(64, 130, 30, 0, 180, ST7735_WHITE); // Sad mouth
}

void drawBlinkingFace()
{
  // Eyes are closed, so no pupils
  tft.drawLine(32, 110, 96, 110, ST7735_WHITE); // Neutral mouth
}

void drawArc(int16_t x, int16_t y, int16_t radius, int16_t startAngle, int16_t endAngle, uint16_t color)
{
  for (int i = startAngle; i < endAngle; i++)
  {
    float rad = i * DEG_TO_RAD;
    int16_t x0 = x + radius * cos(rad);
    int16_t y0 = y + radius * sin(rad);
    int16_t x1 = x + radius * cos(rad + DEG_TO_RAD);
    int16_t y1 = y + radius * sin(rad + DEG_TO_RAD);
    tft.drawLine(x0, y0, x1, y1, color);
  }
}

void TimerMode(int duration)
{
  int minutes = 0;
  int seconds = duration;

  while (minutes >= 0)
  {
    while (seconds >= 0)
    {
      tft.fillScreen(ST7735_BLACK);
      tft.setCursor(0, 0);
      tft.setTextSize(5);
      tft.print(minutes);
      tft.println("Min\n");
      tft.setTextSize(3);
      tft.print(seconds);
      tft.print("Sec");
      delay(1000);
      seconds--;
    }
    minutes--;
    seconds = 59;
    Serial.println("Done");
  }

  tft.fillScreen(ST7735_BLACK);
  tft.setCursor(0, 0);
  tft.println("Time's up!");
  delay(2000);
  tft.fillScreen(ST7735_BLACK);
  FaceMode();
}

void processCommand(String command)
{
  int commaIndex = command.indexOf(',');
  if (commaIndex > 0)
  {
    String ex = command.substring(0, commaIndex);
    int duration = command.substring(commaIndex + 1).toInt();

    if (ex == "face")
    {
      FaceMode();
    }
    else if (ex == "timer")
    {
      TimerMode(duration);
    }
  }
}
