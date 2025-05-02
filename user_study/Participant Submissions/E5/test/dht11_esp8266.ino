#include <ESP8266WiFi.h>
#include <ESP8266HTTPClient.h>
#include <WiFiClient.h>
#include <ArduinoJson.h>
#include <DHT.h>
#include <Wire.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>

//======================== 配置区域 ========================
// WiFi设置
const char* ssid = "你的WiFi名称";        // 替换为你的WiFi名称
const char* password = "你的WiFi密码";    // 替换为你的WiFi密码

// Home Assistant设置
const char* ha_host = "192.168.1.xxx";   // 替换为Home Assistant的IP地址
const int ha_port = 8123;                // Home Assistant默认端口
const char* ha_token = "长期访问令牌";    // 替换为你在Home Assistant创建的长期访问令牌

// 传感器设置
#define DHTPIN D4       // DHT11连接到D4引脚(GPIO2)
#define DHTTYPE DHT11   // 传感器类型为DHT11
DHT dht(DHTPIN, DHTTYPE);

// OLED显示屏设置
#define SCREEN_WIDTH 128
#define SCREEN_HEIGHT 64
#define OLED_RESET -1   // 共享Arduino的复位引脚
Adafruit_SSD1306 display(SCREEN_WIDTH, SCREEN_HEIGHT, &Wire, OLED_RESET);

// 其他设置
const long interval = 60000;  // 数据发送间隔(毫秒)，此处设为1分钟
unsigned long previousMillis = 0;

// 传感器数据
float temperature = 0;
float humidity = 0;
//==========================================================

void setup() {
  // 初始化串口
  Serial.begin(115200);
  Serial.println("ESP8266 DHT11传感器连接Home Assistant");
  
  // 初始化I2C总线
  Wire.begin(D2, D1);  // SDA=D2(GPIO4), SCL=D1(GPIO5)
  
  // 初始化OLED显示屏
  if(!display.begin(SSD1306_SWITCHCAPVCC, 0x3C)) {
    Serial.println(F("SSD1306初始化失败"));
    for(;;); // 无限循环
  }
  
  // 显示启动信息
  display.clearDisplay();
  display.setTextSize(1);
  display.setTextColor(WHITE);
  display.setCursor(0, 0);
  display.println("温湿度监测系统");
  display.println("正在连接WiFi...");
  display.display();
  
  // 初始化DHT传感器
  dht.begin();
  
  // 连接WiFi
  WiFi.begin(ssid, password);
  Serial.print("正在连接WiFi");
  
  // 等待WiFi连接
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  
  // 连接成功
  Serial.println();
  Serial.println("WiFi已连接");
  Serial.print("IP地址: ");
  Serial.println(WiFi.localIP());
  
  // 显示连接成功信息
  display.clearDisplay();
  display.setCursor(0, 0);
  display.println("WiFi已连接!");
  display.print("IP: ");
  display.println(WiFi.localIP().toString());
  display.println("准备发送数据...");
  display.display();
  delay(2000);
}

void loop() {
  unsigned long currentMillis = millis();
  
  // 读取传感器数据
  float newT = dht.readTemperature();
  float newH = dht.readHumidity();
  
  // 检查读取的数据是否有效
  if (!isnan(newT) && !isnan(newH)) {
    temperature = newT;
    humidity = newH;
    
    // 更新OLED显示
    updateDisplay();
    
    // 检查是否到达发送间隔
    if (currentMillis - previousMillis >= interval) {
      previousMillis = currentMillis;
      
      // 发送数据到Home Assistant
      if (WiFi.status() == WL_CONNECTED) {
        sendDataToHomeAssistant();
      } else {
        Serial.println("WiFi连接已断开，尝试重新连接");
        WiFi.begin(ssid, password);
      }
    }
  } else {
    Serial.println("读取DHT11传感器失败!");
    display.clearDisplay();
    display.setCursor(0, 0);
    display.println("传感器读取失败!");
    display.println("请检查连接");
    display.display();
  }
  
  delay(2000); // 2秒读取一次传感器，避免过于频繁
}

// 更新显示屏内容
void updateDisplay() {
  display.clearDisplay();
  
  // 显示温度
  display.setCursor(0, 0);
  display.print("温度: ");
  display.print(temperature);
  display.println(" C");
  
  // 显示湿度
  display.setCursor(0, 16);
  display.print("湿度: ");
  display.print(humidity);
  display.println(" %");
  
  // 显示WiFi信号强度
  display.setCursor(0, 32);
  display.print("WiFi: ");
  display.print(WiFi.RSSI());
  display.println(" dBm");
  
  // 显示上次发送时间
  display.setCursor(0, 48);
  display.print("上次发送: ");
  display.print(previousMillis / 60000);
  display.println("分钟前");
  
  display.display();
}

// 发送数据到Home Assistant
void sendDataToHomeAssistant() {
  WiFiClient client;
  HTTPClient http;
  
  // 准备发送温度数据
  Serial.println("发送温度数据到Home Assistant...");
  String tempUrl = "http://" + String(ha_host) + ":" + String(ha_port) + "/api/states/sensor.esp8266_temperature";
  
  http.begin(client, tempUrl);
  http.addHeader("Content-Type", "application/json");
  http.addHeader("Authorization", "Bearer " + String(ha_token));
  
  // 创建JSON数据
  StaticJsonDocument<200> tempDoc;
  tempDoc["state"] = temperature;
  tempDoc["attributes"]["unit_of_measurement"] = "°C";
  tempDoc["attributes"]["device_class"] = "temperature";
  tempDoc["attributes"]["friendly_name"] = "ESP8266温度";
  
  String tempJsonStr;
  serializeJson(tempDoc, tempJsonStr);
  
  // 发送POST请求
  int tempHttpCode = http.POST(tempJsonStr);
  
  if (tempHttpCode > 0) {
    Serial.printf("温度数据发送成功，状态码: %d\n", tempHttpCode);
  } else {
    Serial.printf("温度数据发送失败，错误: %s\n", http.errorToString(tempHttpCode).c_str());
  }
  
  http.end();
  
  // 准备发送湿度数据
  Serial.println("发送湿度数据到Home Assistant...");
  String humUrl = "http://" + String(ha_host) + ":" + String(ha_port) + "/api/states/sensor.esp8266_humidity";
  
  http.begin(client, humUrl);
  http.addHeader("Content-Type", "application/json");
  http.addHeader("Authorization", "Bearer " + String(ha_token));
  
  // 创建JSON数据
  StaticJsonDocument<200> humDoc;
  humDoc["state"] = humidity;
  humDoc["attributes"]["unit_of_measurement"] = "%";
  humDoc["attributes"]["device_class"] = "humidity";
  humDoc["attributes"]["friendly_name"] = "ESP8266湿度";
  
  String humJsonStr;
  serializeJson(humDoc, humJsonStr);
  
  // 发送POST请求
  int humHttpCode = http.POST(humJsonStr);
  
  if (humHttpCode > 0) {
    Serial.printf("湿度数据发送成功，状态码: %d\n", humHttpCode);
  } else {
    Serial.printf("湿度数据发送失败，错误: %s\n", http.errorToString(humHttpCode).c_str());
  }
  
  http.end();
} 