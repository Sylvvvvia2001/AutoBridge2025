# ESP8266 温湿度监测系统 + Home Assistant 集成

本项目通过ESP8266将DHT11温湿度传感器数据发送到Home Assistant平台，并通过OLED显示屏实时显示数据。

## 硬件准备

- NodeMCU ESP8266开发板
- DHT11温湿度传感器
- 0.96英寸OLED显示屏 (I2C接口，SSD1306芯片)
- 连接线
- Micro USB数据线

## 硬件连接

1. **DHT11连接**:
   - VCC: 连接到ESP8266的3.3V
   - GND: 连接到ESP8266的GND
   - DATA: 连接到ESP8266的D4(GPIO2)

2. **OLED显示屏连接**:
   - VCC: 连接到ESP8266的3.3V
   - GND: 连接到ESP8266的GND
   - SCL: 连接到ESP8266的D1(GPIO5)
   - SDA: 连接到ESP8266的D2(GPIO4)

## 软件准备

### 方法一: 使用ESPHome (推荐)

1. 安装Home Assistant:
   - 在树莓派或服务器上安装Home Assistant OS
   - 或使用Home Assistant Docker容器

2. 安装ESPHome:
   - 在Home Assistant中，进入`设置` > `加载项` > `加载项商店`
   - 安装ESPHome加载项

3. 配置ESP8266:
   - 在ESPHome仪表板中点击"+"创建新设备
   - 上传`esphome_config.yaml`文件（修改WiFi设置）
   - 通过USB将固件刷入ESP8266

### 方法二: 使用Arduino IDE

1. 安装Arduino IDE
2. 添加ESP8266支持:
   - 在首选项>附加开发板管理器网址中添加:
     `http://arduino.esp8266.com/stable/package_esp8266com_index.json`
   - 在开发板管理器中安装ESP8266平台

3. 安装必要的库:
   - ESP8266WiFi
   - ESP8266HTTPClient
   - ArduinoJson
   - DHT sensor library
   - Adafruit SSD1306
   - Adafruit GFX Library

4. 修改代码中的配置:
   - 打开`dht11_esp8266.ino`
   - 修改WiFi设置和Home Assistant设置
   - 上传代码到ESP8266

## 连接到Home Assistant

### 获取Home Assistant API访问令牌

1. 登录Home Assistant
2. 进入`设置` > `用户` > 点击你的用户名
3. 滚动到页面底部的"长期访问令牌"
4. 点击"创建令牌"，输入名称如"ESP8266传感器"
5. 复制生成的令牌（只显示一次!）

### 使用ESPHome方式:

设备会自动被Home Assistant发现并添加。

### 使用Arduino方式:

1. 修改ESP8266代码中的设置:
   - 填入正确的Home Assistant IP地址和端口
   - 添加长期访问令牌

2. 将`configuration.yaml`内容添加到Home Assistant配置
3. 重启Home Assistant
4. 创建仪表板目录并添加`temperature.yaml`文件

## 故障排除

1. 检查ESP8266是否正常连接WiFi
2. 确认DHT11和OLED连接正确
3. 验证Home Assistant访问令牌是否有效
4. 检查Home Assistant API是否正常工作
5. 查看ESP8266串口输出以获取错误信息

## 项目文件

- `dht11_esp8266.ino`: Arduino代码版本
- `esphome_config.yaml`: ESPHome配置版本
- `configuration.yaml`: Home Assistant配置文件
- `dashboards/temperature.yaml`: Home Assistant仪表板配置
- `README.md`: 项目说明文件 