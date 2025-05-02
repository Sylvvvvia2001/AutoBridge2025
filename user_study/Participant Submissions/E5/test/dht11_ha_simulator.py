#!/usr/bin/env python3
"""
ESP8266 + DHT11 + OLED 温湿度监测系统的Python模拟器
可以在电脑上运行，模拟传感器数据并发送到Home Assistant
"""

import time
import json
import random
import requests
import logging
from datetime import datetime
import tkinter as tk
from tkinter import font as tkfont
from PIL import Image, ImageTk, ImageDraw, ImageFont
import threading

# 配置日志
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# ============================ 配置 ============================
# Home Assistant配置
HA_HOST = "192.168.17.102"  # 修改为你的Home Assistant IP地址
HA_PORT = 8123             # Home Assistant默认端口
HA_TOKEN = "你的长期访问令牌"  # 从Home Assistant获取的长期访问令牌

# 传感器模拟配置
UPDATE_INTERVAL = 5  # 数据更新间隔（秒）
SEND_INTERVAL = 60   # 发送到HA的间隔（秒）

# OLED模拟配置
SCREEN_WIDTH = 128
SCREEN_HEIGHT = 64
# ==============================================================

class DHT11Simulator:
    """模拟DHT11传感器"""
    
    def __init__(self, base_temp=25.0, base_humidity=50.0, variation=2.0):
        self.base_temp = base_temp
        self.base_humidity = base_humidity
        self.variation = variation
        
    def read_temperature(self):
        """模拟读取温度"""
        temp = self.base_temp + random.uniform(-self.variation, self.variation)
        return round(temp, 1)
    
    def read_humidity(self):
        """模拟读取湿度"""
        humidity = self.base_humidity + random.uniform(-self.variation, self.variation)
        # 确保湿度在0-100范围内
        humidity = max(0, min(100, humidity))
        return round(humidity, 1)

class OLEDSimulator:
    """模拟OLED显示屏"""
    
    def __init__(self, master, width=SCREEN_WIDTH, height=SCREEN_HEIGHT):
        self.width = width
        self.height = height
        
        # 创建GUI
        self.frame = tk.Frame(master, bg="black", width=width*2, height=height*2)
        self.frame.pack(padx=20, pady=20)
        
        # 创建Canvas
        self.canvas = tk.Canvas(self.frame, bg="black", width=width*2, height=height*2, highlightthickness=0)
        self.canvas.pack()
        
        # 创建显示图像
        self.image = Image.new('1', (width, height), 0)
        self.draw = ImageDraw.Draw(self.image)
        
        # 尝试加载字体
        try:
            self.font = ImageFont.truetype("arial.ttf", 10)
        except IOError:
            # 如果无法加载特定字体，使用默认字体
            self.font = ImageFont.load_default()
        
        # 放大后的图像，用于显示
        self.display_image = None

    def clear(self):
        """清空显示"""
        self.draw.rectangle((0, 0, self.width, self.height), fill=0)
    
    def text(self, x, y, text, fill=1):
        """显示文本"""
        self.draw.text((x, y), text, font=self.font, fill=fill)
        
    def display(self):
        """更新显示"""
        # 放大图像以便更清晰地显示
        enlarged = self.image.resize((self.width*2, self.height*2))
        self.display_image = ImageTk.PhotoImage(enlarged)
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.display_image)

class ESP8266Simulator:
    """模拟ESP8266设备"""
    
    def __init__(self, master):
        self.master = master
        master.title("ESP8266 + DHT11 + OLED 模拟器")
        master.configure(bg="#222222")
        
        # 初始化组件
        self.dht11 = DHT11Simulator()
        self.display = OLEDSimulator(master)
        
        # 状态变量
        self.temperature = 0.0
        self.humidity = 0.0
        self.wifi_rssi = -65  # 模拟WiFi信号强度
        self.last_send_time = 0
        self.running = True
        
        # 控制面板
        self.control_frame = tk.Frame(master, bg="#333333")
        self.control_frame.pack(padx=20, pady=10, fill=tk.X)
        
        # 温度调节
        tk.Label(self.control_frame, text="基准温度:", bg="#333333", fg="white").grid(row=0, column=0, padx=5, pady=5)
        self.temp_slider = tk.Scale(self.control_frame, from_=0, to=40, orient=tk.HORIZONTAL, 
                                   bg="#333333", fg="white", highlightthickness=0)
        self.temp_slider.set(self.dht11.base_temp)
        self.temp_slider.grid(row=0, column=1, padx=5, pady=5)
        self.temp_slider.config(command=self.update_temp)
        
        # 湿度调节
        tk.Label(self.control_frame, text="基准湿度:", bg="#333333", fg="white").grid(row=1, column=0, padx=5, pady=5)
        self.humid_slider = tk.Scale(self.control_frame, from_=0, to=100, orient=tk.HORIZONTAL, 
                                    bg="#333333", fg="white", highlightthickness=0)
        self.humid_slider.set(self.dht11.base_humidity)
        self.humid_slider.grid(row=1, column=1, padx=5, pady=5)
        self.humid_slider.config(command=self.update_humidity)
        
        # 发送数据按钮
        self.send_button = tk.Button(self.control_frame, text="立即发送数据到HA", 
                                     command=self.send_data_now, bg="#555555", fg="white")
        self.send_button.grid(row=2, column=0, columnspan=2, padx=5, pady=10)
        
        # 状态标签
        self.status_label = tk.Label(self.control_frame, text="状态: 正在初始化...", 
                                     bg="#333333", fg="#AAFFAA", justify=tk.LEFT)
        self.status_label.grid(row=3, column=0, columnspan=2, padx=5, pady=5, sticky=tk.W)
        
        # 启动传感器读取线程
        self.sensor_thread = threading.Thread(target=self.sensor_loop)
        self.sensor_thread.daemon = True
        self.sensor_thread.start()
        
        # 开始显示更新
        self.update_display()
    
    def update_temp(self, value):
        """更新基准温度"""
        self.dht11.base_temp = float(value)
    
    def update_humidity(self, value):
        """更新基准湿度"""
        self.dht11.base_humidity = float(value)
    
    def update_display(self):
        """更新OLED显示"""
        self.display.clear()
        
        # 显示温度
        self.display.text(0, 0, f"温度: {self.temperature:.1f} °C")
        
        # 显示湿度
        self.display.text(0, 16, f"湿度: {self.humidity:.1f} %")
        
        # 显示WiFi信号强度
        self.display.text(0, 32, f"WiFi: {self.wifi_rssi} dBm")
        
        # 显示上次发送时间
        time_since_last = time.time() - self.last_send_time
        if self.last_send_time > 0:
            self.display.text(0, 48, f"上次发送: {int(time_since_last)}秒前")
        else:
            self.display.text(0, 48, "等待首次发送...")
        
        # 更新显示
        self.display.display()
        
        # 每秒更新一次显示
        if self.running:
            self.master.after(1000, self.update_display)
    
    def sensor_loop(self):
        """传感器读取和数据发送循环"""
        last_update_time = 0
        
        while self.running:
            current_time = time.time()
            
            # 更新传感器数据
            if current_time - last_update_time >= UPDATE_INTERVAL:
                self.temperature = self.dht11.read_temperature()
                self.humidity = self.dht11.read_humidity()
                # 随机波动WiFi信号
                self.wifi_rssi = -65 + random.randint(-10, 10)
                
                last_update_time = current_time
                self.status_label.config(text=f"状态: 更新传感器数据 - {datetime.now().strftime('%H:%M:%S')}")
            
            # 发送到Home Assistant
            if current_time - self.last_send_time >= SEND_INTERVAL:
                try:
                    self.send_data_to_ha()
                    self.last_send_time = current_time
                    self.status_label.config(text=f"状态: 数据已发送 - {datetime.now().strftime('%H:%M:%S')}")
                except Exception as e:
                    logger.error(f"发送数据失败: {e}")
                    self.status_label.config(text=f"状态: 发送失败 - {e}")
            
            time.sleep(1)
    
    def send_data_now(self):
        """立即发送数据按钮回调"""
        try:
            self.send_data_to_ha()
            self.last_send_time = time.time()
            self.status_label.config(text=f"状态: 数据已手动发送 - {datetime.now().strftime('%H:%M:%S')}")
        except Exception as e:
            logger.error(f"手动发送数据失败: {e}")
            self.status_label.config(text=f"状态: 手动发送失败 - {e}")
    
    def send_data_to_ha(self):
        """发送数据到Home Assistant"""
        # 在生产环境中取消以下注释，并填入正确的信息
        # self._send_temperature()
        # self._send_humidity()
        
        # 仅用于模拟
        logger.info(f"模拟发送数据到Home Assistant - 温度: {self.temperature}°C, 湿度: {self.humidity}%")
        
        # 如果HA_HOST是默认值，则显示未配置消息
        if HA_HOST == "192.168.1.xxx":
            logger.warning("Home Assistant未配置，仅模拟发送")
    
    def _send_temperature(self):
        """发送温度数据到Home Assistant"""
        url = f"http://{HA_HOST}:{HA_PORT}/api/states/sensor.esp8266_temperature"
        headers = {
            "Authorization": f"Bearer {HA_TOKEN}",
            "Content-Type": "application/json"
        }
        data = {
            "state": self.temperature,
            "attributes": {
                "unit_of_measurement": "°C",
                "device_class": "temperature",
                "friendly_name": "ESP8266温度"
            }
        }
        
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        logger.info(f"温度数据发送成功: {response.status_code}")
    
    def _send_humidity(self):
        """发送湿度数据到Home Assistant"""
        url = f"http://{HA_HOST}:{HA_PORT}/api/states/sensor.esp8266_humidity"
        headers = {
            "Authorization": f"Bearer {HA_TOKEN}",
            "Content-Type": "application/json"
        }
        data = {
            "state": self.humidity,
            "attributes": {
                "unit_of_measurement": "%",
                "device_class": "humidity",
                "friendly_name": "ESP8266湿度"
            }
        }
        
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        logger.info(f"湿度数据发送成功: {response.status_code}")

def main():
    """主函数"""
    # 创建GUI
    root = tk.Tk()
    app = ESP8266Simulator(root)
    
    # 设置窗口关闭处理
    def on_closing():
        app.running = False
        root.destroy()
    
    root.protocol("WM_DELETE_WINDOW", on_closing)
    
    # 启动主循环
    root.mainloop()

if __name__ == "__main__":
    main() 