#!/usr/bin/env python3
"""
使用官方Home Assistant API库的温湿度模拟发送器

这个脚本使用官方Home Assistant Python API库发送模拟传感器数据。
这是更现代和推荐的使用Python与Home Assistant交互的方式。
"""

import asyncio
import logging
import random
import time
from datetime import datetime

# 需要安装的库
# pip install homeassistant-api

from homeassistant_api import Client

# 配置日志
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# ============================ 配置 ============================
# Home Assistant配置
HA_URL = "http://192.168.1.xxx:8123"  # 修改为你的Home Assistant URL
HA_TOKEN = "你的长期访问令牌"         # 从Home Assistant获取的长期访问令牌

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

async def main():
    """主函数"""
    # 初始化传感器
    dht11 = DHT11Simulator()
    
    # 检查配置
    if "192.168.1.xxx" in HA_URL:
        logger.warning("请修改脚本中的HA_URL为你的Home Assistant的URL")
        logger.warning("当前使用调试模式，不会发送实际请求")
        debug_mode = True
    else:
        debug_mode = DEBUG_MODE
    
    if not debug_mode:
        try:
            # 连接到Home Assistant
            logger.info(f"连接到Home Assistant: {HA_URL}")
            client = Client(HA_URL, HA_TOKEN)
            logger.info("连接成功!")
        except Exception as e:
            logger.error(f"连接到Home Assistant失败: {e}")
            return
    
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
            
            timestamp = datetime.now().isoformat()
            logger.info(f"读取温度: {temperature}°C")
            logger.info(f"读取湿度: {humidity}%")
            
            # 发送数据到Home Assistant
            if debug_mode:
                logger.info("调试模式: 模拟发送到Home Assistant")
                logger.info(f"温度实体: sensor.esp8266_temperature, 值: {temperature}°C")
                logger.info(f"湿度实体: sensor.esp8266_humidity, 值: {humidity}%")
            else:
                try:
                    # 发送温度数据
                    await client.set_state(
                        entity_id="sensor.esp8266_temperature",
                        state=temperature,
                        attributes={
                            "unit_of_measurement": "°C",
                            "device_class": "temperature",
                            "friendly_name": "ESP8266温度",
                            "last_updated": timestamp
                        }
                    )
                    logger.info("温度数据发送成功")
                    
                    # 发送湿度数据
                    await client.set_state(
                        entity_id="sensor.esp8266_humidity",
                        state=humidity,
                        attributes={
                            "unit_of_measurement": "%",
                            "device_class": "humidity",
                            "friendly_name": "ESP8266湿度",
                            "last_updated": timestamp
                        }
                    )
                    logger.info("湿度数据发送成功")
                
                except Exception as e:
                    logger.error(f"发送数据到Home Assistant失败: {e}")
            
            logger.info(f"等待{SEND_INTERVAL}秒后进行下一次发送...")
            
            # 在调试模式下，我们限制运行次数
            if debug_mode and run_count >= 5:
                logger.info("调试模式已完成5次循环，退出程序")
                break
            
            # 等待下一次发送
            await asyncio.sleep(SEND_INTERVAL)
    
    except KeyboardInterrupt:
        logger.info("程序被用户中断")
    except Exception as e:
        logger.error(f"程序发生错误: {e}")
    finally:
        if not debug_mode:
            # 关闭客户端连接
            try:
                client.close()
                logger.info("已关闭与Home Assistant的连接")
            except:
                pass
        
        logger.info("程序结束")

if __name__ == "__main__":
    # 运行异步主函数
    asyncio.run(main()) 