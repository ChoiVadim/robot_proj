//#include <Adafruit_GFX.h>
#include <Adafruit_ST7735.h>
//#include <SPI.h>

#define TFT_CS 10
#define TFT_RST 9
#define TFT_DC 8

Adafruit_ST7735 tft = Adafruit_ST7735(TFT_CS, TFT_DC, TFT_RST);
unsigned long previousMillis = 0;
const long interval = 1000; // Интервал отправки сообщения (1 секунда)

void setup()
{
  Serial.begin(9600);

  tft.initR(INITR_BLACKTAB);
  tft.fillScreen(ST7735_BLACK);

  tft.setTextColor(ST7735_WHITE);
  tft.setTextSize(5);
}

void loop()
{
  FaceMode();
  unsigned long currentMillis = millis();

  if (currentMillis - previousMillis >= interval)
  {
    previousMillis = currentMillis;
  }

  if (Serial.available() > 0)
  {
    String command = Serial.readStringUntil('\n');
    processCommand(command);
  }
}

void FaceMode()
{
  tft.fillCircle(32, 64, 25, ST77XX_WHITE);
  tft.fillCircle(96, 64, 25, ST77XX_WHITE);
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
