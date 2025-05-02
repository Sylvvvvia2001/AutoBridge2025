#!/usr/bin/env python3
"""
Home Assistant温湿度传感器模拟器

这个脚本模拟DHT11传感器读取温湿度数据，并使用Home Assistant API发送到Home Assistant。
这是一个命令行版本，易于在任何Python环境中运行，包括Cursor。
"""

import time
import json
import random
import requests
import logging
from datetime import datetime

# 配置日志
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# ============================ 配置 ============================
# Home Assistant配置
HA_HOST = "192.168.1.xxx"  # 修改为你的Home Assistant IP地址
HA_PORT = 8123             # Home Assistant默认端口
HA_TOKEN = "你的长期访问令牌"  # 从Home Assistant获取的长期访问令牌

# 传感器模拟配置
BASE_TEMPERATURE = 25.0    # 基准温度(°C)
BASE_HUMIDITY = 50.0       # 基准湿度(%)
VARIATION = 2.0            # 随机变化幅度
SEND_INTERVAL = 60         # 发送到HA的间隔（秒），设置较短方便测试
DEBUG_MODE = True          # 调试模式，设置为True时只打印不发送
# ==============================================================

class DHT11Simulator:
    """模拟DHT11传感器"""
    
    def __init__(self, base_temp=BASE_TEMPERATURE, base_humidity=BASE_HUMIDITY, variation=VARIATION):
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

class HomeAssistantAPI:
    """Home Assistant API封装"""
    
    def __init__(self, host, port, token, debug_mode=False):
        self.host = host
        self.port = port
        self.token = token
        self.debug_mode = debug_mode
        self.base_url = f"http://{host}:{port}/api"
        self.headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
    
    def send_state(self, entity_id, state, attributes=None):
        """发送状态到Home Assistant"""
        url = f"{self.base_url}/states/{entity_id}"
        
        # 构建数据
        data = {"state": state}
        if attributes:
            data["attributes"] = attributes
        
        # 如果是调试模式，只打印不发送
        if self.debug_mode:
            logger.info(f"调试模式: 将发送到 {url}")
            logger.info(f"数据: {json.dumps(data, ensure_ascii=False)}")
            return {"success": True, "response": "调试模式，未实际发送"}
        
        # 发送请求
        try:
            response = requests.post(url, headers=self.headers, json=data)
            response.raise_for_status()
            return {"success": True, "response": response.json()}
        except requests.exceptions.RequestException as e:
            logger.error(f"API请求失败: {e}")
            return {"success": False, "error": str(e)}

def main():
    """主函数"""
    # 初始化传感器和API
    dht11 = DHT11Simulator()
    
    # 检查配置
    if HA_HOST == "192.168.1.xxx":
        logger.warning("请修改脚本中的HA_HOST为你的Home Assistant的IP地址")
        logger.warning("当前使用调试模式，不会发送实际请求")
        debug_mode = True
    else:
        debug_mode = DEBUG_MODE
    
    ha_api = HomeAssistantAPI(HA_HOST, HA_PORT, HA_TOKEN, debug_mode)
    
    try:
        logger.info("开始温湿度监测模拟...")
        
        # 间隔发送数据循环
        run_count = 0
        while True:
            run_count += 1
            logger.info(f"===== 第{run_count}次运行 =====")
            
            # 读取传感器数据
            temperature = dht11.read_temperature()
            humidity = dht11.read_humidity()
            
            logger.info(f"读取温度: {temperature}°C")
            logger.info(f"读取湿度: {humidity}%")
            
            # 发送温度数据
            temp_result = ha_api.send_state(
                "sensor.esp8266_temperature", 
                temperature,
                {
                    "unit_of_measurement": "°C",
                    "device_class": "temperature",
                    "friendly_name": "ESP8266温度",
                    "last_updated": datetime.now().isoformat()
                }
            )
            
            if temp_result["success"]:
                logger.info("温度数据发送成功")
            else:
                logger.error(f"温度数据发送失败: {temp_result.get('error')}")
            
            # 发送湿度数据
            humid_result = ha_api.send_state(
                "sensor.esp8266_humidity", 
                humidity,
                {
                    "unit_of_measurement": "%",
                    "device_class": "humidity",
                    "friendly_name": "ESP8266湿度",
                    "last_updated": datetime.now().isoformat()
                }
            )
            
            if humid_result["success"]:
                logger.info("湿度数据发送成功")
            else:
                logger.error(f"湿度数据发送失败: {humid_result.get('error')}")
            
            logger.info(f"等待{SEND_INTERVAL}秒后进行下一次发送...")
            
            # 在调试模式下，我们限制运行次数
            if debug_mode and run_count >= 5:
                logger.info("调试模式已完成5次循环，退出程序")
                break
            
            # 等待下一次发送
            time.sleep(SEND_INTERVAL)
    
    except KeyboardInterrupt:
        logger.info("程序被用户中断")
    
    logger.info("程序结束")

if __name__ == "__main__":
    main() 